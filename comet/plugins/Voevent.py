import os
import re
import json
import math
import requests
import numpy as np
import comet.log as log
import voeventparse as vp
from tokenize import group
from datetime import datetime
from datetime import datetime
from astropy.time import Time
from astropy import units as u
import lxml.etree as ElementTree
from comet.utility import voevent
from astropy.coordinates import SkyCoord
from comet.utility.xml import xml_document
from ligo.skymap.io.fits import read_sky_map
from ligo.skymap.postprocess.contour import contour as ligo_contour
from comet.plugins.test.test_voevents import DUMMY_VOEVENT_GCN, DUMMY_VOEVENT_INTEGRAL, DUMMY_VOEVENT_CHIME, \
    DUMMY_VOEVENT_LIGO, DUMMY_VOEVENT_LIGO_INITIAL, DUMMY_VOEVENT_LIGO_PRELIMINARY, DUMMY_VOEVENT_GCN_FERMI, \
    DUMMY_VOEVENT_GCN_MAXI

class DummyEvent(object):
    """
    Class containing standard voevent from different networks
    """
    gcn = xml_document(DUMMY_VOEVENT_GCN)
    chime = xml_document(DUMMY_VOEVENT_CHIME)
    integral = xml_document(DUMMY_VOEVENT_INTEGRAL)
    fermi = xml_document(DUMMY_VOEVENT_GCN_FERMI) 
    ligo = xml_document(DUMMY_VOEVENT_LIGO)
    ligo2 = xml_document(DUMMY_VOEVENT_LIGO_PRELIMINARY)
    ligo_initial = xml_document(DUMMY_VOEVENT_LIGO_INITIAL)
    maxi = xml_document(DUMMY_VOEVENT_GCN_MAXI)


