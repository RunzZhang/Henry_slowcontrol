BASE_ADDRESS= 12288
# real address  = base+ comparative/2
# Initialization of Address, Value Matrix
# 40001 is actually address 0

# MODULE connection alarm: manual toggle on or off if user choose to trigger the connection alarm
MODULE_CONNECTION_ALARM = {"AD1": True, "AD2": True, "LS": True, "LL": False, "Beckhoff": True}
TT_AD1_ADDRESS = {"RTD9": 0, "RTD10":1, "RTD11": 2, "RTD12": 3, "RTD13": 4, "RTD14":5}

TT_AD2_ADDRESS = { }

HTRTD_ADDRESS = {"RTD5":(0,0,0),"RTD6":(0,0,1),"RTD7":(0,1,0),"RTD8":(0,1,1), # change according to RTD/HTR config
                 "RTD1":(1,0,0),"RTD2":(1,0,1),"RTD3":(1,1,0), "RTD4":(1,1,1)}
# first digit the number of Lakeshore, second digit the number of Heater, the 3rd digit the number of feedback RTD
LL_ADDRESS = {"LL":"10.111.19.113"}


PT_ADDRESS = {"PT001": 12796, "PT002": 12798, "PT003": 12800, "PT004": 12802, "PT1000": 12808,
              "PT1001": 12810, "PT1002": 12812, "PT0": 12824}

# PT_ADDRESS = {"PT001": 12796, "PT002": 12798, "PT003": 12800, "PT004": 12802, "PT1000": 12808,
#              "PT1001": 12810, "PT1002": 12812, "PT0": 12824}

LEFT_REAL_ADDRESS = {'FCV1001': 12792, 'FCV1002': 12794, "BGAAH01": 12804, "BGAAH02": 12806 , "MFC1008": 12816,"BGAP01": 12820, "BGAP02": 12818,
                     "PT003ST":12814,"TT0001":12988,"TT0002":12990,"TT0001ST":12992,"TT0002ST":12994, "SV0001_TIME": 16822}

TT_AD1_DIC = {"RTD9": 0, "RTD10":0, "RTD11": 0, "RTD12": 0, "RTD13": 0, "RTD14": 0}
TT_AD1_CALI =  {"RTD9": -1.24, "RTD10": -0.99, "RTD11": -0.74, "RTD12": -1.05, "RTD13": -1.40, "RTD14": -1.79} # calirations as of 5.27.26

TT_AD2_DIC = {}

HTRTD_DIC = {"RTD1":0,"RTD2":0,"RTD3":0,
                 "RTD4":0,"RTD5":0,"RTD6":0, "RTD7":0, "RTD8":0}
LL_DIC = {"LL":0}

PT_DIC = {"PT001": 0, "PT002": 0, "PT003": 0, "PT004": 0, "PT1000": 0,
              "PT1001": 0, "PT1002": 0, "PT0": 0}

LEFT_REAL_DIC = {'FCV1001': 0, 'FCV1002': 0, "BGAAH01": 0, "BGAAH02": 0, "MFC1008": 0,"BGAP01": 0, "BGAP02": 0,
                 "PT003ST":0,"TT0001":0,"TT0002":0,"TT0001ST":0,"TT0002ST":0, "SV0001_TIME": 0}

TT_AD1_LOWLIMIT =  {"RTD9": 0, "RTD10":0, "RTD11": 0, "RTD12": 0, "RTD13": 0, "RTD14": 0}

TT_AD1_HIGHLIMIT = {"RTD9": 30, "RTD10":30, "RTD11": 30, "RTD12": 30,  "RTD13": 30, "RTD14": 30}
HTRTD_HIGHLIMIT = {"RTD1":30,"RTD2":30,"RTD3":30,
                 "RTD4":30,"RTD5":30,"RTD6":30, "RTD7":30, "RTD8":30}
HTRTD_LOWLIMIT =  {"RTD1":30,"RTD2":30,"RTD3":30,
                 "RTD4":30,"RTD5":30,"RTD6":30, "RTD7":30, "RTD8":30}

LL_LOWLIMIT = {"LL":0}

LL_HIGHLIMIT = {"LL":100}

TT_AD2_LOWLIMIT = { }

TT_AD2_HIGHLIMIT = { }


PT_LOWLIMIT = {"PT001": 0, "PT002": 0, "PT003": 0, "PT004": 0, "PT1000": 0,
              "PT1001": 0, "PT1002": 0, "PT0": 0}
PT_HIGHLIMIT = {"PT001": 0, "PT002": 0, "PT003": 0, "PT004": 0, "PT1000": 0,
              "PT1001": 0, "PT1002": 0, "PT0": 0}

LEFT_REAL_HIGHLIMIT = {'FCV1001': 100, 'FCV1002': 100, "BGAAH01": 100, "BGAAH02": 100 , "MFC1008": 100,"BGAP01": 5, "BGAP02": 5,
                       "PT003ST":100,"TT0001":300,"TT0002":300,"TT0001ST":300,"TT0002ST":300,  "SV0001_TIME": 300}
LEFT_REAL_LOWLIMIT = {'FCV1001': 0, 'FCV1002': 0, "BGAAH01": 0, "BGAAH02": 0, "MFC1008": 0,"BGAP01": -5, "BGAP02": -5,
                      "PT003ST":-1,"TT0001":-1,"TT0002":-1,"TT0001ST":-1,"TT0002ST":-1, "SV0001_TIME": -1}

