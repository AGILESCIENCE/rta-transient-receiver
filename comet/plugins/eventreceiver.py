import os
import io
import json
import yaml
import pickle
import xmltodict
import numpy as np
import mysql.connector
import voeventparse as vp
from datetime import datetime
from astropy.time import Time
from astropy import units as u
from pymongo import MongoClient
import lxml.etree as ElementTree
from comet.icomet import IHandler
from twisted.plugin import IPlugin
from zope.interface import implementer
from astropy.coordinates import SkyCoord

from comet.plugins.Voevent import Voevent
from comet.plugins.mail import Mail
from comet.plugins.utils import Utils

# Server parameters
db_config = {'user': 'afiss', 'password': '', 'host': '127.0.0.1', 'port': 60306, 'database': 'afiss_rta_pipe_test_3'}

# Event handlers must implement IPlugin and IHandler.
@implementer(IPlugin, IHandler)
class EventReceiver(object):
    
    name = "receive-event"
    print("receive event attivo")
    
    def add_notice_mysql(self, voevent):
        
        try:

            cnx = mysql.connector.connect(user=db_config['user'], password=os.environ["MYSQL_AFISS"],
                              host=db_config['host'], port=db_config['port'],
                              database=db_config['database'])

        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

        
        cursor = cnx.cursor()

        #check if the query is null the alert is not present -> it will be inserted into receivedsciencealert table

        query = f"SELECT receivedsciencealertid FROM receivedsciencealert WHERE instrumentid = {voevent.instrumentId} AND triggerid = {voevent.triggerId};"
        cursor.execute(query)

        check_rsa = cursor.fetchone()

        if check_rsa is None:
            #insert
            #####################

            query = f"INSERT INTO receivedsciencealert (instrumentid, networkid, time, triggerid, ste) VALUES ({voevent.instrumentId}, {voevent.networkId}, {voevent.isoTime}, {voevent.triggerId}, {voevent.ste});"
            #print(f"query1 {query}")
            cursor.execute(query)
            cnx.commit()

            receivedsciencealertid = cursor.lastrowid
        else:
            receivedsciencealertid = int(check_rsa[0])
            
        #seqnum handling
        #####################
        if voevent.seqNum == -1:
        
            query = f"SELECT seqnum FROM notice n join receivedsciencealert rsa ON (rsa.receivedsciencealertid = n.receivedsciencealertid) WHERE last = 1 AND rsa.instrumentid = {voevent.instrumentId} AND rsa.triggerid = {voevent.triggerId}"
            cursor.execute(query)
            result_seqnum = cursor.fetchone()

            try:
                voevent.seqNum = int(result_seqnum[0]) + 1 
            except:
                voevent.seqNum = 0

        #last handling
        ######################
        query = f"UPDATE notice SET last = 0 WHERE last = 1 AND receivedsciencealertid = {receivedsciencealertid};"
        cursor.execute(query)
        cnx.commit()


        #insert in notice table
        #######################

        noticetime = datetime.utcnow().isoformat(timespec="seconds")


        query = f"INSERT INTO notice (receivedsciencealertid, seqnum, l, b, error, contour, `last`, `type`, configuration, noticetime, notice, tstart, tstop, url, `attributes`, afisscheck) VALUES ({receivedsciencealertid}, {voevent.seqNum}, {voevent.l}, {voevent.b}, {voevent.error}, '{voevent.contour}', {voevent.last}, {voevent.packetType}, '{voevent.configuration}', '{noticetime}', '{voevent.notice}', {voevent.tstart}, {voevent.tstop}, '{voevent.url}', '{voevent.attributes}', 0);"
        cursor.execute(query)
        cnx.commit()


        #send alert email
        
        mail = Mail("alert.agile@inaf.it", os.environ["MAIL_PASS"])
        
        if voevent.packetType in ["150", "151", "152", "163", "158", "169", "173", "174"] or voevent.ste: #it will send an email for GW, Neutrino event or STE events

            

            to = ["antonio.addis@inaf.it", "nicolo.parmiggiani@inaf.it"]

            subject = f'Notice alert for {voevent.name}'

            body = f'The AFIS platform received a notice for the {voevent.name} event at {voevent.UTC} for triggerID {voevent.triggerId} {chr(10)} available at \
            http://afiss.iasfbo.inaf.it/afiss/full_results.html?instrument_name={voevent.name}&trigger_time_utc={voevent.UTC}&trigger_id={Utils.graceID_from_triggerId(voevent.name, voevent.triggerId)}&seqnum={voevent.seqNum}'

            mail.send_email(to, subject, body)
        
        #check if there are correlated instruments and send an email if so
        query = f"select ins.name,n.seqnum,n.noticetime,rsa.receivedsciencealertid, rsa.triggerid,rsa.ste,rsa.time as `trigger_time`,ste,notice,JSON_PRETTY(n.attributes) as `attributes` from notice n join receivedsciencealert rsa on ( rsa.receivedsciencealertid = n.receivedsciencealertid) join instrument ins on(ins.instrumentid = rsa.instrumentid) where  ins.name != '{voevent.name}' and rsa.instrumentid != 19 and rsa.time >= {voevent.isoTime - 10} and rsa.time <= {voevent.isoTime + 10} and n.seqnum = (select max(seqnum) from notice n2 join receivedsciencealert rsa2 on ( rsa2.receivedsciencealertid = n2.receivedsciencealertid)  where  rsa.triggerid = rsa2.triggerid ) order by n.noticetime"
        cursor.execute(query)
        results_row = cursor.fetchall()

        #print(f"resulsts row is {results_row}")

        if results_row:
            for row in results_row:
                rsaid = row[3]
                query = f"INSERT INTO correlations (rsaId1, rsaId2) VALUES({receivedsciencealertid}, {rsaid});"
                cursor.execute(query)
                cnx.commit()

            query = f"SELECT ins.name, max(n.seqnum),n.noticetime, n.receivedsciencealertid, rsa.triggerid,rsa.ste,rsa.time as `trigger_time` from notice n join correlations c on (n.receivedsciencealertid = c.rsaId2) join receivedsciencealert rsa on ( rsa.receivedsciencealertid = n.receivedsciencealertid) join instrument ins on (ins.instrumentid = rsa.instrumentid) where c.rsaId1 = {receivedsciencealertid} group by n.receivedsciencealertid"
            cursor.execute(query)

            results_row = cursor.fetchall()


            to = ["antonio.addis@inaf.it", "nicolo.parmiggiani@inaf.it"]

            subject = f'Correlations for {voevent.name}'

            body = f'The AFIS platform received a notice for the {voevent.name} at {voevent.UTC} for triggerID {voevent.triggerId} {chr(10)} available at \
            http://afiss.iasfbo.inaf.it/afiss/full_results.html?instrument_name={voevent.name}&trigger_time_utc={voevent.UTC}&trigger_id={Utils.graceID_from_triggerId(voevent.name, voevent.triggerId)}&seqnum={voevent.seqNum} {chr(10)} with the following correlated events: {chr(10)} {str(results_row)}'

            mail.send_email(to, subject, body)
        

    # When the handler is called, it is passed an instance of
    # comet.utility.xml.xml_document.
    def __call__(self, event):

        #db=self.client["AFISS"]
        #collection=db["Events"]

        v = vp.loads(event.raw_bytes)

        voevent = Voevent(v)

        self.add_notice_mysql(voevent)
        #doc = xmltodict.parse(vp.dumps(v))
        #print("Ivorn:", v.attrib['ivorn'])
        #print("Role:", v.attrib['role'])
        #print("AuthorIVORN:", v.Who.AuthorIVORN)
        #print("Short name:", v.Who.Author.shortName)
        #print("Contact:", v.Who.Author.contactEmail)

        return True

receive_event = EventReceiver()