class Voevent(object):

    def __init__(self, voe) -> None:

        self.voevent = voe

        self.GCN = False
        self.CHIME = False
        self.INTEGRAL = False
        self.LIGO = False
        self.AGILE = False
        self.mark_notice()
        self.ste = self.is_ste()
        self.instrumentId = self.get_instrumentid_from_packet_type()
        self.seqNum = -1
        self.triggerId = self.get_triggerID()
        self.packetType = self.get_packet_tipe()
        self.isoTime = self.get_time_from_voe()
        self.networkId = self.get_networkID()
        self.l, self.b = self.get_l_b()
        self.error = self.get_position_error()
        self.notice = vp.prettystr(self.voevent)
        self.configuration = self.get_configuration()
        self.tstart = 0
        self.tstop = 0
        self.last = 1
        self.url = self.get_url()
        self.contour = self.get_contour()
        self.attributes = self.get_ligo_attributes()
        
    

    def mark_notice(self):
        """
        The only common parameter is ivorn, we discriminate among notices using this parameter
        """
        print(f"ivorn is {self.voevent.attrib['ivorn']}")
        
        if "gcn" in self.voevent.attrib['ivorn']:
            self.GCN = True
            return
        if "gwnet" in self.voevent.attrib['ivorn']:
            self.LIGO = True
            return
        if "chimenet" in self.voevent.attrib['ivorn']:
            self.CHIME = True
            return
        if "INTEGRAL" in self.voevent.attrib['ivorn']:
            self.INTEGRAL = True
            return
        if "AGILE" in self.voevent.attrib['ivorn']:
            self.AGILE = True
            return
        
        
        raise Exception(f"Notice not supported  ivorn is {self.voevent.attrib['ivorn']}")

    def is_ste(self):
        if self.AGILE or self.INTEGRAL:
            return 1
        else:
            return 0
    
    
    def get_instrumentid_from_packet_type(self):
        """
        Packet type description available at https://gcn.gsfc.nasa.gov/sock_pkt_def_doc.html
        Eg:
            INTEGRAL [53,54,55]
            SWIFT [46,47, 60 to 99, 103, 133, 140, 141]
            FERMI_GBM [110 to 119, 144]
            FERMI_LAT [120,121,122,123,124,125,127,128]
            MAXI [134,135,136]
            LIGO [150, 151, 152]
            ICECUBE [173, 174]

        """
        if self.GCN or self.LIGO:
            packet_type = int(self.voevent.What.Param[0].attrib["value"])

            if packet_type in [53,54,55]: # INTEGRAL FROM GCN
                return 23
            elif packet_type == 97: #SWIFT 
                return 3
            elif packet_type == 111:  #FERMI_GBM 
                return 1
            elif packet_type in [125,128]: #FERMI_LAT 
                return 2
            elif packet_type == 105: #AGILE_MCAL FROM GCN
                return 5
            elif packet_type in [150, 151, 152, 163]: #LIGO and LIGO_TEST TBD
                if  "test" in self.voevent.attrib['role']:
                    return 19
                if  "observation" in self.voevent.attrib['role']:
                    return 7
            elif packet_type == 158: #ICECUBE_HESE
                return 8
            elif packet_type == 169: #ICECUBE_EHE
                return 10
            elif packet_type == 173: #ICECUBE_ASTROTRACK_GOLD
                return 21
            elif packet_type == 174: #ICECUBE_ASTROTRACK_GOLD
                return 22
            elif packet_type == 59: #KONUS
                return 25
            elif packet_type == 134: #MAXI_UNKNOWN
                return 26
            elif packet_type == 135: #MAXI_KNOWN
                return 27
            #elif packet_type == 175: #SK_SN NOT SUPPORTED
                #return 28
            else:
                log.info(f"Voevent with packet type {packet_type} not supported")
                raise Exception(f"Voevent with packet type {packet_type} not supported")

        if self.CHIME:
            return 24 
        if self.INTEGRAL: # INTEGRAL subthrsld from James Rodi
            return 23
        if self.AGILE:  #AGILE MCAL subtrheshold from AGILE's TEAM
            return 5
        log.info("Voevent not supported")
        raise Exception("Voevent not supported")

    def get_seqnum(self):
        return self.seqNum
    
    def set_seqnum(self, seqnum):
        self.seqNum = seqnum

    def get_configuration(self):
        if self.LIGO:
            top_params = vp.get_toplevel_params(self.voevent)
            return top_params["Instruments"]["value"]
        else:
            return "None"
    
    def get_triggerID(self):
        """
        For LIGO trigger id is only numbers such that:
        220530p -> 22053016 (p is 16th)
        """

        if self.GCN or self.INTEGRAL or self.AGILE:
            top_params = vp.get_toplevel_params(self.voevent)
            return top_params["TrigID"]["value"]

        if self.CHIME:
            grouped_params = vp.get_grouped_params(self.voevent)
            return grouped_params["event parameters"]["event_no"]["value"]
            
        if self.LIGO:
            top_params = vp.get_toplevel_params(self.voevent)
            graceID = top_params["GraceID"]["value"]
            last = str(ord(graceID[-1]) - 96)
            result = re.sub("[^0-9]", "", graceID) + last.zfill(2)
            return result
        else:
            return 0

    def get_packet_tipe(self):

        if self.GCN or self.LIGO:
            top_params = vp.get_toplevel_params(self.voevent)
            return top_params["Packet_Type"]["value"]
        else:
            return 0

    def get_time_from_voe(self):

        iso_time = self.voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Time.TimeInstant.ISOTime.text

        t = Time(iso_time, format="fits", scale="utc")
        return np.round(t.unix - 1072915200)

    def get_networkID(self):
        """
        Possible networks
        - GCN network
        - Chimenet
        - INTEGRAL subthreshold notices from James Rodi
        """
        if self.GCN or self.LIGO:
            return 1
        if self.CHIME:
            return 4
        if self.INTEGRAL:
            return 6
        if self.AGILE:
            return 7

    def get_l_b(self):

        if self.LIGO:
            return 0,0

        ra = float(self.voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C1.text)
        dec = float(self.voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Value2.C2.text)

        c = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')

        return c.galactic.l.degree, c.galactic.b.degree

    def get_position_error(self):
        if self.LIGO:
            return 0
        return float(self.voevent.WhereWhen.ObsDataLocation.ObservationLocation.AstroCoords.Position2D.Error2Radius.text)

    def get_ligo_attributes(self):
        """
        tipical LIGO attributes extracted:
        {"bbh": 0, "bns": 0.9999947011562164, "far": 0.00000000000009110699364861295, "nsbh": 0, "has_ns": 1, "grace_id": "MS210208t",
        "mass_gap": 0, "has_remnant": 1, "terrestrial": 0.000005298843783562432}
        """
        if self.LIGO:
            top_params = vp.get_toplevel_params(self.voevent)
            grouped_params = vp.get_grouped_params(self.voevent)
            attributes = {}
            attributes["bbh"] = grouped_params["Classification"]["BBH"]["value"]
            attributes["bns"] = grouped_params["Classification"]["BNS"]["value"]
            attributes["far"] = top_params["FAR"]["value"]
            attributes["nsbh"] = grouped_params["Classification"]["NSBH"]["value"]
            attributes["has_ns"] = grouped_params["Properties"]["HasNS"]["value"]
            attributes["grace_id"] = top_params["GraceID"]["value"]
            try:
                attributes["mass_gap"] = grouped_params["Classification"]["MassGap"]["value"]
            except:
                attributes["mass_gap"] = 0
            attributes["has_remnant"] = grouped_params["Properties"]["HasRemnant"]["value"]
            attributes["terrestrial"] = grouped_params["Classification"]["Terrestrial"]["value"]

            return str(json.dumps(attributes))
        
        return {}

    def get_contour(self):

        if self.LIGO:
            """
            For LIGO instrument we call contour function from ligo-contour tool
            """
            url = self.url
            now = datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
            target_path = f'/tmp/skymap_{now}.tar.gz'

            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(target_path, 'wb') as f:
                    f.write(response.raw.read())

            #Implementing the code from ligo-countour tool, the level [90] is hardcoded

            m, meta = read_sky_map(target_path, nest=True)
            i = np.flipud(np.argsort(m))
            cumsum = np.cumsum(m[i])
            cls = np.empty_like(m)
            cls[i] = cumsum * 100
            

            cont = list(ligo_contour(cls, [90.0], nest=True, degrees=True, simplify=False))
            
            #Conversion to galactic: it computes the position without loops to be more efficient, it uses approx 3 GB RAM
            ra = []
            dec = []
            for level in cont:
                for poligon in level:
                    for coord in poligon:
                        ra.append(coord[0])
                        dec.append(coord[1])
            
            c = SkyCoord(ra=ra*u.degree, dec=dec*u.degree)
            contour = ""
            for coords in c.galactic.to_string():
                contour = contour + f"{coords}\n"

            os.remove(target_path)

            return contour

        
        if self.GCN:
            """
            copy-paste from https://github.com/ASTRO-EDU/AlertReceiver_GCNnetwork/blob/117ce436b7003af14843cd6fd97ed0c0e1d90eb5/gcn/alert.c#L161
            """
            if self.l == 0 and self.b == 0:
                return 0
            l = 0
            b = 0
            r = self.error
            delta = 0
            if (r < 0.0000001):
                r = 0.1
            steps = int(10. + 10. * r)

            contour = ""

            for i in range(steps):
                l = self.l - r * math.cos(delta)
                b = self.b + r * math.sin(delta)
                if (l < 0):
                    l = 0
                elif(l >= 360):
                    l = 360
                elif (l == 0):
                    l = 0
                if (b < -90):
                    b = -90
                elif (b > 90):
                    b = 90
                elif (b == 0):
                    b = 0
                
                delta = delta - 2 * math.pi / steps

                contour = contour + f"{l} {b}\n"
            return contour

    def get_url(self):

        if self.LIGO:
            grouped_params = vp.get_grouped_params(self.voevent)
            return  grouped_params["GW_SKYMAP"]["skymap_fits"]["value"]
        
        return "none"

    def __str__(self):
        return f"Voevent\nIntrumentID: {self.instrumentId}, seqNum {self.seqNum}, triggerid: {self.triggerId}, packetType: {self.packetType},time: {self.isoTime}, l: {self.l}, b: {self.b}, contour: {self.contour}, url: {self.url}"