TT_AD1_ACTIVATED = {"RTD9": False, "RTD10":False, "RTD11": False, "RTD12": False, "RTD13": False, "RTD14": False}

TT_AD2_ACTIVATED = {}

HTRTD_ACTIVATED = {"RTD1":False,"RTD2":False,"RTD3":False,
                 "RTD4":False,"RTD5":False,"RTD6":False, "RTD7":False, "RTD8":False}

LL_ACTIVATED = {"LL":False}


PT_ACTIVATED = {"PT001": False, "PT002": False, "PT003": False, "PT004": False, "PT1000": False,
              "PT1001": False, "PT1002": False, "PT0": False}
LEFT_REAL_ACTIVATED = {'FCV1001': False, 'FCV1002': False, "BGAAH01": False, "BGAAH02": False, "MFC1008": False,"BGAP01": False, "BGAP02": False,
                       "PT003ST":False,"TT0001":False,"TT0002":False,"TT0001ST":False,"TT0002ST":False, "SV0001_TIME": False}
TT_AD1_ALARM = {"RTD9": False, "RTD10":False, "RTD11": False, "RTD12": False, "RTD13": False, "RTD14": False}

TT_AD2_ALARM = {}

HTRTD_ALARM = {"RTD1":False,"RTD2":False,"RTD3":False,
                 "RTD4":False,"RTD5":False,"RTD6":False, "RTD7":False, "RTD8":False}

LL_ALARM = {"LL":False}


PT_ALARM = {"PT001": False, "PT002": False, "PT003": False, "PT004": False, "PT1000": False,
              "PT1001": False, "PT1002": False, "PT0": False}
LEFT_REAL_ALARM = {'FCV1001': False, 'FCV1002': False, "BGAAH01": False, "BGAAH02": False, "MFC1008": False,"BGAP01": False, "BGAP02": False,
                   "PT003ST":False,"TT0001":False,"TT0002":False,"TT0001ST":False,"TT0002ST":False, "SV0001_TIME": False}
MAINALARM = False
MAINALARM_PARA = 0
MAINALARM_RATE = 60

MAN_SET = False
NTT_AD1 = len(TT_AD1_ADDRESS)
NTT_AD2 = len(TT_AD2_ADDRESS)
NLL =len(LL_ADDRESS)
NPT = len(PT_ADDRESS)

# FDC1004 capacitance channels. These come from fdc1004_logger.py's own
# 10-second averaging loop (UpdateFDC1004 writes into plc_data directly,
# not via PLC.ReadAll()/modbus), so there's no ADDRESS/ACTIVATED/ALARM
# mapping here like the modbus-backed sensor types above — just the
# current value dict the database thread reads from.
CAP_DIC = {"FDC1004_CH1": 0, "FDC1004_CH2": 0, "FDC1004_CH3": 0, "FDC1004_CH4": 0}
NREAL = len(LEFT_REAL_ADDRESS)
NHTRTD = len(HTRTD_ADDRESS)


PT_SETTING = [0.] * NPT
NPT_ATTRIBUTE = [0.] * NPT

SWITCH_ADDRESS = {"PUMP3305": 12688}
NSWITCH = len(SWITCH_ADDRESS)
SWITCH = {}
SWITCH_OUT = {"PUMP3305": 0}
SWITCH_MAN = {"PUMP3305": False}
SWITCH_INTLKD = {"PUMP3305": False}
SWITCH_ERR = {"PUMP3305": False}

DIN_ADDRESS = {"LS3338": (12778, 0), "LS3339": (12778, 1), "ES3347": (12778, 2), "PUMP3305_CON": (12778, 3),
               "PUMP3305_OL": (12778, 4),"PS2352":(12778, 5),"PS1361":(12778, 6),"PS8302":(12778, 7), "SV0001_MAN":(16792,3), "SV0001_TRIG":(16792,4), "SV0001_RESET":(16792,5) ,"PV1_LCK": (16792,6),"PV1_RESET":(16792,7)}
NDIN = len(DIN_ADDRESS)
DIN = {}
DIN_DIC = {"LS3338": False, "LS3339": False, "ES3347": False, "PUMP3305_CON": False, "PUMP3305_OL": False,"PS2352":False,"PS1361":False,"PS8302":False, "SV0001_MAN":False, "SV0001_TRIG":False, "SV0001_RESET":False,"PV1_LCK":False,"PV1_RESET":False}

DIN_LOWLIMIT = {"LS3338": False, "LS3339": False, "ES3347": False, "PUMP3305_CON": False, "PUMP3305_OL": False,"PS2352":False,"PS1361":False,"PS8302":False, "SV0001_MAN":False, "SV0001_TRIG":False, "SV0001_RESET":False,"PV1_LCK":False,"PV1_RESET":False}

DIN_HIGHLIMIT = {"LS3338": True, "LS3339": True, "ES3347": True, "PUMP3305_CON": True, "PUMP3305_OL": True,"PS2352":True,"PS1361":True,"PS8302":True,"SV0001_MAN":False, "SV0001_TRIG":False, "SV0001_RESET":False,"PV1_LCK":False,"PV1_RESET":False}

