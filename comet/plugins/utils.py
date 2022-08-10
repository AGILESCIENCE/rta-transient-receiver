import re

class Utils:

    @staticmethod
    def triggerId_from_graceID(graceID):
        last = str(ord(graceID[-1]) - 96)
        result = re.sub("[^0-9]", "", graceID) + last.zfill(2)
        return result
    
    @staticmethod
    def graceID_from_triggerId(mission, triggerID):

        
        IDENTITY = triggerID
        MISSION = mission

        GW_ALERT_ID = 0

        if MISSION == 'LIGO_TEST' or MISSION == 'LIGO':

            THRESHOLD = 4.0

            if MISSION == 'LIGO_TEST':
                CHAR = 'MS'
            elif MISSION == 'LIGO':
                CHAR = 'S'

            if len(IDENTITY[6:]) == 2:
                GW_ALERT_ID = "%s%s%s" % (CHAR, IDENTITY[:6], chr(int(IDENTITY[6:8])+96))
                print("GW_ALERT_ID = ", GW_ALERT_ID)
            if len(IDENTITY[6:]) == 4:
                GW_ALERT_ID = "%s%s%s%s" % (CHAR, IDENTITY[:6], chr(int(IDENTITY[6:8])+96), chr(int(IDENTITY[8:10])+96))
                print ("GW_ALERT_ID = ", GW_ALERT_ID)
            if len(IDENTITY[6:]) == 6:
                GW_ALERT_ID = "%s%s%s%s%s" % (CHAR, IDENTITY[:6], chr(int(IDENTITY[6:8])+96), chr(int(IDENTITY[8:10])+96), chr(int(IDENTITY[10:12])+96))
                print ("GW_ALERT_ID = ", GW_ALERT_ID)
            if len(IDENTITY[6:]) == 8:
                GW_ALERT_ID = "%s%s%s%s%s" % (CHAR, IDENTITY[:6], chr(int(IDENTITY[6:8])+96), chr(int(IDENTITY[8:10])+96), chr(int(IDENTITY[10,12])+96), chr(int(IDENTITY[12,14])+96))
                print("GW_ALERT_ID = ", GW_ALERT_ID)
        else:
            GW_ALERT_ID = triggerID
        
        return GW_ALERT_ID