if __name__ == "__main__":
    """
    Main used to quick test. It Should not be used as unit test
    """
    
    dummyevents = DummyEvent()

    voe_chime = vp.loads(dummyevents.chime.raw_bytes)
    voe_gcn = vp.loads(dummyevents.gcn.raw_bytes)
    voe_integral = vp.loads(dummyevents.integral.raw_bytes)
    voe_fermi = vp.loads(dummyevents.fermi.raw_bytes)
    voe_ligo = vp.loads(dummyevents.ligo.raw_bytes)
    voe_ligo_2 = vp.loads(dummyevents.ligo2.raw_bytes)
    voe_ligo_init = vp.loads(dummyevents.ligo_initial.raw_bytes)
    voe_maxi = vp.loads(dummyevents.maxi.raw_bytes)

    v_chime = Voevent(voe_chime)
    v_gcn = Voevent(voe_gcn)
    v_integral = Voevent(voe_integral)
    v_ligo = Voevent(voe_ligo)
    v_ligo2 = Voevent(voe_ligo_2)
    v_fermi = Voevent(voe_fermi)
    v_ligo_init = Voevent(voe_ligo_init)
    v_maxi = Voevent(voe_maxi)

    print(v_chime)
    print(v_gcn)
    print(v_integral)
    print(v_fermi)
    print(v_ligo)
    print(v_ligo2)
    print(v_ligo_init)
    print(v_maxi)