DIN_ACTIVATED = {"LS3338": False, "LS3339": False, "ES3347": False, "PUMP3305_CON": False, "PUMP3305_OL": False,"PS2352":False,"PS1361":False,"PS8302":False,"SV0001_MAN":False, "SV0001_TRIG":False, "SV0001_RESET":False,"PV1_LCK":False,"PV1_RESET":False}

DIN_ALARM = {"LS3338": False, "LS3339": False, "ES3347": False, "PUMP3305_CON": False, "PUMP3305_OL": False,"PS2352":False,"PS1361":False,"PS8302":False,"SV0001_MAN":False, "SV0001_TRIG":False, "SV0001_RESET":False,"PV1_LCK":False,"PV1_RESET":False}

VALVE_ADDRESS = {"PV1": 12288, "PV2": 12289, "PV3": 12290, "PV4": 12291, "PV5": 12292, "PV6": 12293,
                 "PV7": 12294, "PV8": 12295, "PV9": 12296,
                 "PV10": 12297, "PV11": 12298,"PV12": 12299, "PV1000": 12300, "PV1001": 12301, "PV1002": 12302,
                 "PV1003": 12303, "PV1004": 12304,
                 "PV1005": 12305, "PV1006": 12306,"PV1007": 12307, "SV0001":12308}
VALVE_INVERT_LIST = ["PV1000","PV1001","PV1002","PV1003","PV1004","PV1005","PV1006","PV1007","SV0001"]
NVALVE = len(VALVE_ADDRESS)
VALVE = {}
VALVE_OUT = {"PV1": 0, "PV2": 0, "PV3": 0, "PV4": 0, "PV5": 0, "PV6": 0,
                 "PV7": 0, "PV8": 0, "PV9": 0,
                 "PV10": 0, "PV11": 0,"PV12": 0, "PV1000": 0, "PV1001": 0, "PV1002": 0,
                 "PV1003": 0, "PV1004": 0,
                 "PV1005": 0, "PV1006": 0,"PV1007": 0,"SV0001":0}
VALVE_MAN = {"PV1": True, "PV2": True, "PV3": True, "PV4": True, "PV5": True, "PV6": True,
                 "PV7": True, "PV8": True, "PV9": True,
                 "PV10": True, "PV11": True,"PV12": True, "PV1000": True, "PV1001": True, "PV1002": True,
                 "PV1003": True, "PV1004": True,
                 "PV1005": True, "PV1006": True,"PV1007":True, "SV0001":True}
VALVE_INTLKD = {"PV1": False, "PV2": False, "PV3": False, "PV4": False, "PV5": False, "PV6": False,
                 "PV7": False, "PV8": False, "PV9": False,
                 "PV10": False, "PV11": False,"PV12": False, "PV1000": False, "PV1001": False, "PV1002": False,
                 "PV1003": False, "PV1004": False,
                 "PV1005": False, "PV1006": False,"PV1007":False, "SV0001":False}
VALVE_ERR = {"PV1": False, "PV2": False, "PV3": False, "PV4": False, "PV5": False, "PV6": False,
                 "PV7": False, "PV8": False, "PV9": False,
                 "PV10": False, "PV11": False,"PV12": False, "PV1000": False, "PV1001": False, "PV1002": False,
                 "PV1003": False, "PV1004": False,
                 "PV1005": False, "PV1006": False,"PV1007":False,"SV0001":False}
VALVE_COMMAND_CACHE = {"PV1": False, "PV2": False, "PV3": False, "PV4": False, "PV5": False, "PV6": False,
                 "PV7": False, "PV8": False, "PV9": False,
                 "PV10": False, "PV11": False,"PV12": False, "PV1000": False, "PV1001": False, "PV1002": False,
                 "PV1003": False, "PV1004": False,
                 "PV1005": False, "PV1006": False,"PV1007":False, "SV0001":False}
VALVE_BUSY = {"PV1": False, "PV2": False, "PV3": False, "PV4": False, "PV5": False, "PV6": False,
                 "PV7": False, "PV8": False, "PV9": False,
                 "PV10": False, "PV11": False,"PV12": False, "PV1000": False, "PV1001": False, "PV1002": False,
                 "PV1003": False, "PV1004": False,
                 "PV1005": False, "PV1006": False,"PV1007":False, "SV0001":False}

LOOPPID_ADR_BASE = {'HTR1001': (0,0), 'HTR1002': (0,1), 'HTR1003': (0,2),'HTR1004': (1,0), 'HTR1005': (1,1)}

LOOPPID_MODE0 = {'HTR1001': True, 'HTR1002': True, 'HTR1003': True,'HTR1004': True, 'HTR1005': True}

LOOPPID_MODE1 = {'HTR1001': False, 'HTR1002': False,'HTR1003': False, 'HTR1004': False, 'HTR1005': False}

LOOPPID_MODE2 = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}

LOOPPID_MODE3 = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}

LOOPPID_INTLKD = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}

LOOPPID_TT = {'HTR1001': [0,0], 'HTR1002': [0,0],'HTR1003': [0,0], 'HTR1004': [0,0], 'HTR1005': [0,0]}

LOOPPID_MAN = {'HTR1001': True, 'HTR1002': True, 'HTR1003': True,'HTR1004': True, 'HTR1005': True}

LOOPPID_ERR = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}

LOOPPID_SATHI = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}

LOOPPID_SATLO = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}

LOOPPID_EN = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}

LOOPPID_ALARM = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}

LOOPPID_OUT = {'HTR1001': -2, 'HTR1002': -2,'HTR1003': -2, 'HTR1004': -2, 'HTR1005': -2}

LOOPPID_IN = {'HTR1001': 0, 'HTR1002': 0, 'HTR1003': 0,'HTR1004': 0, 'HTR1005': 0}

LOOPPID_HI_LIM = {'HTR1001': 100, 'HTR1002': 100, 'HTR1003': 100,'HTR1004': 100, 'HTR1005': 100}

LOOPPID_LO_LIM = {'HTR1001': 0, 'HTR1002': 0, 'HTR1003': 0,'HTR1004': 0, 'HTR1005': 0}

LOOPPID_SET0 = {'HTR1001': 0, 'HTR1002': 0, 'HTR1003': 0,'HTR1004': 0, 'HTR1005': 0}

LOOPPID_SET1 = {'HTR1001': 0, 'HTR1002': 0, 'HTR1003': 0,'HTR1004': 0, 'HTR1005': 0}

LOOPPID_SET2 = {'HTR1001': 0, 'HTR1002': 0, 'HTR1003': 0,'HTR1004': 0, 'HTR1005': 0}

LOOPPID_SET3 = {'HTR1001': 0, 'HTR1002': 0, 'HTR1003': 0,'HTR1004': 0, 'HTR1005': 0}

LOOPPID_ACTIVATED = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}


LOOPPID_COMMAND_CACHE = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}


LOOPPID_BUSY = {'HTR1001': False, 'HTR1002': False, 'HTR1003': False,'HTR1004': False, 'HTR1005': False}



LOOPPID_ALARM_HI_LIM = {'HTR1001': 100, 'HTR1002': 100, 'HTR1003': 100,'HTR1004': 100, 'HTR1005': 100}

LOOPPID_ALARM_LO_LIM = {'HTR1001': 0, 'HTR1002': 0, 'HTR1003': 0,'HTR1004': 0, 'HTR1005': 0}


LOOP2PT_ADR_BASE = {'PUMP3305':14688}

LOOP2PT_MODE0 = {'PUMP3305': True}

LOOP2PT_MODE1 = {'PUMP3305': False}

LOOP2PT_MODE2 = {'PUMP3305': False}

LOOP2PT_MODE3 = {'PUMP3305': False}

LOOP2PT_INTLKD = {'PUMP3305': False}

LOOP2PT_MAN = {'PUMP3305': True}

LOOP2PT_ERR = {'PUMP3305': False}

LOOP2PT_OUT = {'PUMP3305': 0}

LOOP2PT_SET1 = {'PUMP3305': 0}

LOOP2PT_SET2 = {'PUMP3305': 0}

LOOP2PT_SET3 = {'PUMP3305': 0}

LOOP2PT_COMMAND_CACHE = {'PUMP3305': False}

LOOP2PT_BUSY = {'PUMP3305': False}

PROCEDURE_ADDRESS = {'TS_ADDREM': 15288, 'TS_EMPTY': 15290, 'TS_EMPTYALL': 15292, 'PU_PRIME': 15294, 'WRITE_SLOWDAQ': 15296, 'PRESSURE_CYCLE':15298}
PROCEDURE_RUNNING = {'TS_ADDREM': False, 'TS_EMPTY': False, 'TS_EMPTYALL': False, 'PU_PRIME': False, 'WRITE_SLOWDAQ': False, 'PRESSURE_CYCLE':False}
PROCEDURE_INTLKD = {'TS_ADDREM': False, 'TS_EMPTY': False, 'TS_EMPTYALL': False, 'PU_PRIME': False, 'WRITE_SLOWDAQ': False, 'PRESSURE_CYCLE':False}
PROCEDURE_EXIT = {'TS_ADDREM': 0, 'TS_EMPTY': 0, 'TS_EMPTYALL': 0, 'PU_PRIME': 0, 'WRITE_SLOWDAQ': 0, 'PRESSURE_CYCLE':0}

FLAG_ADDRESS={'MAN_TS':13288,'MAN_HYD':13289,"PCYCLE_AUTOCYCLE":13290}
FLAG_DIC = {'MAN_TS':False,'MAN_HYD':False,"PCYCLE_AUTOCYCLE":False}
FLAG_INTLKD={'MAN_TS':False,'MAN_HYD':False,"PCYCLE_AUTOCYCLE":False}
FLAG_BUSY={'MAN_TS':False,'MAN_HYD':False,"PCYCLE_AUTOCYCLE":False}

INTLK_D_ADDRESS={'TS1_INTLK': 13828, 'ES3347_INTLK': 13829, 'PUMP3305_OL_INTLK': 13830, 'TS2_INTLK': 13832, 'TS3_INTLK': 13836, 'PU_PRIME_INTLK': 13840}
INTLK_D_DIC={'TS1_INTLK': True, 'ES3347_INTLK': True, 'PUMP3305_OL_INTLK': True, 'TS2_INTLK': True, 'TS3_INTLK': True, 'PU_PRIME_INTLK': True}
INTLK_D_EN={'TS1_INTLK': True, 'ES3347_INTLK': True, 'PUMP3305_OL_INTLK': True, 'TS2_INTLK': True, 'TS3_INTLK': True, 'PU_PRIME_INTLK': True}
INTLK_D_COND={'TS1_INTLK': True, 'ES3347_INTLK': True, 'PUMP3305_OL_INTLK': True, 'TS2_INTLK': True, 'TS3_INTLK': True, 'PU_PRIME_INTLK': True}

INTLK_D_BUSY={'TS1_INTLK': True, 'ES3347_INTLK': True, 'PUMP3305_OL_INTLK': True, 'TS2_INTLK': True, 'TS3_INTLK': True, 'PU_PRIME_INTLK': True}

INTLK_A_ADDRESS={'TT2118_HI_INTLK': 13788, 'TT2118_LO_INTLK': 13792, 'PT4306_LO_INTLK': 13796, 'PT4306_HI_INTLK': 13800, 'PT4322_HI_INTLK': 13804, 'PT4322_HIHI_INTLK': 13808, 'PT4319_HI_INTLK': 13812, 'PT4319_HIHI_INTLK': 13816, 'PT4325_HI_INTLK': 13820, 'PT4325_HIHI_INTLK': 13824,
'TT6203_HI_INTLK': 13844, 'TT6207_HI_INTLK': 13848, 'TT6211_HI_INTLK': 13852, 'TT6213_HI_INTLK': 13856, 'TT6222_HI_INTLK': 13860,
'TT6407_HI_INTLK': 13864, 'TT6408_HI_INTLK': 13868, 'TT6409_HI_INTLK': 13872, 'TT6203_HIHI_INTLK': 13876, 'TT6207_HIHI_INTLK': 13880,
'TT6211_HIHI_INTLK': 13884, 'TT6213_HIHI_INTLK': 13888, 'TT6222_HIHI_INTLK': 13892, 'TT6407_HIHI_INTLK': 13896, 'TT6408_HIHI_INTLK': 13900,
'TT6409_HIHI_INTLK': 13904}
INTLK_A_DIC={'TT2118_HI_INTLK': True, 'TT2118_LO_INTLK': True, 'PT4306_LO_INTLK': True, 'PT4306_HI_INTLK': True, 'PT4322_HI_INTLK': True, 'PT4322_HIHI_INTLK': True, 'PT4319_HI_INTLK': True, 'PT4319_HIHI_INTLK': True, 'PT4325_HI_INTLK': True, 'PT4325_HIHI_INTLK': True,
             'TT6203_HI_INTLK': True, 'TT6207_HI_INTLK': True, 'TT6211_HI_INTLK': True, 'TT6213_HI_INTLK': True,
             'TT6222_HI_INTLK': True,
             'TT6407_HI_INTLK': True, 'TT6408_HI_INTLK': True, 'TT6409_HI_INTLK': True, 'TT6203_HIHI_INTLK': True,
             'TT6207_HIHI_INTLK': True,
             'TT6211_HIHI_INTLK': True, 'TT6213_HIHI_INTLK': True, 'TT6222_HIHI_INTLK': True,
             'TT6407_HIHI_INTLK': True, 'TT6408_HIHI_INTLK': True,
             'TT6409_HIHI_INTLK': True}
INTLK_A_EN={'TT2118_HI_INTLK': True, 'TT2118_LO_INTLK': True, 'PT4306_LO_INTLK': True, 'PT4306_HI_INTLK': True, 'PT4322_HI_INTLK': True, 'PT4322_HIHI_INTLK': True, 'PT4319_HI_INTLK': True, 'PT4319_HIHI_INTLK': True, 'PT4325_HI_INTLK': True, 'PT4325_HIHI_INTLK': True,
            'TT6203_HI_INTLK': True, 'TT6207_HI_INTLK': True, 'TT6211_HI_INTLK': True, 'TT6213_HI_INTLK': True,
            'TT6222_HI_INTLK': True,
            'TT6407_HI_INTLK': True, 'TT6408_HI_INTLK': True, 'TT6409_HI_INTLK': True, 'TT6203_HIHI_INTLK': True,
            'TT6207_HIHI_INTLK': True,
            'TT6211_HIHI_INTLK': True, 'TT6213_HIHI_INTLK': True, 'TT6222_HIHI_INTLK': True,
            'TT6407_HIHI_INTLK': True, 'TT6408_HIHI_INTLK': True,
            'TT6409_HIHI_INTLK': True
            }
INTLK_A_COND={'TT2118_HI_INTLK': True, 'TT2118_LO_INTLK': True, 'PT4306_LO_INTLK': True, 'PT4306_HI_INTLK': True, 'PT4322_HI_INTLK': True, 'PT4322_HIHI_INTLK': True, 'PT4319_HI_INTLK': True, 'PT4319_HIHI_INTLK': True, 'PT4325_HI_INTLK': True, 'PT4325_HIHI_INTLK': True,
              'TT6203_HI_INTLK': True, 'TT6207_HI_INTLK': True, 'TT6211_HI_INTLK': True, 'TT6213_HI_INTLK': True,
              'TT6222_HI_INTLK': True,
              'TT6407_HI_INTLK': True, 'TT6408_HI_INTLK': True, 'TT6409_HI_INTLK': True, 'TT6203_HIHI_INTLK': True,
              'TT6207_HIHI_INTLK': True,
              'TT6211_HIHI_INTLK': True, 'TT6213_HIHI_INTLK': True, 'TT6222_HIHI_INTLK': True,
              'TT6407_HIHI_INTLK': True, 'TT6408_HIHI_INTLK': True,
              'TT6409_HIHI_INTLK': True
              }
INTLK_A_SET={'TT2118_HI_INTLK': 0, 'TT2118_LO_INTLK': 0, 'PT4306_LO_INTLK': 0, 'PT4306_HI_INTLK': 0, 'PT4322_HI_INTLK': 0, 'PT4322_HIHI_INTLK': 0, 'PT4319_HI_INTLK': 0, 'PT4319_HIHI_INTLK': 0, 'PT4325_HI_INTLK': 0, 'PT4325_HIHI_INTLK': 0,
             'TT6203_HI_INTLK': 0, 'TT6207_HI_INTLK': 0, 'TT6211_HI_INTLK': 0, 'TT6213_HI_INTLK': 0,
             'TT6222_HI_INTLK': 0,
             'TT6407_HI_INTLK': 0, 'TT6408_HI_INTLK': 0, 'TT6409_HI_INTLK': 0, 'TT6203_HIHI_INTLK': 0,
             'TT6207_HIHI_INTLK': 0,
             'TT6211_HIHI_INTLK': 0, 'TT6213_HIHI_INTLK': 0, 'TT6222_HIHI_INTLK': 0,
             'TT6407_HIHI_INTLK': 0, 'TT6408_HIHI_INTLK': 0,
             'TT6409_HIHI_INTLK': 0 }

INTLK_A_BUSY={'TT2118_HI_INTLK': 0, 'TT2118_LO_INTLK': 0, 'PT4306_LO_INTLK': 0, 'PT4306_HI_INTLK': 0, 'PT4322_HI_INTLK': 0, 'PT4322_HIHI_INTLK': 0, 'PT4319_HI_INTLK': 0, 'PT4319_HIHI_INTLK': 0, 'PT4325_HI_INTLK': 0, 'PT4325_HIHI_INTLK': 0,
             'TT6203_HI_INTLK': 0, 'TT6207_HI_INTLK': 0, 'TT6211_HI_INTLK': 0, 'TT6213_HI_INTLK': 0,
             'TT6222_HI_INTLK': 0,
             'TT6407_HI_INTLK': 0, 'TT6408_HI_INTLK': 0, 'TT6409_HI_INTLK': 0, 'TT6203_HIHI_INTLK': 0,
             'TT6207_HIHI_INTLK': 0,
             'TT6211_HIHI_INTLK': 0, 'TT6213_HIHI_INTLK': 0, 'TT6222_HIHI_INTLK': 0,
             'TT6407_HIHI_INTLK': 0, 'TT6408_HIHI_INTLK': 0,
             'TT6409_HIHI_INTLK': 0 }

FF_ADDRESS={'TS_ADDREM_FF': 14788, 'TS_EMPTY_FF': 14789, 'TS_EMPTYALL_FF': 14790, 'SLOWDAQ_FF': 14791, 'PCYCLE_ABORT_FF': 14792, 'PCYCLE_FASTCOMP_FF': 14793, 'PCYCLE_SLOWCOMP_FF': 14794, 'PCYCLE_CYLEQ_FF': 14795, 'PCYCLE_CYLBLEED_FF': 14796, 'PCYCLE_ACCHARGE_FF': 14797}
FF_DIC={'TS_ADDREM_FF': 0, 'TS_EMPTY_FF': 0, 'TS_EMPTYALL_FF': 0, 'SLOWDAQ_FF': 0, 'PCYCLE_ABORT_FF': 0, 'PCYCLE_FASTCOMP_FF': 0, 'PCYCLE_SLOWCOMP_FF': 0, 'PCYCLE_CYLEQ_FF': 0, 'PCYCLE_CYLBLEED_FF': 0, 'PCYCLE_ACCHARGE_FF': 0}

PARAM_F_ADDRESS ={'TS_ADDREM_MASS': 16790,'PCYCLE_PSET': 16794,'PCYCLE_MAXEQPDIFF': 16802,'PCYCLE_MAXACCDPDT': 16806,'PCYCLE_MAXBLEEDDPDT': 16810, 'PCYCLE_SLOWCOMP_SET': 16812}
PARAM_F_DIC ={'TS_ADDREM_MASS': 0,'PCYCLE_PSET': 0,'PCYCLE_MAXEQPDIFF': 0,'PCYCLE_MAXACCDPDT': 0,'PCYCLE_MAXBLEEDDPDT':0, 'PCYCLE_SLOWCOMP_SET': 0}

PARAM_T_ADDRESS = {'PCYCLE_MAXEXPTIME': 16798, 'PCYCLE_MAXEQTIME': 16800,'PCYCLE_MAXACCTIME': 16804,'PCYCLE_MAXBLEEDTIME': 16808,"TS_ADDREM_MAXTIME":16814, "TS_ADDREM_FLOWET":16816}
PARAM_T_DIC = {'PCYCLE_MAXEXPTIME': 0, 'PCYCLE_MAXEQTIME': 0,'PCYCLE_MAXACCTIME': 0,'PCYCLE_MAXBLEEDTIME': 0,"TS_ADDREM_MAXTIME":0, "TS_ADDREM_FLOWET":0}

PARAM_I_ADDRESS = {'TS_SEL': 16788}
PARAM_I_DIC = {'TS_SEL': 0}

PARAM_B_ADDRESS = {'TS1_EMPTY':(16792,0),'TS2_EMPTY':(16792,1), 'TS3_EMPTY':(16792,2)}
PARAM_B_DIC = {'TS1_EMPTY':0,'TS2_EMPTY':0, 'TS3_EMPTY':0}

TIME_ADDRESS = {'PCYCLE_EXPTIME': 16796}
TIME_DIC = {'PCYCLE_EXPTIME': 0}
# This is for checkbox initialization when BKG restarts
# first digit means whether server(BKG) send check_ini request to client(GUI)
# second digit means whether client(GUI) send check box info to server(BKG)
# true value table
#[0,0]
#[0,1]
#[1,1]
#[1,0]
INI_CHECK= True

TT_AD1_PARA = {"RTD9": 0, "RTD10":0, "RTD11": 0, "RTD12": 0, "RTD13": 0, "RTD14": 0}


TT_AD1_RATE = {"RTD9": 30, "RTD10": 30, "RTD11": 30, "RTD12": 30, "RTD13": 30, "RTD14": 30}

HTRTD_PARA = {"RTD1":0,"RTD2":0,"RTD3":0,
                 "RTD4":0,"RTD5":0,"RTD6":0, "RTD7":0, "RTD8":0}

HTRTD_RATE = {"RTD1":30,"RTD2":30,"RTD3":30,
                 "RTD4":30,"RTD5":30,"RTD6":30, "RTD7":30, "RTD8":30}
TT_AD2_PARA = { }


TT_AD2_RATE = { }



LL_PARA ={"LL":0}
LL_RATE ={"LL":30}


PT_PARA = {"PT001": 0, "PT002": 0, "PT003": 0, "PT004": 0, "PT1000": 0,
              "PT1001": 0, "PT1002": 0, "PT0": 0}

PT_RATE = {"PT001": 30, "PT002": 30, "PT003": 30, "PT004": 30, "PT1000": 30,
              "PT1001": 30, "PT1002": 30, "PT0": 30}

LEFT_REAL_PARA = {'FCV1001': 0, 'FCV1002': 0, "BGAAH01":0, "BGAAH02": 0,  "MFC1008": 0,
                  "PT003ST":0,"TT0001":0,"TT0002":0,"TT0001ST":0,"TT0002ST":0, "SV0001_TIME": 0}


LEFT_REAL_RATE = {'FCV1001': 30, 'FCV1002': 30, "BGAAH01": 30, "BGAAH02": 30, "MFC1008": 30,
                  "PT003ST":30,"TT0001":30,"TT0002":30,"TT0001ST":30,"TT0002ST":30, "SV0001_TIME": 30}

DIN_PARA = {"LS3338": 0, "LS3339": 0, "ES3347": 0, "PUMP3305_CON": 0, "PUMP3305_OL": 0,"PS2352":0,"PS1361":0,"PS8302":0, "SV0001_MAN":0, "SV0001_TRIG":0, "SV0001_RESET":0, "PV1_LCK": 0,"PV1_RESET":0}

DIN_RATE = {"LS3338": 30, "LS3339": 30, "ES3347": 30, "PUMP3305_CON": 30, "PUMP3305_OL": 30,"PS2352":30,"PS1361":30,"PS8302":30, "SV0001_MAN":3, "SV0001_TRIG":3, "SV0001_RESET":3, "PV1_LCK": 30,"PV1_RESET":30}

LOOPPID_PARA = {'HTR1001': 0, 'HTR1002': 0, 'HTR1003': 0,'HTR1004': 0, 'HTR1005': 0}
LOOPPID_RATE = {'HTR1001': 30, 'HTR1002': 30, 'HTR1002': 30,'HTR1004': 30, 'HTR1005': 30}

BROAD_CAST_PARA =0
BROAD_CAST_RATE = 100

DATABASE_PARA = {"alarm": 0, "TT": 0, "PT":0 , "REAL":0 ,  "Din": 0, "Valve": 0, "Switch": 0, "LOOPPID": 0,
                 "LOOP2PT":0 , "FLAG": 0, "INTLK_A":0, "INTLK_D":0, "FF": 0, "PARAM_F":0, "PARAM_I": 0, "PARAM_B":0,
                 "PARAM_T":0, "TIME":0, "LL":0, "CAP":0}
DATABASE_RATE = {"alarm": 1000, "TT": 3, "PT":3 , "REAL":3 ,  "Din": 5, "Valve": 90, "Switch": 90, "LOOPPID": 5,
                 "LOOP2PT":90 , "FLAG": 90, "INTLK_A":90, "INTLK_D":90, "FF": 90, "PARAM_F":90, "PARAM_I": 90, "PARAM_B":90,
                 "PARAM_T":90, "TIME":90 , "LL": 3, "CAP": 5}
DATABASE_HOLD = 300
PLC_HOLD = 300
SOCKET_HOLD =300
BROAD_CAST_HOLD = 300
COUPP_trigger_PARA = 0 # 1 hours the unit is different from other parameters because during every loop it will sleep 1 minutes
COUPP_trigger_RATE =60
COUPP_trigger_MID = 2
MAINALARM_LONG_PARA = 0
MAINALARM_LONG_RATE = 300

DIC_PACK = {"data": {"TT": {"AD1": {"value": TT_AD1_DIC, "high": TT_AD1_HIGHLIMIT, "low": TT_AD1_LOWLIMIT},
                             "AD2": {"value": TT_AD2_DIC, "high": TT_AD2_HIGHLIMIT, "low": TT_AD2_LOWLIMIT},
                            "LS":{"value": HTRTD_DIC, "high": HTRTD_HIGHLIMIT, "low": HTRTD_LOWLIMIT}},
                                  "PT": {"value": PT_DIC, "high": PT_HIGHLIMIT, "low": PT_LOWLIMIT},
                                  "CAP": {"value": CAP_DIC},
                                  "LEFT_REAL": {"value": LEFT_REAL_DIC, "high": LEFT_REAL_HIGHLIMIT, "low": LEFT_REAL_LOWLIMIT},
                                  "LL": {"value": LL_DIC, "high": LL_HIGHLIMIT, "low": LL_LOWLIMIT},
                                  "Valve": {"OUT": VALVE_OUT,
                                            "INTLKD": VALVE_INTLKD,
                                            "MAN": VALVE_MAN,
                                            "ERR": VALVE_ERR,
                                            "Busy":VALVE_BUSY},
                                  "Switch": {"OUT": SWITCH_OUT,
                                             "INTLKD": SWITCH_INTLKD,
                                             "MAN": SWITCH_MAN,
                                             "ERR": SWITCH_ERR},
                                  "Din": {'value': DIN_DIC,"high": DIN_HIGHLIMIT, "low": DIN_LOWLIMIT},
                                  "LOOPPID": {"MODE0": LOOPPID_MODE0,
                                              "MODE1": LOOPPID_MODE1,
                                              "MODE2": LOOPPID_MODE2,
                                              "MODE3": LOOPPID_MODE3,
                                              "INTLKD": LOOPPID_INTLKD,
                                              "MAN": LOOPPID_MAN,
                                              "TT":LOOPPID_TT,
                                              "ERR": LOOPPID_ERR,
                                              "SATHI": LOOPPID_SATHI,
                                              "SATLO": LOOPPID_SATLO,
                                              "EN": LOOPPID_EN,
                                              "OUT": LOOPPID_OUT,
                                              "IN": LOOPPID_IN,
                                              "HI_LIM": LOOPPID_HI_LIM,
                                              "LO_LIM": LOOPPID_LO_LIM,
                                              "SET0": LOOPPID_SET0,
                                              "SET1": LOOPPID_SET1,
                                              "SET2": LOOPPID_SET2,
                                              "SET3": LOOPPID_SET3,
                                              "Busy":LOOPPID_BUSY,
                                              "Alarm":LOOPPID_ALARM,
                                              "Alarm_HighLimit":LOOPPID_ALARM_HI_LIM,
                                              "Alarm_LowLimit":LOOPPID_ALARM_LO_LIM},
                                  "LOOP2PT": {"MODE0": LOOP2PT_MODE0,
                                              "MODE1": LOOP2PT_MODE1,
                                              "MODE2": LOOP2PT_MODE2,
                                              "MODE3": LOOP2PT_MODE3,
                                              "INTLKD": LOOP2PT_INTLKD,
                                              "MAN": LOOP2PT_MAN,
                                              "ERR": LOOP2PT_ERR,
                                              "OUT": LOOP2PT_OUT,
                                              "SET1": LOOP2PT_SET1,
                                              "SET2": LOOP2PT_SET2,
                                              "SET3": LOOP2PT_SET3,
                                              "Busy":LOOP2PT_BUSY},
                                  "INTLK_D": {"value": INTLK_D_DIC,
                                              "EN": INTLK_D_EN,
                                              "COND": INTLK_D_COND,
                                              "Busy":INTLK_D_BUSY},
                                  "INTLK_A": {"value":INTLK_A_DIC,
                                              "EN":INTLK_A_EN,
                                              "COND":INTLK_A_COND,
                                              "SET":INTLK_A_SET,
                                              "Busy":INTLK_A_BUSY},
                                  "FLAG": {"value":FLAG_DIC,
                                           "INTLKD":FLAG_INTLKD,
                                           "Busy":FLAG_BUSY},
                                  "Procedure": {"Running": PROCEDURE_RUNNING, "INTLKD": PROCEDURE_INTLKD, "EXIT": PROCEDURE_EXIT}},
                         "Alarm": {"TT": {"AD1": TT_AD1_ALARM,"AD2": TT_AD2_ALARM, "LS":HTRTD_ALARM
                                          },
                                   "PT": PT_ALARM,
                                   "LEFT_REAL": LEFT_REAL_ALARM,
                                   "Din": DIN_ALARM,
                                   "LOOPPID": LOOPPID_ALARM,
                                   "LL":LL_ALARM},
                         "Active": {"TT": {"AD1": TT_AD1_ACTIVATED,"AD2": TT_AD2_ACTIVATED, "LS":HTRTD_ACTIVATED
                                          },
                                   "PT": PT_ACTIVATED,
                                   "LEFT_REAL": LEFT_REAL_ACTIVATED,
                                    "Din": DIN_ACTIVATED,
                                    "LOOPPID": LOOPPID_ACTIVATED,
                                    "LL":LL_ACTIVATED,
                                    "INI_CHECK": INI_CHECK
                                    },
                         "MainAlarm": MAINALARM
                         }



# if same key conflicts, the later one will replace the previous one
def merge_dic(dic1,*args):
    res = dic1
    for dicts in args:
       res = {**res, **dicts}
    return res
