"""
Class PLC is used to read/write via modbus to the temperature PLC

To read the variable, just call the ReadAll() method
To write to a variable, call the proper setXXX() method

By: Mathieu Laurin

v1.0 Initial code 25/11/19 ML
v1.1 Initialize values, flag when values are updated more modbus variables 04/03/20 ML
"""

import struct, time, zmq, sys, pickle, copy, logging, threading, queue, socket, json
from pythonping import ping
import numpy as np
import sshtunnel, ssl, smtplib
from Henry_watchdog_database import *
from email.header import Header
from smtplib import SMTP_SSL
import Henry_env as env
import Henry_alarm_autoload as AL
from Henry_watchdog_database import *
from email.mime.text import MIMEText
import socket
import requests
import logging,os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import Henry_env as sec

import statistics
import fdc1004_logger as fdc
import serial

# delete random number package when you read real data from PLC
import random
from pymodbus.client.sync import ModbusTcpClient
from lakeshore import Model336
# delete random number package when you read real data from PLC
import random
from pymodbus.client.sync import ModbusTcpClient

# Initialization of Address, Value Matrix

# logging.basicConfig(filename="/home/hep/sbc_error_log.log")
sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    print("ExceptType: ", exctype, "Value: ", value, "Traceback: ", traceback)
    # sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = exception_hook


# output address to attribute function in FP ()
def FPADS_OUT_AT(outaddress):
    # 1e5 digit
    e5 = outaddress // 10000
    e4 = (outaddress % 10000) // 1000
    e3 = (outaddress % 1000) // 100
    e2 = (outaddress % 100) // 10
    e1 = (outaddress % 10) // 1
    new_e5 = e5 - 2
    new_e4 = e4
    new_e321 = (e3 * 100 + e2 * 10 + e1) * 4
    new_address = new_e5 * 10000 + new_e4 * 1000 + new_e321
    print(e5, e4, e3, e2, e1)
    print(new_address)
    return new_address


def LS_TT_translate(receive):
    # receive would be "float1,float2,float3,float4\r\n"
    # we need to return (float1, float2, float3, float4)
    try:
        stripped =  receive.strip("\n")
        stripped =  stripped.strip("\r")
    except:
        stripped = receive
    # stripped = stripped.strip("+")
    # print(stripped)
    str_list = eval(stripped)
    # print("split",str_list)
    float_list =  [float(i) for i in str_list]
    res = tuple(float_list)
    # print("res",res)
    return(res)

def LS_OUT_translate(receive):
    # receive would be "float1,float2,float3,float4\r\n"
    # we need to return (float1, float2, float3, float4)
    try:
        stripped =  receive.strip("\n")
        stripped =  stripped.strip("\r")

        res = stripped.strip("+")
    except:
        return(receive)
    # print("res",res)
    return(res)


class PLC:
    def __init__(self, plc_data, plc_lock, command_data, command_lock, alarm_stack, alarm_lock):
        self.plc_data = plc_data
        self.plc_lock = plc_lock
        self.command_data = command_data
        self.command_lock = command_lock
        self.alarm_stack =  alarm_stack
        self.alarm_lock = alarm_lock

        self.IP_LS1 = 'LSA2BVC'
        self.PORT_LS1 = 7777
        self.LS1_con = False
        try:
            self.Client_LS1 = Model336(serial_number=self.IP_LS1)
            self.LS1_con = True
            print("LS1 connected: " + str(self.LS1_con))
        except:
            self.LS1_con = False
            print("LS1 connected: " + str(self.LS1_con))


        self.IP_LS2 = 'LSA2AJN'
        self.PORT_LS2 = 7777
        self.LS2_con = False
        try:
            self.Client_LS2 = Model336(serial_number=self.IP_LS2)
            self.LS2_con = True
            print("LS2 connected: " + str(self.LS2_con))
        except:
            self.LS2_con = False
            print("LS2 connected: " + str(self.LS2_con))

        # Adam
        IP_AD1 = "10.111.19.101"
        PORT_AD1 = 502
        # 135,,139, 445,3389,5700,6000,9012
        self.Client_AD1 = ModbusTcpClient(IP_AD1, port=PORT_AD1)
        self.Connected_AD1 = self.Client_AD1.connect()

        print(" AD1 connected: " + str(self.Connected_AD1))
        self.AD1_updatesignal = False

        IP_AD2 = "10.111.19.104"

        PORT_AD2 = 502

        self.Client_AD2 = ModbusTcpClient(IP_AD2, port=PORT_AD2)
        self.Connected_AD2 = self.Client_AD2.connect()
        print(" AD2 connected: " + str(self.Connected_AD2))
        self.AD2_updatesignal = False

        IP_BO = "10.111.19.106"

        PORT_BO = 502

        self.Client_BO = ModbusTcpClient(IP_BO, port=PORT_BO)
        self.Connected_BO = self.Client_BO.connect()

        print(" BO connected: " + str(self.Connected_BO))

        self.BO_updatesignal = False

        # FDC1004EVM (connected over serial via fdc1004_logger.py, not modbus).
        self.fdc_ser = None
        self.fdc_reader = None
        self.fdc_channel_samples = [[], [], [], []]
        self.fdc_interval_start = time.time()
        self.Connected_FDC1004 = self._connect_fdc1004()
        print(" FDC1004 connected: " + str(self.Connected_FDC1004))



        self.IP_LL = sec.LL_ADDRESS["LL"][0]
        # it maychange...
        # Lakeshore1 10.111.19.100 and lakeshore 2 10.111.19.102
        self.PORT_LL = 7180
        self.BUFFER_SIZE = 1024
        try:
            self.socket_LL = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_LL.connect((self.IP_LL, self.PORT_LL))
            self.Connected_LL = True
            print("LL connected: " + str(self.Connected_LL))
        except:
            self.Connected_LL = False
            print("LL connected: " + str(self.Connected_LL))

        # wait 1 second to init
        time.sleep(1)

        self.module_connection_alarm = copy.copy(sec.MODULE_CONNECTION_ALARM)

        self.TT_AD1_address = copy.copy(sec.TT_AD1_ADDRESS)
        self.TT_AD2_address = copy.copy(sec.TT_AD2_ADDRESS)
        self.HTRTD_address = copy.copy(sec.HTRTD_ADDRESS)
        self.PT_address = copy.copy(sec.PT_ADDRESS)

        self.LEFT_REAL_address = copy.copy(sec.LEFT_REAL_ADDRESS)

        self.TT_AD1_dic = copy.copy(sec.TT_AD1_DIC)
        self.TT_AD1_cali = copy.copy(sec.TT_AD1_CALI)
        self.TT_AD2_dic = copy.copy(sec.TT_AD2_DIC)

        self.HTRTD_dic = copy.copy(sec.HTRTD_DIC)

        self.PT_dic = copy.copy(sec.PT_DIC)

        self.CAP_dic = copy.copy(sec.CAP_DIC)

        self.LEFT_REAL_dic = copy.copy(sec.LEFT_REAL_DIC)

        self.TT_AD1_LowLimit = copy.copy(sec.TT_AD1_LOWLIMIT)

        self.TT_AD1_HighLimit = copy.copy(sec.TT_AD1_HIGHLIMIT)

        self.TT_AD2_LowLimit = copy.copy(sec.TT_AD2_LOWLIMIT)

        self.TT_AD2_HighLimit = copy.copy(sec.TT_AD2_HIGHLIMIT)

        self.HTRTD_LowLimit = copy.copy(sec.HTRTD_LOWLIMIT)
        self.HTRTD_HighLimit = copy.copy(sec.HTRTD_HIGHLIMIT)
        self.PT_LowLimit = copy.copy(sec.PT_LOWLIMIT)
        self.PT_HighLimit = copy.copy(sec.PT_HIGHLIMIT)

        self.LEFT_REAL_HighLimit = copy.copy(sec.LEFT_REAL_HIGHLIMIT)
        self.LEFT_REAL_LowLimit = copy.copy(sec.LEFT_REAL_LOWLIMIT)

        self.TT_AD1_Activated = copy.copy(sec.TT_AD1_ACTIVATED)
        self.TT_AD2_Activated = copy.copy(sec.TT_AD2_ACTIVATED)
        self.HTRTD_Activated = copy.copy(sec.HTRTD_ACTIVATED)
        self.PT_Activated = copy.copy(sec.PT_ACTIVATED)
        self.LEFT_REAL_Activated = copy.copy(sec.LEFT_REAL_ACTIVATED)

        self.TT_AD1_Alarm = copy.copy(sec.TT_AD1_ALARM)
        self.TT_AD2_Alarm = copy.copy(sec.TT_AD2_ALARM)
        self.HTRTD_Alarm = copy.copy(sec.HTRTD_ALARM)

        self.PT_Alarm = copy.copy(sec.PT_ALARM)
        self.LEFT_REAL_Alarm = copy.copy(sec.LEFT_REAL_ALARM)
        self.MainAlarm = copy.copy(sec.MAINALARM)
        self.MAN_SET = copy.copy(sec.MAN_SET)

        self.nTT_AD1 = copy.copy(sec.NTT_AD1)
        self.nTT_AD2 = copy.copy(sec.NTT_AD2)
        self.nHTRTD = copy.copy(sec.NHTRTD)
        self.nPT = copy.copy(sec.NPT)
        self.nREAL = copy.copy(sec.NREAL)

        self.PT_setting = copy.copy(sec.PT_SETTING)
        self.nPT_Attribute = copy.copy(sec.NPT_ATTRIBUTE)

        self.Din_address = copy.copy(sec.DIN_ADDRESS)
        self.nDin = copy.copy(sec.NDIN)
        self.Din = copy.copy(sec.DIN)
        self.Din_dic = copy.copy(sec.DIN_DIC)
        self.Din_LowLimit = copy.copy(sec.DIN_LOWLIMIT)
        self.Din_HighLimit = copy.copy(sec.DIN_HIGHLIMIT)
        self.Din_Activated = copy.copy(sec.DIN_ACTIVATED)
        self.Din_Alarm = copy.copy(sec.DIN_ALARM)

        self.valve_address = copy.copy(sec.VALVE_ADDRESS)
        self.nValve = copy.copy(sec.NVALVE)
        self.Valve = copy.copy(sec.VALVE)
        self.Valve_OUT = copy.copy(sec.VALVE_OUT)
        self.Valve_MAN = copy.copy(sec.VALVE_MAN)
        self.Valve_INTLKD = copy.copy(sec.VALVE_INTLKD)
        self.Valve_ERR = copy.copy(sec.VALVE_ERR)
        self.Valve_Busy = copy.copy(sec.VALVE_BUSY)
        self.valve_invert_list = sec.VALVE_INVERT_LIST

        self.LOOPPID_ADR_BASE = copy.copy(sec.LOOPPID_ADR_BASE)

        self.LOOPPID_MODE0 = copy.copy(sec.LOOPPID_MODE0)

        self.LOOPPID_MODE1 = copy.copy(sec.LOOPPID_MODE1)

        self.LOOPPID_MODE2 = copy.copy(sec.LOOPPID_MODE2)

        self.LOOPPID_MODE3 = copy.copy(sec.LOOPPID_MODE3)

        self.LOOPPID_INTLKD = copy.copy(sec.LOOPPID_INTLKD)
        self.LOOPPID_TT = copy.copy(sec.LOOPPID_TT)

        self.LOOPPID_MAN = copy.copy(sec.LOOPPID_MAN)

        self.LOOPPID_ERR = copy.copy(sec.LOOPPID_ERR)

        self.LOOPPID_SATHI = copy.copy(sec.LOOPPID_SATHI)

        self.LOOPPID_SATLO = copy.copy(sec.LOOPPID_SATLO)

        self.LOOPPID_EN = copy.copy(sec.LOOPPID_EN)

        self.LOOPPID_OUT = copy.copy(sec.LOOPPID_OUT)

        self.LOOPPID_IN = copy.copy(sec.LOOPPID_IN)

        self.LOOPPID_HI_LIM = copy.copy(sec.LOOPPID_HI_LIM)

        self.LOOPPID_LO_LIM = copy.copy(sec.LOOPPID_LO_LIM)

        self.LOOPPID_SET0 = copy.copy(sec.LOOPPID_SET0)

        self.LOOPPID_SET1 = copy.copy(sec.LOOPPID_SET1)

        self.LOOPPID_SET2 = copy.copy(sec.LOOPPID_SET2)

        self.LOOPPID_SET3 = copy.copy(sec.LOOPPID_SET3)
        self.LOOPPID_Busy = copy.copy(sec.LOOPPID_BUSY)
        self.LOOPPID_Activated = copy.copy(sec.LOOPPID_ACTIVATED)
        self.LOOPPID_Alarm = copy.copy(sec.LOOPPID_ALARM)
        self.LOOPPID_Alarm_HighLimit = copy.copy(sec.LOOPPID_ALARM_HI_LIM)
        self.LOOPPID_Alarm_LowLimit = copy.copy(sec.LOOPPID_ALARM_LO_LIM)

        self.LOOP2PT_ADR_BASE = copy.copy(sec.LOOP2PT_ADR_BASE)
        self.LOOP2PT_MODE0 = copy.copy(sec.LOOP2PT_MODE0)
        self.LOOP2PT_MODE1 = copy.copy(sec.LOOP2PT_MODE1)
        self.LOOP2PT_MODE2 = copy.copy(sec.LOOP2PT_MODE2)
        self.LOOP2PT_MODE3 = copy.copy(sec.LOOP2PT_MODE3)
        self.LOOP2PT_INTLKD = copy.copy(sec.LOOP2PT_INTLKD)
        self.LOOP2PT_MAN = copy.copy(sec.LOOP2PT_MAN)
        self.LOOP2PT_ERR = copy.copy(sec.LOOP2PT_ERR)
        self.LOOP2PT_OUT = copy.copy(sec.LOOP2PT_OUT)
        self.LOOP2PT_SET1 = copy.copy(sec.LOOP2PT_SET1)
        self.LOOP2PT_SET2 = copy.copy(sec.LOOP2PT_SET2)
        self.LOOP2PT_SET3 = copy.copy(sec.LOOP2PT_SET3)
        self.LOOP2PT_Busy = copy.copy(sec.LOOP2PT_BUSY)

        self.Procedure_address = copy.copy(sec.PROCEDURE_ADDRESS)
        self.Procedure_running = copy.copy(sec.PROCEDURE_RUNNING)
        self.Procedure_INTLKD = copy.copy(sec.PROCEDURE_INTLKD)
        self.Procedure_EXIT = copy.copy(sec.PROCEDURE_EXIT)

        self.INTLK_D_ADDRESS = copy.copy(sec.INTLK_D_ADDRESS)
        self.INTLK_D_DIC = copy.copy(sec.INTLK_D_DIC)
        self.INTLK_D_EN = copy.copy(sec.INTLK_D_EN)
        self.INTLK_D_COND = copy.copy(sec.INTLK_D_COND)
        self.INTLK_D_Busy = copy.copy(sec.INTLK_D_BUSY)
        self.INTLK_A_ADDRESS = copy.copy(sec.INTLK_A_ADDRESS)
        self.INTLK_A_DIC = copy.copy(sec.INTLK_A_DIC)
        self.INTLK_A_EN = copy.copy(sec.INTLK_A_EN)
        self.INTLK_A_COND = copy.copy(sec.INTLK_A_COND)
        self.INTLK_A_SET = copy.copy(sec.INTLK_A_SET)
        self.INTLK_A_Busy = copy.copy(sec.INTLK_A_BUSY)

        self.FLAG_ADDRESS = copy.copy(sec.FLAG_ADDRESS)
        self.FLAG_DIC = copy.copy(sec.FLAG_DIC)
        self.FLAG_INTLKD = copy.copy(sec.FLAG_INTLKD)
        self.FLAG_Busy = copy.copy(sec.FLAG_BUSY)

        self.FF_ADDRESS = copy.copy(sec.FF_ADDRESS)
        self.FF_DIC = copy.copy(sec.FF_DIC)

        self.PARAM_F_ADDRESS = copy.copy(sec.PARAM_F_ADDRESS)
        self.PARAM_F_DIC = copy.copy(sec.PARAM_F_DIC)

        self.PARAM_I_ADDRESS = copy.copy(sec.PARAM_I_ADDRESS)
        self.PARAM_I_DIC = copy.copy(sec.PARAM_I_DIC)

        self.PARAM_B_ADDRESS = copy.copy(sec.PARAM_B_ADDRESS)
        self.PARAM_B_DIC = copy.copy(sec.PARAM_B_DIC)

        self.PARAM_T_ADDRESS = copy.copy(sec.PARAM_T_ADDRESS)
        self.PARAM_T_DIC = copy.copy(sec.PARAM_T_DIC)

        self.TIME_ADDRESS = copy.copy(sec.TIME_ADDRESS)
        self.TIME_DIC = copy.copy(sec.TIME_DIC)

        self.LL_dic = copy.copy(sec.LL_DIC)
        self.LL_address = copy.copy(sec.LL_ADDRESS)
        self.LL_LowLimit = copy.copy(sec.LL_LOWLIMIT)
        self.LL_HighLimit = copy.copy(sec.LL_HIGHLIMIT)
        self.LL_Alarm = copy.copy(sec.LL_ALARM)
        self.LL_Activated = copy.copy(sec.LL_ACTIVATED)
        self.nLL = copy.copy(sec.NLL)

        self.ini_check = copy.copy(sec.INI_CHECK)


        self.data_dic  = {"data": {"TT": {"AD1": {"value": self.TT_AD1_dic, "high": self.TT_AD1_HighLimit, "low": self.TT_AD1_LowLimit},
                             "AD2": {"value": self.TT_AD2_dic, "high": self.TT_AD2_HighLimit, "low": self.TT_AD2_LowLimit},
                            "LS":{"value": self.HTRTD_dic, "high": self.HTRTD_HighLimit, "low": self.HTRTD_LowLimit}},
                                  "PT": {"value": self.PT_dic, "high": self.PT_HighLimit, "low": self.PT_LowLimit},
                                  "CAP": {"value": self.CAP_dic},
                                  "LEFT_REAL": {"value": self.LEFT_REAL_dic, "high": self.LEFT_REAL_HighLimit, "low": self.LEFT_REAL_LowLimit},
                                  "LL": {"value": self.LL_dic, "high": self.LL_HighLimit, "low": self.LL_LowLimit},
                                  "Valve": {"OUT": self.Valve_OUT,
                                            "INTLKD": self.Valve_INTLKD,
                                            "MAN": self.Valve_MAN,
                                            "ERR": self.Valve_ERR,
                                            "Busy":self.Valve_Busy},
                                  "Din": {'value': self.Din_dic,"high": self.Din_HighLimit, "low": self.Din_LowLimit},
                                  "LOOPPID": {"MODE0": self.LOOPPID_MODE0,
                                              "MODE1": self.LOOPPID_MODE1,
                                              "MODE2": self.LOOPPID_MODE2,
                                              "MODE3": self.LOOPPID_MODE3,
                                              "INTLKD": self.LOOPPID_INTLKD,
                                              "MAN": self.LOOPPID_MAN,
                                              "TT":self.LOOPPID_TT,
                                              "ERR": self.LOOPPID_ERR,
                                              "SATHI": self.LOOPPID_SATHI,
                                              "SATLO": self.LOOPPID_SATLO,
                                              "EN": self.LOOPPID_EN,
                                              "OUT": self.LOOPPID_OUT,
                                              "IN": self.LOOPPID_IN,
                                              "HI_LIM": self.LOOPPID_HI_LIM,
                                              "LO_LIM": self.LOOPPID_LO_LIM,
                                              "SET0": self.LOOPPID_SET0,
                                              "SET1": self.LOOPPID_SET1,
                                              "SET2": self.LOOPPID_SET2,
                                              "SET3": self.LOOPPID_SET3,
                                              "Busy": self.LOOPPID_Busy,
                                              "Alarm": self.LOOPPID_Alarm,
                                              "Alarm_HighLimit": self.LOOPPID_Alarm_HighLimit,
                                              "Alarm_LowLimit": self.LOOPPID_Alarm_LowLimit},
                                  "LOOP2PT": {"MODE0": self.LOOP2PT_MODE0,
                                              "MODE1": self.LOOP2PT_MODE1,
                                              "MODE2": self.LOOP2PT_MODE2,
                                              "MODE3": self.LOOP2PT_MODE3,
                                              "INTLKD": self.LOOP2PT_INTLKD,
                                              "MAN": self.LOOP2PT_MAN,
                                              "ERR": self.LOOP2PT_ERR,
                                              "OUT": self.LOOP2PT_OUT,
                                              "SET1": self.LOOP2PT_SET1,
                                              "SET2": self.LOOP2PT_SET2,
                                              "SET3": self.LOOP2PT_SET3,
                                              "Busy": self.LOOP2PT_Busy},
                                  "INTLK_D": {"value": self.INTLK_D_DIC,
                                              "EN": self.INTLK_D_EN,
                                              "COND": self.INTLK_D_COND,
                                              "Busy":self.INTLK_D_Busy},
                                  "INTLK_A": {"value":self.INTLK_A_DIC,
                                              "EN":self.INTLK_A_EN,
                                              "COND":self.INTLK_A_COND,
                                              "SET":self.INTLK_A_SET,
                                              "Busy":self.INTLK_A_Busy},
                                  "FLAG": {"value":self.FLAG_DIC,
                                           "INTLKD":self.FLAG_INTLKD,
                                           "Busy":self.FLAG_Busy},
                                  "Procedure": {"Running": self.Procedure_running, "INTLKD": self.Procedure_INTLKD, "EXIT": self.Procedure_EXIT}},
                         "Alarm": {"TT": {"AD1": self.TT_AD1_Alarm,"AD2": self.TT_AD2_Alarm, "LS":self.HTRTD_Alarm
                                          },
                                   "PT": self.PT_Alarm,
                                   "LEFT_REAL": self.LEFT_REAL_Alarm,
                                   "Din": self.Din_Alarm,
                                   "LOOPPID": self.LOOPPID_Alarm,
                                   "LL":self.LL_Alarm},
                         "Active": {"TT": {"AD1": self.TT_AD1_Activated,"AD2":self.TT_AD2_Activated, "LS": self.HTRTD_Activated
                                          },
                                   "PT": self.PT_Activated,
                                   "LEFT_REAL": self.LEFT_REAL_Activated,
                                    "Din": self.Din_Activated,
                                    "LOOPPID": self.LOOPPID_Activated,
                                    "LL":self.LL_Activated,
                                    "INI_CHECK": self.ini_check
                                    },
                         "MainAlarm": self.MainAlarm
                         }

        self.load_alarm_config()



    def load_alarm_config(self):
        self.alarm_config = AL.Alarm_Setting()
        self.alarm_config.read_Information()
        self.Connected_BO = self.Client_BO.connect()
        if self.Connected_BO:
            # high group
            for key in self.TT_AD1_HighLimit:
                try:
                    self.TT_AD1_HighLimit[key] = self.alarm_config.high_dic[key]
                except:
                    pass
            for key in self.TT_AD2_HighLimit:
                try:
                    self.TT_AD2_HighLimit[key] = self.alarm_config.high_dic[key]
                except:
                    pass

            for key in self.PT_HighLimit:
                try:
                    self.PT_HighLimit[key] = self.alarm_config.high_dic[key]
                except:
                    pass
            for key in self.LEFT_REAL_HighLimit:
                try:
                    self.LEFT_REAL_HighLimit[key] = self.alarm_config.high_dic[key]
                except:
                    pass

            for key in self.LOOPPID_Alarm_HighLimit:
                try:
                    # self.LOOPPID_SET_HI_LIM(address=self.LOOPPID_ADR_BASE[key],
                    #                         value=self.alarm_config.high_dic[key])
                    self.LOOPPID_Alarm_HighLimit[key] = self.alarm_config.high_dic[key]
                except:
                    pass

            for key in self.LL_HighLimit:
                try:
                    # self.LOOPPID_SET_HI_LIM(address=self.LOOPPID_ADR_BASE[key],
                    #                         value=self.alarm_config.high_dic[key])
                    self.LL_HighLimit[key] = self.alarm_config.high_dic[key]
                except:
                    pass

            for key in self.HTRTD_HighLimit:
                try:
                    # self.LOOPPID_SET_HI_LIM(address=self.LOOPPID_ADR_BASE[key],
                    #                         value=self.alarm_config.high_dic[key])
                    self.HTRTD_HighLimit[key] = self.alarm_config.high_dic[key]
                except:
                    pass

            # low group

            for key in self.TT_AD1_LowLimit:
                try:
                    self.TT_AD1_LowLimit[key] = self.alarm_config.low_dic[key]
                except:
                    pass
            for key in self.TT_AD2_LowLimit:
                try:
                    self.TT_AD2_LowLimit[key] = self.alarm_config.low_dic[key]
                except:
                    pass

            for key in self.PT_LowLimit:
                try:
                    self.PT_LowLimit[key] = self.alarm_config.low_dic[key]
                except:
                    pass
            for key in self.LEFT_REAL_LowLimit:
                try:
                    self.LEFT_REAL_LowLimit[key] = self.alarm_config.low_dic[key]
                except:
                    pass

            for key in self.LOOPPID_Alarm_LowLimit:
                # self.LOOPPID_SET_LO_LIM(address=self.LOOPPID_ADR_BASE[key],
                #                         value=self.alarm_config.low_dic[key])
                try:
                    self.LOOPPID_Alarm_LowLimit[key] = self.alarm_config.low_dic[key]
                except:
                    pass

            for key in self.LL_LowLimit:
                try:
                    # self.LOOPPID_SET_HI_LIM(address=self.LOOPPID_ADR_BASE[key],
                    #                         value=self.alarm_config.high_dic[key])
                    self.LL_LowLimit[key] = self.alarm_config.high_dic[key]
                except:
                    pass

            for key in self.HTRTD_LowLimit:
                try:
                    # self.LOOPPID_SET_HI_LIM(address=self.LOOPPID_ADR_BASE[key],
                    #                         value=self.alarm_config.high_dic[key])
                    self.HTRTD_LowLimit[key] = self.alarm_config.high_dic[key]
                except:
                    pass

            # activated group
            for key in self.TT_AD1_Activated:
                try:
                    self.TT_AD1_Activated[key] = self.alarm_config.active_dic[key]
                except:
                    pass
            for key in self.TT_AD2_Activated:
                try:
                    self.TT_AD2_Activated[key] = self.alarm_config.active_dic[key]
                except:
                    pass

            for key in self.PT_Activated:
                try:
                    self.PT_Activated[key] = self.alarm_config.active_dic[key]
                except:
                    pass

            for key in self.LL_Activated:
                try:
                    self.LL_Activated[key] = self.alarm_config.active_dic[key]
                except:
                    pass

            for key in self.LOOPPID_Activated:
                try:
                    self.LOOPPID_Activated[key] = self.alarm_config.active_dic[key]
                except:
                    pass

            for key in self.HTRTD_Activated:
                try:
                    self.HTRTD_Activated[key] = self.alarm_config.active_dic[key]
                except:
                    pass
        # after the initilaztion, set the flag as true so that GUI can start load this config
        with self.plc_lock:
            self.data_dic["Active"]["INI_CHECK"] = True
            self.plc_data.update(self.data_dic)



    def _connect_fdc1004(self):
        """Opens the serial port, applies config.json, starts streaming,
        and discards the warmup samples. Returns True/False; used both at
        __init__ (initial connect) and by ReadFDC1004() (reconnect)."""
        try:
            self.fdc_ser = serial.Serial(fdc.PORT, fdc.BAUD, timeout=1)
            capdac_offsets = fdc.start_stream(self.fdc_ser)
            self.fdc_reader = fdc.StreamReader(self.fdc_ser, capdac_offsets)
            discarded = 0
            while discarded < fdc.WARMUP_SAMPLES:
                if self.fdc_reader.read_sample() is not None:
                    discarded += 1
            self.fdc_channel_samples = [[], [], [], []]
            self.fdc_interval_start = time.time()
            return True
        except Exception as e:
            print("FDC1004 connect failed:", repr(e))
            return False

    def ReadFDC1004(self):
        """
        Non-blocking per-cycle FDC1004 read. Unlike UpdatePLC's other
        sensors (one modbus round-trip per cycle), the FDC1004 streams
        continuously and only produces an average every
        fdc.AVERAGING_INTERVAL_S seconds — so this drains whatever samples
        are CURRENTLY buffered (bounded by the port's short timeout, not by
        the averaging interval) and only writes into CAP_dic once a full
        interval's worth has accumulated. This keeps ReadAll()'s ~1s cycle
        from ever blocking for the multi-second averaging window.
        """
        if not self.Connected_FDC1004:
            self.Connected_FDC1004 = self._connect_fdc1004()
            if self.Connected_FDC1004:
                print("FDC1004 Reconnected")
            else:
                print("FDC1004 Reconnect failed, trying again")
                with self.alarm_lock:
                    if self.module_connection_alarm.get('FDC1004', True):
                        self.alarm_stack.update({"FDC1004 disconnection alarm": "FDC1004 is disconnected. Restarting..."})
            return

        try:
            while True:
                sample = self.fdc_reader.read_sample()
                if sample is None:
                    break
                for ch in range(4):
                    self.fdc_channel_samples[ch].append(sample[ch])

            if time.time() - self.fdc_interval_start >= fdc.AVERAGING_INTERVAL_S and self.fdc_channel_samples[0]:
                means = [statistics.mean(v) for v in self.fdc_channel_samples]
                for ch in range(4):
                    name = fdc.SLOWCONTROL_INSTRUMENT_NAMES[ch + 1]
                    self.CAP_dic[name] = means[ch]
                self.fdc_channel_samples = [[], [], [], []]
                self.fdc_interval_start = time.time()
        except Exception as e:
            print("Exception reading FDC1004", e)
            try:
                self.fdc_ser.close()
            except Exception:
                pass
            self.Connected_FDC1004 = False
            with self.alarm_lock:
                self.alarm_stack.update({"FDC1004 Exception": "FDC1004 read error. Reconnecting..."})

    def ReadAll(self):


        #########################################################################
        if not self.Client_BO.is_socket_open():
            try:
                self.Client_BO.connect()
                print("BO Reconnected")
            except Exception as e:
                print("BO Reconnect failed, trying again")
                # Wait for 5 seconds before retrying
            finally:
                self.Read_BO_empty()
                with self.alarm_lock:
                    if self.module_connection_alarm['Beckhoff']:
                        self.alarm_stack.update({"BO disconnection alarm":"Beckhoff modbus is disconnected. Restarting..."})
        else:
            try:
                self.Read_BO()
            except Exception as e:
                pass

        if not self.Client_AD1.is_socket_open() and self.Client_AD2.is_socket_open():
            try:
                self.Client_AD1.connect()
                self.Client_AD2.connect()
                print("AD Reconnected")
            except Exception as e:
                print("AD1 and AD2 Reconnect failed, trying again")
                # Wait for 5 seconds before retrying
            finally:
                self.Read_AD_empty()
                with self.alarm_lock:
                    if self.module_connection_alarm['AD1'] and self.module_connection_alarm['AD2']:
                        self.alarm_stack.update({"Adam disconnection alarm":"Adam modbus is disconnected. Restarting..."})
        else:
            try:
                self.Read_AD()
            except Exception as e:
                pass

        if not self.is_LS_connected():
            try:
                self.Client_LS1 = Model336(serial_number=self.IP_LS1)
                self.Client_LS2 = Model336(serial_number=self.IP_LS2)
                print("LS Reconnected")
            except Exception as e:
                print("LS1 and LS2 Reconnect failed, trying again")
                # Wait for 5 seconds before retrying
            finally:
                self.Read_LS_empty()
                with self.alarm_lock:
                    if self.module_connection_alarm['LS']:
                        self.alarm_stack.update({"Lakeshore disconnection alarm":"Lakeshore modbus is disconnected. Restarting..."})
        else:
            try:
                self.Read_LS()
            except Exception as e:
                pass
        print(self.is_LL_connected())
        if not self.is_LL_connected():
            try:
                self.socket_LL = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_LL.connect((self.IP_LL, self.PORT_LL))
                print("LL Reconnected")
            except Exception as e:
                print("LL Reconnect failed, trying again")
                # Wait for 5 seconds before retrying
            finally:
                self.Read_LL_empty()
                with self.alarm_lock:
                    if self.module_connection_alarm['LL']:
                        self.alarm_stack.update({"LL disconnection alarm":"Liquid leveler modbus is disconnected. Restarting..."})
        else:
            try:
                self.Read_LL()
            except Exception as e:
                pass

        self.ReadFDC1004()

        with self.plc_lock:
            self.plc_data.update(self.data_dic)



            #########################################################################################################



        return 0


    def is_LS_connected(self):
        try:
            self.Client_LS1.query("*IDN?")
            self.Client_LS2.query("*IDN?")
            return True
        except:
            return False


    def Read_BO(self):
        if self.Connected_BO:

            Raw_BO_PT = {}
            for key in self.PT_address:
                Raw_BO_PT[key] = self.Client_BO.read_holding_registers(self.PT_address[key], count=2, unit=0x01)
                self.PT_dic[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_BO_PT[key].getRegister(0 + 1),
                                                    Raw_BO_PT[key].getRegister(0)))[0], 3)

            Raw_BO_REAL = {}
            for key in self.LEFT_REAL_address:
                if key!="SV0001_TIME":
                    Raw_BO_REAL[key] = self.Client_BO.read_holding_registers(self.LEFT_REAL_address[key], count=2,
                                                                             unit=0x01)
                    self.LEFT_REAL_dic[key] = round(
                        struct.unpack(">f", struct.pack(">HH", Raw_BO_REAL[key].getRegister(0 + 1),
                                                        Raw_BO_REAL[key].getRegister(0)))[0], 5)
                elif key == "SV0001_TIME":
                    Raw_BO_REAL[key] = self.Client_BO.read_holding_registers(self.LEFT_REAL_address[key], count=2,
                                                                             unit=0x01)
                    self.LEFT_REAL_dic[key] = struct.unpack(">I", struct.pack(">HH", Raw_BO_REAL[key].getRegister(0 + 1),
                                                        Raw_BO_REAL[key].getRegister(0)))[0]/1000

                # TIME finally is in seconds



            Raw_BO_Valve = {}
            Raw_BO_Valve_OUT = {}
            for key in self.valve_address:
                Raw_BO_Valve[key] = self.Client_BO.read_holding_registers(self.valve_address[key], count=1, unit=0x01)
                self.Valve[key] = struct.pack("H", Raw_BO_Valve[key].getRegister(0))
                if key in self.valve_invert_list:
                    self.Valve_OUT[key] = not self.ReadCoil(1, self.valve_address[key])
                else:
                    self.Valve_OUT[key] = self.ReadCoil(1, self.valve_address[key])
                self.Valve_Busy[key] = self.ReadCoil(2, self.valve_address[key]) or self.ReadCoil(4, self.valve_address[
                    key])
                self.Valve_INTLKD[key] = self.ReadCoil(8, self.valve_address[key])
                self.Valve_MAN[key] = self.ReadCoil(16, self.valve_address[key])
                self.Valve_ERR[key] = self.ReadCoil(32, self.valve_address[key])

            Raw_BO_Din = {}
            for key in self.Din_address:
                Raw_BO_Din[key] = self.Client_BO.read_holding_registers(self.Din_address[key][0], count=1, unit=0x01)
                # print(Raw_BO_Din[key])
                self.Din[key] = struct.pack("H", Raw_BO_Din[key].getRegister(0))

                self.Din_dic[key] = self.ReadCoil(2 ** (self.Din_address[key][1]), self.Din_address[key][0])



    def Read_BO_empty(self):

        for key in self.PT_address:
            self.PT_dic[key] = 0

        for key in self.LEFT_REAL_address:
            self.LEFT_REAL_dic[key] = 0


        for key in self.valve_address:

            self.Valve_OUT[key] = 0
            self.Valve_Busy[key] = 0
            self.Valve_INTLKD[key] = 0
            self.Valve_MAN[key] = 0
            self.Valve_ERR[key] = 0


    def Read_AD(self):

        Raw_RTDs_AD1 = {}
        Raw_RTDs_AD2 = {}

        for key in self.TT_AD1_address:
            bias = self.TT_AD1_cali[key]
            Raw_RTDs_AD1[key] = self.Client_AD1.read_holding_registers(self.TT_AD1_address[key], count=1, unit=0x01)
            # also transform C into K if value is not NULL
            # read_value = round(struct.unpack("<f", struct.pack("<HH", Raw_RTDs_AD1[key].getRegister(1), Raw_RTDs_AD1[key].getRegister(0)))[0], 3)
            read_value = -200 + 400 * Raw_RTDs_AD1[key].getRegister(0) / 2 ** 16
            # print(key, read_value)
            if read_value < 201:

                self.TT_AD1_dic[key] = round(273.15 + read_value + bias, 2)
            else:
                self.TT_AD1_dic[key] = round(read_value + bias, 2)

        for key in self.TT_AD2_address:
            Raw_RTDs_AD2[key] = self.Client_AD2.read_holding_registers(self.TT_AD2_address[key], count=1, unit=0x01)
            # also transform C into K if value is not NULL
            # read_value = round(struct.unpack("<f", struct.pack("<HH", Raw_RTDs_AD2[key].getRegister(1), Raw_RTDs_AD2[key].getRegister(0)))[0], 3)
            read_value = -200 + 400 * Raw_RTDs_AD2[key].getRegister(0) / 2 ** 16
            if read_value < 201:

                self.TT_AD2_dic[key] = round(273.15 + read_value, 2)
            else:
                self.TT_AD2_dic[key] = round(read_value, 2)


    def Read_AD_empty(self):
        for key in self.TT_AD1_address:
            self.TT_AD1_dic[key] = -1
        for key in self.TT_AD2_address:
            self.TT_AD2_dic[key] = -1

    def Read_LS(self):
        #LS1 should be unaffected if LS2 lost connection
        Raw_LS_power = {}
        Raw_LS_TT = {}
        self.LS_timeout  = 5


        for key in self.LOOPPID_ADR_BASE:
            # time.sleep(0.1)
            command_base = "HTR?"
            command_base_alter = "RELAYST?"
            command_middle=str(self.LOOPPID_ADR_BASE[key][1]+1)
            command_middle_alter=str(self.LOOPPID_ADR_BASE[key][1]-1)
            if self.LOOPPID_ADR_BASE[key][1] <= 1:
                command0 = command_base + command_middle
                command1 = command_base +" "+ command_middle
            else:
                command0 = command_base_alter + command_middle_alter
                command1 = command_base_alter + " " + command_middle_alter
            if self.LOOPPID_ADR_BASE[key][0]==0:
                # print("connection success!", key)
                try:
                    if self.LOOPPID_ADR_BASE[key][1] <= 1:

                        Raw_LS_power[key] = float(LS_OUT_translate(self.Client_LS1.query(command0)))
                    else:
                        Raw_LS_power[key] = float(LS_OUT_translate(self.Client_LS1.query(command0)))*100

                except:
                    Raw_LS_power[key] = -1

            if self.LOOPPID_ADR_BASE[key][0]==1:
                try:
                    if self.LOOPPID_ADR_BASE[key][1] <= 1:
                        Raw_LS_power[key] = float(LS_OUT_translate(self.Client_LS2.query(command1)))
                    else:
                        Raw_LS_power[key] = float(LS_OUT_translate(self.Client_LS2.query(command1)))*100
                except:
                    Raw_LS_power[key] = -1

        # print("OUTPUT POWER",Raw_LS_power)
        for key in self.LOOPPID_ADR_BASE:
            try:
                stripped = Raw_LS_power[key].strip("+")
            except:
                stripped = Raw_LS_power[key]
            self.LOOPPID_OUT[key] = float(stripped)
        # print("HTR OUT",self.LOOPPID_OUT)
        for key in self.LOOPPID_ADR_BASE:
            if float(self.LOOPPID_OUT[key])>0:
                self.LOOPPID_EN[key] = True
            else:
                self.LOOPPID_EN[key] = False


        #RTD read is all pulled out once (1,2,3,4), so we can read the tuple first and give it to Raw_dic
        # this reduces the times we communicates with the LS server by a factor of 4
        # too many communications in a short of time can cause LS server to crash
        command_base = "KRDG?"
        # command_middle=str(self.LOOPPID_ADR_BASE[key][1])
        command_middle = "0"
        command0 = command_base + command_middle
        command1 = command_base + "0"+command_middle

        try:
            output_tuple = LS_TT_translate(self.Client_LS1.query(command0))

            for key in self.HTRTD_address:
                if self.HTRTD_address[key][0] == 0:
                    Raw_LS_TT[key] = output_tuple[
                        2 * self.HTRTD_address[key][1] + self.HTRTD_address[key][2]]

        except:
            for key in self.HTRTD_address:
                if self.HTRTD_address[key][0] == 0:
                    Raw_LS_TT[key] = -1

        try:
            output_tuple = LS_TT_translate(self.Client_LS2.query(command1))
            for key in self.HTRTD_address:
                if self.HTRTD_address[key][0] == 1:

                    Raw_LS_TT[key] = output_tuple[2*self.HTRTD_address[key][1]+self.HTRTD_address[key][2]]

        except:
            for key in self.HTRTD_address:
                if self.HTRTD_address[key][0] == 1:
                    Raw_LS_TT[key] = -1

        for key in self.HTRTD_address:
            self.HTRTD_dic[key] = Raw_LS_TT[key]
        # print("HTR RTDs",self.HTRTD_dic)

    def Read_LS_empty(self):
        for key in self.LOOPPID_ADR_BASE:

            self.LOOPPID_OUT[key] = -1
        for key in self.LOOPPID_ADR_BASE:
            self.LOOPPID_EN[key] = False

        for key in self.HTRTD_address:
            self.HTRTD_dic[key] = -1


    def Read_LL(self):

        for key in self.LL_address:
            # self.socket_LL.settimeout(1)
            if self.LL_address[key][1]==0:
                commandN2 = "MEASure:N2:LEVel?\n"
            elif self.LL_address[key][1]==1:
                commandN2 = "MEASure:N2:PERIod?\n"

            # commandN2 = "*IDN?\n"
            cm_codeN2 = commandN2.encode()
            self.socket_LL.send(cm_codeN2)
            dataN2 = self.socket_LL.recv(self.BUFFER_SIZE)
            value = dataN2.decode()
            trimed_value = value.replace("\r\n", "")
            if self.LL_address[key][1]==0:
                self.LL_dic[key] = float(trimed_value) + 0.521
            elif self.LL_address[key][1]==1:
                self.LL_dic[key] = float(trimed_value)

            # offset of leveler sensro in cm =0.521 inch

            # commandHE = "MEASure:HE:LEVel?\n"
            # print("command", commandHE)
            # cm_codeHE = commandHE.encode()
            # self.socket_LL.send(cm_codeHE)
            # dataHE = self.socket_LL.recv(self.BUFFER_SIZE)
            #
            # print("fetched data HE", dataHE.decode())
            # self.LL_updatesignal = True
            # self.socket_LL.close()

        # print(self.LL_dic)
    def Read_LL_empty(self):
        for key in self.LL_address:
            self.LL_dic[key] = 0

    def is_LL_connected(self):
        try:
            commandN2 = "*IDN?\n"
            cm_codeN2 = commandN2.encode()
            self.socket_LL.send(cm_codeN2)
            dataN2 = self.socket_LL.recv(self.BUFFER_SIZE)
            return True
        except:
            return False


    def write_data(self, received_dict):
        message = received_dict
        # print("write data in plc module",message)
        if not "MAN_SET" in message:
            if message == {}:
                pass
            else:
                for key in message:

                    if message[key]["type"] == "valve":
                        # print("Valve", datetime_in_1e5micro())
                        if message[key]["operation"] == "OPEN":
                            self.WriteBase2(address=message[key]["address"])
                        elif message[key]["operation"] == "CLOSE":
                            self.WriteBase4(address=message[key]["address"])
                        else:
                            pass
                    if message[key]["type"] == "TRIG":
                        print(message)
                        if message[key]["operation"] == "MAN":
                            self.trigcoil(address=message[key]["address"][0], digit=message[key]["address"][1])
                        elif message[key]["operation"] == "RESET":
                            self.trigcoil(address=message[key]["address"][0], digit=message[key]["address"][1])
                        else:
                            pass

                        # write success signal


                    elif message[key]["type"] == "TT":

                        if message[key]["server"] == "AD1":
                            if message[key]["operation"]["Update"]:
                                self.TT_AD1_Activated[key] = message[key]["operation"]["Act"]
                                self.TT_AD1_LowLimit[key] = message[key]["operation"]["LowLimit"]
                                self.TT_AD1_HighLimit[key] = message[key]["operation"]["HighLimit"]
                            else:
                                self.TT_AD1_Activated[key] = message[key]["operation"]["Act"]
                        elif message[key]["server"] == "AD2":
                            if message[key]["operation"]["Update"]:
                                self.TT_AD2_Activated[key] = message[key]["operation"]["Act"]
                                self.TT_AD2_LowLimit[key] = message[key]["operation"]["LowLimit"]
                                self.TT_AD2_HighLimit[key] = message[key]["operation"]["HighLimit"]
                            else:
                                self.TT_AD2_Activated[key] = message[key]["operation"]["Act"]

                        elif message[key]["server"] == "LS":
                            if message[key]["operation"]["Update"]:
                                self.HTRTD_Activated[key] = message[key]["operation"]["Act"]
                                self.HTRTD_LowLimit[key] = message[key]["operation"]["LowLimit"]
                                self.HTRTD_HighLimit[key] = message[key]["operation"]["HighLimit"]
                            else:
                                self.HTRTD_Activated[key] = message[key]["operation"]["Act"]
                        else:
                            pass

                    elif message[key]["type"] == "PT":
                        if message[key]["server"] == "BO":
                            if message[key]["operation"]["Update"]:
                                self.PT_Activated[key] = message[key]["operation"]["Act"]
                                self.PT_LowLimit[key] = message[key]["operation"]["LowLimit"]
                                self.PT_HighLimit[key] = message[key]["operation"]["HighLimit"]
                            else:
                                self.PT_Activated[key] = message[key]["operation"]["Act"]
                        else:
                            pass
                    elif message[key]["type"] == "PTSET":
                        if message[key]["server"] == "BO":
                            if message[key]["operation"]["Update"]:

                                self.Write_BO_2(message[key]["address"],float(message[key]["operation"]["HighLimit"]))

                        else:
                            pass
                    elif message[key]["type"] == "LEFT":
                        if message[key]["server"] == "BO":
                            if message[key]["operation"]["Update"]:
                                self.LEFT_REAL_Activated[key] = message[key]["operation"]["Act"]
                                self.LEFT_REAL_LowLimit[key] = message[key]["operation"]["LowLimit"]
                                self.LEFT_REAL_HighLimit[key] = message[key]["operation"]["HighLimit"]

                            else:
                                self.LEFT_REAL_Activated[key] = message[key]["operation"]["Act"]
                        else:
                            pass
                    elif message[key]["type"] == "LL":
                        if message[key]["server"] == "LL":
                            if message[key]["operation"]["Update"]:
                                self.LL_Activated[key] = message[key]["operation"]["Act"]
                                self.LL_LowLimit[key] = message[key]["operation"]["LowLimit"]
                                self.LL_HighLimit[key] = message[key]["operation"]["HighLimit"]
                            else:
                                self.LL_Activated[key] = message[key]["operation"]["Act"]
                        else:
                            pass

                    elif message[key]["type"] == "Din":
                        if message[key]["server"] == "BO":
                            if message[key]["operation"]["Update"]:
                                self.Din_Activated[key] = message[key]["operation"]["Act"]
                                self.Din_LowLimit[key] = message[key]["operation"]["LowLimit"]
                                self.Din_HighLimit[key] = message[key]["operation"]["HighLimit"]
                            else:
                                self.Din_Activated[key] = message[key]["operation"]["Act"]
                        else:
                            pass


                    elif message[key]["type"] == "LOOPPID_alarm":
                        if message[key]["server"] == "LS":
                            if message[key]["operation"]["Update"]:
                                self.LOOPPID_Activated[key] = message[key]["operation"]["Act"]
                                # self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
                                #                             value=message[key]["operation"]["LowLimit"])
                                # self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
                                #                             value=message[key]["operation"]["HighLimit"])
                                self.LOOPPID_Alarm_HighLimit[key] = message[key]["operation"]["HighLimit"]
                                self.LOOPPID_Alarm_LowLimit[key] = message[key]["operation"]["LowLimit"]
                                # time.sleep(1)
                                # print(self.LOOPPID_Activated[key],self.LOOPPID_Alarm_HighLimit[key],self.LOOPPID_Alarm_LowLimit[key])


                            else:
                                self.LOOPPID_Activated[key] = message[key]["operation"]["Act"]
                        else:
                            pass

                    elif message[key]["type"] == "Procedure":
                        if message[key]["server"] == "BO":
                            if message[key]["operation"]["Start"]:
                                self.WriteBase4(address=message[key]["address"])
                            elif message[key]["operation"]["Stop"]:
                                self.WriteBase8(address=message[key]["address"])
                            elif message[key]["operation"]["Abort"]:
                                self.WriteBase16(address=message[key]["address"])
                            else:
                                pass
                        else:
                            pass

                    elif message[key]["type"] == "Procedure_TS":
                        if message[key]["server"] == "BO":
                            if message[key]["operation"]["RST_FF"]:
                                self.WriteFF(self.FF_ADDRESS["TS_ADDREM_FF"])
                            if message[key]["operation"]["update"]:
                                self.Write_BO_2_int16(self.PARAM_I_ADDRESS["TS_SEL"],
                                                          message[key]["operation"]["SEL"])
                                self.Write_BO_2(self.PARAM_F_ADDRESS["TS_ADDREM_MASS"],
                                                    message[key]["operation"]["ADDREM_MASS"])
                                self.Write_BO_2_int32(self.PARAM_T_ADDRESS["TS_ADDREM_MAXTIME"],
                                                          round(float(message[key]["operation"]["MAXTIME"]) * 1000))

                            else:
                                pass
                        else:
                            pass

                    elif message[key]["type"] == "Procedure_PC":
                        if message[key]["server"] == "BO":
                            if message[key]["operation"]["ABORT_FF"]:
                                self.WriteFF(self.FF_ADDRESS["PCYCLE_ABORT_FF"])
                            if message[key]["operation"]["FASTCOMP_FF"]:
                                self.WriteFF(self.FF_ADDRESS["PCYCLE_FASTCOMP_FF"])
                            if message[key]["operation"]["SLOWCOMP_FF"]:
                                self.WriteFF(self.FF_ADDRESS["PCYCLE_SLOWCOMP_FF"])
                            if message[key]["operation"]["CYLEQ_FF"]:
                                self.WriteFF(self.FF_ADDRESS["PCYCLE_CYLEQ_FF"])
                            if message[key]["operation"]["ACCHARGE_FF"]:
                                self.WriteFF(self.FF_ADDRESS["PCYCLE_ACCHARGE_FF"])
                            if message[key]["operation"]["CYLBLEED_FF"]:
                                self.WriteFF(self.FF_ADDRESS["PCYCLE_CYLBLEED_FF"])

                            if message[key]["operation"]["update"]:
                                self.Write_BO_2(self.PARAM_F_ADDRESS["PSET"], message[key]["operation"]["PSET"])
                                self.Write_BO_2_int32(self.PARAM_T_ADDRESS["MAXEXPTIME"],
                                                          round(float(message[key]["operation"]["MAXEXPTIME"]) * 1000))
                                self.Write_BO_2_int32(self.PARAM_T_ADDRESS["MAXEQTIME"],
                                                          round(float(message[key]["operation"]["MAXEXQTIME"]) * 1000))
                                self.Write_BO_2(self.PARAM_F_ADDRESS["MAXEQPDIFF"],
                                                    message[key]["operation"]["MAXEQPDIFF"])
                                self.Write_BO_2_int32(self.PARAM_T_ADDRESS["MAXACCTIME"],
                                                          round(float(message[key]["operation"]["MAXACCTIME"]) * 1000))
                                self.Write_BO_2(self.PARAM_F_ADDRESS["MAXACCDPDT"],
                                                    message[key]["operation"]["MAXACCDPDT"])

                                self.Write_BO_2_int32(self.PARAM_T_ADDRESS["MAXBLEEDTIME"],
                                                          round(
                                                              float(message[key]["operation"]["MAXBLEEDTIME"]) * 1000))
                                self.Write_BO_2(self.PARAM_F_ADDRESS["MAXBLEEDDPDT"],
                                                    message[key]["operation"]["MAXBLEEDDPDT"])
                                self.Write_BO_2(self.PARAM_F_ADDRESS["SLOWCOMP_SET"],
                                                    message[key]["operation"]["SLOWCOMP_SET"])

                            else:
                                pass
                        else:
                            pass


                    elif message[key]["type"] == "heater_power":
                        if message[key]["operation"] == "EN":
                            self.LOOPPID_OUT_ENA(address=message[key]["address"])
                        elif message[key]["operation"] == "DISEN":
                            self.LOOPPID_OUT_DIS(address=message[key]["address"])
                        else:
                            pass

                    elif message[key]["type"] == "heater_para":
                        if message[key]["operation"] == "SET0":
                            # self.LOOPPID_SET_MODE(address=message[key]["address"], mode= 0)
                            self.LOOPPID_SETPOINT(address=message[key]["address"],
                                                      setpoint=message[key]["value"]["SETPOINT"], mode=0)
                            # self.LOOPPID_HI_LIM(address=message[key]["address"], value=message[key]["value"]["HI_LIM"])
                            # self.LOOPPID_LO_LIM(address=message[key]["address"], value=message[key]["value"]["LO_LIM"])
                            self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
                                                        value=message[key]["value"]["HI_LIM"])
                            self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
                                                        value=message[key]["value"]["LO_LIM"])

                        elif message[key]["operation"] == "SET1":
                            # self.LOOPPID_SET_MODE(address=message[key]["address"], mode=1)
                            self.LOOPPID_SETPOINT(address=message[key]["address"],
                                                      setpoint=message[key]["value"]["SETPOINT"], mode=1)
                            self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
                                                        value=message[key]["value"]["HI_LIM"])
                            self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
                                                        value=message[key]["value"]["LO_LIM"])
                        elif message[key]["operation"] == "SET2":
                            # self.LOOPPID_SET_MODE(address=message[key]["address"], mode=2)
                            self.LOOPPID_SETPOINT(address=message[key]["address"],
                                                      setpoint=message[key]["value"]["SETPOINT"], mode=2)
                            self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
                                                        value=message[key]["value"]["HI_LIM"])
                            self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
                                                        value=message[key]["value"]["LO_LIM"])
                        elif message[key]["operation"] == "SET3":
                            # self.LOOPPID_SET_MODE(address=message[key]["address"], mode=3)
                            self.LOOPPID_SETPOINT(address=message[key]["address"],
                                                      setpoint=message[key]["value"]["SETPOINT"], mode=3)
                            self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
                                                        value=message[key]["value"]["HI_LIM"])
                            self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
                                                        value=message[key]["value"]["LO_LIM"])
                        else:
                            pass

                    elif message[key]["type"] == "heater_setmode":
                        if message[key]["operation"] == "SET0":
                            self.LOOPPID_SET_MODE(address=message[key]["address"], mode=0)

                        elif message[key]["operation"] == "SET1":
                            # print(True)
                            self.LOOPPID_SET_MODE(address=message[key]["address"], mode=1)

                        elif message[key]["operation"] == "SET2":
                            self.LOOPPID_SET_MODE(address=message[key]["address"], mode=2)

                        elif message[key]["operation"] == "SET3":
                            self.LOOPPID_SET_MODE(address=message[key]["address"], mode=3)

                        else:
                            pass

                        # if message[key]["operation"] == "HI_LIM":
                        #     self.LOOPPID_HI_LIM(address= message[key]["address"], value = message[key]["value"])
                        # else:
                        #     pass
                        #
                        # if message[key]["operation"] == "LO_LIM":
                        #     self.LOOPPID_HI_LIM(address= message[key]["address"], value = message[key]["value"])

                    elif message[key]["type"] == "LOOP2PT_power":
                        # print("PUMP", datetime_in_1e5micro())
                        if message[key]["operation"] == "OPEN":
                            self.LOOP2PT_OPEN(address=message[key]["address"])
                        elif message[key]["operation"] == "CLOSE":
                            self.LOOP2PT_CLOSE(address=message[key]["address"])
                        else:
                            pass

                    elif message[key]["type"] == "LOOP2PT_para":

                        if message[key]["operation"] == "SET1":
                            # self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=1)
                            self.LOOP2PT_SETPOINT(address=message[key]["address"],
                                                      setpoint=message[key]["value"]["SETPOINT"], mode=1)

                        elif message[key]["operation"] == "SET2":
                            # self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=2)
                            self.LOOP2PT_SETPOINT(address=message[key]["address"],
                                                      setpoint=message[key]["value"]["SETPOINT"], mode=2)

                        elif message[key]["operation"] == "SET3":
                            # self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=3)
                            self.LOOP2PT_SETPOINT(address=message[key]["address"],
                                                      setpoint=message[key]["value"]["SETPOINT"], mode=3)
                        else:
                            pass

                    elif message[key]["type"] == "LOOP2PT_setmode":
                        if message[key]["operation"] == "SET0":
                            self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=0)

                        elif message[key]["operation"] == "SET1":
                            self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=1)

                        elif message[key]["operation"] == "SET2":
                            self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=2)

                        elif message[key]["operation"] == "SET3":
                            self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=3)

                        else:
                            pass
                    elif message[key]["type"] == "INTLK_A":
                        if message[key]["server"] == "BO":
                            if message[key]["operation"] == "ON":
                                self.WriteBase8(address=message[key]["address"])
                            elif message[key]["operation"] == "OFF":
                                self.WriteBase16(address=message[key]["address"])
                            elif message[key]["operation"] == "RESET":
                                self.WriteBase32(address=message[key]["address"])
                            elif message[key]["operation"] == "update":
                                self.Write_BO_2(message[key]["address"] + 2, message[key]["value"])
                            else:
                                pass
                    elif message[key]["type"] == "INTLK_D":
                        if message[key]["server"] == "BO":
                            if message[key]["operation"] == "ON":
                                self.WriteBase8(address=message[key]["address"])
                            elif message[key]["operation"] == "OFF":
                                self.WriteBase16(address=message[key]["address"])
                            elif message[key]["operation"] == "RESET":
                                self.WriteBase32(address=message[key]["address"])
                            else:
                                pass
                    elif message[key]["type"] == "FLAG":
                        print("time", datetime.datetime.now())
                        if message[key]["operation"] == "OPEN":
                            self.WriteBase2(address=message[key]["address"])
                        elif message[key]["operation"] == "CLOSE":
                            self.WriteBase4(address=message[key]["address"])
                        else:
                            pass

                    else:
                        pass

            # if message == b'this is a command':
            #     self.WriteBase2()
            #     self.Read_BO_1()
            #     print("I will set valve")
            # elif message == b'no command':
            #     self.WriteBase4()
            #     self.Read_BO_1()
            #     print("I will stay here")
            # elif message == b'this an anti_conmmand':
            #
            #     print("reset the valve")
            # else:
            #     print("I didn't see any command")
            #     pass
        elif "MAN_SET" in message:
            # manuall set the configuration

            for key in message["MAN_SET"]["data"]["TT"]["AD1"]["high"]:
                self.TT_AD1_HighLimit[key] = message["MAN_SET"]["data"]["TT"]["AD1"]["high"][key]
            for key in message["MAN_SET"]["data"]["TT"]["AD2"]["high"]:
                self.TT_AD2_HighLimit[key] = message["MAN_SET"]["data"]["TT"]["AD2"]["high"][key]
            for key in message["MAN_SET"]["data"]["TT"]["LS"]["high"]:
                self.HTRTD_HighLimit[key] = message["MAN_SET"]["data"]["TT"]["LS"]["high"][key]

            for key in message["MAN_SET"]["data"]["PT"]["high"]:
                self.PT_HighLimit[key] = message["MAN_SET"]["data"]["PT"]["high"][key]

            for key in message["MAN_SET"]["data"]["LEFT_REAL"]["high"]:
                self.LEFT_REAL_HighLimit[key] = message["MAN_SET"]["data"]["LEFT_REAL"]["high"][key]

            for key in message["MAN_SET"]["data"]["Din"]["high"]:
                self.Din_HighLimit[key] = message["MAN_SET"]["data"]["Din"]["high"][key]

            for key in message["MAN_SET"]["data"]["LOOPPID"]["Alarm_HighLimit"]:
                self.LOOPPID_Alarm_HighLimit[key] = message["MAN_SET"]["data"]["LOOPPID"]["Alarm_HighLimit"][key]

            for key in message["MAN_SET"]["data"]["TT"]["AD1"]["low"]:
                self.TT_AD1_LowLimit[key] = message["MAN_SET"]["data"]["TT"]["AD1"]["low"][key]
            for key in message["MAN_SET"]["data"]["TT"]["AD2"]["low"]:
                self.TT_AD2_LowLimit[key] = message["MAN_SET"]["data"]["TT"]["AD2"]["low"][key]
            for key in message["MAN_SET"]["data"]["TT"]["LS"]["low"]:
                self.HTRTD_LowLimit[key] = message["MAN_SET"]["data"]["TT"]["LS"]["low"][key]

            for key in message["MAN_SET"]["data"]["PT"]["low"]:
                self.PT_LowLimit[key] = message["MAN_SET"]["data"]["PT"]["low"][key]

            for key in message["MAN_SET"]["data"]["LEFT_REAL"]["low"]:
                self.LEFT_REAL_LowLimit[key] = message["MAN_SET"]["data"]["LEFT_REAL"]["low"][key]

            for key in message["MAN_SET"]["data"]["Din"]["low"]:
                self.Din_LowLimit[key] = message["MAN_SET"]["data"]["Din"]["low"][key]

            for key in message["MAN_SET"]["data"]["LOOPPID"]["Alarm_LowLimit"]:
                self.LOOPPID_Alarm_LowLimit[key] = message["MAN_SET"]["data"]["LOOPPID"]["Alarm_LowLimit"][key]

            for key in message["MAN_SET"]["Active"]["TT"]["AD1"]:
                self.TT_AD1_Activated[key] = message["MAN_SET"]["Active"]["TT"]["AD1"][key]
            for key in message["MAN_SET"]["Active"]["TT"]["AD2"]:
                self.TT_AD2_Activated[key] = message["MAN_SET"]["Active"]["TT"]["AD2"][key]
            for key in message["MAN_SET"]["Active"]["TT"]["LS"]:
                self.HTRTD_Activated[key] = message["MAN_SET"]["Active"]["TT"]["LS"][key]

            for key in message["MAN_SET"]["Active"]["PT"]:
                self.PT_Activated[key] = message["MAN_SET"]["Active"]["PT"][key]

            for key in message["MAN_SET"]["Active"]["LEFT_REAL"]:
                self.LEFT_REAL_Activated[key] = message["MAN_SET"]["Active"]["LEFT_REAL"][key]

            for key in message["MAN_SET"]["Active"]["Din"]:
                self.Din_Activated[key] = message["MAN_SET"]["Active"]["Din"][key]

            for key in message["MAN_SET"]["Active"]["LOOPPID"]:
                self.LOOPPID_Activated[key] = message["MAN_SET"]["Active"]["LOOPPID"][key]


        else:
            print(
                "Failed to load data from Client. MAN_SET is not either in or not in the received directory. Please check the code")
        received_dict.clear()

    def Read_BO_1(self, address):
        Raw_BO = self.Client_BO.read_holding_registers(address, count=1, unit=0x01)
        output_BO = struct.pack("H", Raw_BO.getRegister(0))
        # print("valve value is", output_BO)
        return output_BO

    def Read_BO_2(self, address):
        Raw_BO = self.Client_BO.read_holding_registers(address, count=2, unit=0x01)
        output_BO = struct.unpack(">f", struct.pack(">HH", Raw_BO.getRegister(1), Raw_BO.getRegister(0)))[
                              0]
        # print("valve value is", output_BO)
        return output_BO

    def float_to_2words(self, value):
        fl = float(value)
        x = np.arange(fl, fl + 1, dtype='<f4')
        if len(x) == 1:
            word = x.tobytes()
            piece1, piece2 = struct.unpack('<HH', word)
        else:
            print("ERROR in float to words")
        return piece1, piece2

    def int16_to_word(self, value):
        try:
            it = int(value)
            x = np.arange(it, it + 1, dtype='<i2')
            if len(x) == 1:
                word = x.tobytes()
            else:
                print("ERROR in float to words")
            return word
        except:
            return 0

    def int32_to_2words(self, value):
        try:
            it = int(value)
            x = np.arange(it, it + 1, dtype='<i4')
            if len(x) == 1:
                word = x.tobytes()
                piece1, piece2 = struct.unpack('<HH', word)
            else:
                print("ERROR in float to words")
            return piece1, piece2
        except:
            return 0

    def Write_BO_2(self, address, value):
        word1, word2 = self.float_to_2words(value)
        print('words', word1, word2)
        # pay attention to endian relationship
        Raw1 = self.Client_BO.write_register(address, value=word1, unit=0x01)
        Raw2 = self.Client_BO.write_register(address + 1, value=word2, unit=0x01)

        print("write result = ", Raw1, Raw2)

    def Write_BO_2_int16(self, address, value):
        # just write integer
        # word = self.int16_to_word(value)
        # print('word', word)
        # pay attention to endian relationship
        Raw = self.Client_BO.write_register(address, value=int(value), unit=0x01)

        print("write result = ", Raw)

    def Write_BO_2_int32(self, address, value):
        word1, word2 = self.int32_to_2words(value)
        print('words', word1, word2)
        # pay attention to endian relationship
        Raw1 = self.Client_BO.write_register(address, value=word1, unit=0x01)
        Raw2 = self.Client_BO.write_register(address + 1, value=word2, unit=0x01)

        print("write result = ", Raw1, Raw2)
    def trigcoil(self, address, digit):
                # Read register
        rr = self.Client_BO.read_holding_registers(address, 1, unit=0x01)
        value = rr.registers[0]

        # Toggle the specified bit using XOR
        new_value = value ^ (1 << digit)

        # Write the updated value back
        self.Client_BO.write_register(address, new_value, unit=0x01)

    def WriteBase2(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x0002
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write base2 result=", Raw)

    def WriteBase4(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x0004
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write base4 result=", Raw)

    def WriteBase8(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x0008
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write base8 result=", Raw)

    def WriteBase16(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x0010
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write base16 result=", Raw)

    def WriteBase32(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x0020
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write base32 result=", Raw)

    def WriteFF(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x8000
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write FF result=", Raw)

    def Reset(self, address):
        Raw = self.Client_BO.write_register(address, value=0x0010, unit=0x01)
        print("write Reset result=", Raw)

    # mask is a number to read a particular digit. for example, if you want to read 3rd digit, the mask is 0100(binary)
    def ReadCoil(self, mask, address):
        output_BO = self.Read_BO_1(address)
        masked_output = struct.unpack("H", output_BO)[0] & mask
        if masked_output == 0:
            return False
        else:
            return True

    def ReadFPAttribute(self, address):
        Raw = self.Client_BO.read_holding_registers(address, count=1, unit=0x01)
        output = struct.pack("H", Raw.getRegister(0))
        # print(Raw.getRegister(0))
        return output

    def SetFPRTDAttri(self, mode, address):
        # Highly suggested firstly read the value and then set as the FP menu suggests
        # mode should be wrtten in 0x
        # we use Read_BO_1 function because it can be used here, i.e read 2 word at a certain address
        output = self.ReadFPAttribute(address)
        print("output", address, output)
        Raw = self.Client_BO.write_register(address, value=mode, unit=0x01)
        print("write open result=", Raw)
        return 0

    def LOOPPID_SET_MODE(self, address, mode=0):
        output_BO = self.Read_BO_1(address)
        if mode == 0:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0010
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        elif mode == 1:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0020
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        elif mode == 2:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0040
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        elif mode == 3:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0080
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        else:
            Raw = "ERROR in LOOPPID SET MODE"

        print("write result:", "mode=", Raw)

    def LOOPPID_OUT_ENA(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x2000
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write OUT result=", Raw)

    def LOOPPID_OUT_DIS(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x4000
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write OUT result=", Raw)

    def LOOPPID_SETPOINT(self, address, setpoint, mode=0):
        if mode == 0:
            self.Write_BO_2(address + 10, setpoint)
        elif mode == 1:
            self.Write_BO_2(address + 12, setpoint)
        elif mode == 2:
            self.Write_BO_2(address + 14, setpoint)
        elif mode == 3:
            self.Write_BO_2(address + 16, setpoint)
        else:
            pass

        print("LOOPPID_SETPOINT")

    def LOOPPID_SET_HI_LIM(self, address, value):
        self.Write_BO_2(address + 6, value)
        print("LOOPPID_HI")

    def LOOPPID_SET_LO_LIM(self, address, value):
        self.Write_BO_2(address + 8, value)
        print("LOOPPID_LO")

    def LOOP2PT_SET_MODE(self, address, mode=0):
        output_BO = self.Read_BO_1(address)
        if mode == 0:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0400
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        elif mode == 1:
            input_BO = struct.unpack("H", output_BO)[0] | 0x0800
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        elif mode == 2:
            input_BO = struct.unpack("H", output_BO)[0] | 0x1000
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        elif mode == 3:
            input_BO = struct.unpack("H", output_BO)[0] | 0x2000
            Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        else:
            Raw = "ERROR in LOOP2PT SET MODE"

        print("write result:", "mode=", Raw)

    def LOOP2PT_OPEN(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x0002
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write OUT result=", Raw)

    def LOOP2PT_CLOSE(self, address):
        output_BO = self.Read_BO_1(address)
        input_BO = struct.unpack("H", output_BO)[0] | 0x004
        Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write OUT result=", Raw)

    def LOOP2PT_SETPOINT(self, address, setpoint, mode):
        if mode == 1:
            self.Write_BO_2(address + 2, setpoint)
        elif mode == 2:
            self.Write_BO_2(address + 4, setpoint)
        elif mode == 3:
            self.Write_BO_2(address + 6, setpoint)
        else:
            pass

        print("LOOPPID_SETPOINT")

    def WriteFloat(self, Address, value):
        if self.Connected_BO:
            value = value
            Dummy = self.Client_BO.write_register(Address, struct.unpack("<HH", struct.pack("<f", value))[1], unit=0x01)
            Dummy = self.Client_BO.write_register(Address + 1, struct.unpack("<HH", struct.pack("<f", value))[0],
                                               unit=0x01)

            time.sleep(0.1)

            Raw = self.Client_BO.read_holding_registers(Address, count=2, unit=0x01)
            rvalue = struct.unpack("<f", struct.pack("<HH", Raw.getRegister(1), Raw.getRegister(0)))[0]

            if value == rvalue:
                return 0
            else:
                return 2
        else:
            return 1

    def WriteBool(self, Address, Bit, value):
        if self.Connected_BO:
            Raw = self.Client_BO.read_coils(Address, count=Bit, unit=0x01)
            Raw.bits[Bit] = value
            Dummy = self.Client_BO.write_coil(Address, Raw, unit=0x01)

            time.sleep(0.1)

            Raw = self.Client_BO.read_coils(Address, count=Bit, unit=0x01)
            rvalue = Raw.bits[Bit]

            if value == rvalue:
                return 0
            else:
                return 2
        else:
            return 1


# Class to read PLC value every 2 sec
class UpdatePLC(PLC, threading.Thread):

    def __init__(self, plc_data, plc_lock, command_data, command_lock, alarm_stack, alarm_lock,global_time, timelock, *args, **kwargs):
        PLC.__init__(self, plc_data, plc_lock, command_data, command_lock, alarm_stack, alarm_lock)
        threading.Thread.__init__(self, *args, **kwargs)
        self.Running = False
        self.period = 1
        # every pid should have one unique para and rate
        self.TT_AD1_para = sec.TT_AD1_PARA
        self.TT_AD1_rate = sec.TT_AD1_RATE
        self.TT_AD2_para = sec.TT_AD2_PARA
        self.TT_AD2_rate = sec.TT_AD2_RATE
        self.HTRTD_para = sec.HTRTD_PARA
        self.HTRTD_rate = sec.HTRTD_RATE

        self.PT_para = sec.PT_PARA
        self.PT_rate = sec.PT_RATE
        self.LL_para = sec.LL_PARA
        self.LL_rate = sec.LL_RATE
        self.PR_CYCLE_para = 0
        self.PR_CYCLE_rate = 30
        self.LEFT_REAL_para = sec.LEFT_REAL_PARA
        self.LEFT_REAL_rate = sec.LEFT_REAL_RATE
        self.Din_para = sec.DIN_PARA
        self.Din_rate = sec.DIN_RATE
        self.LOOPPID_para = sec.LOOPPID_PARA
        self.LOOPPID_rate = sec.LOOPPID_RATE

        self.mainalarm_para = sec.MAINALARM_PARA
        self.mainalarm_rate = sec.MAINALARM_RATE
        self.broadcast_para = sec.BROAD_CAST_PARA
        self.broadcast_rate = sec.BROAD_CAST_RATE
        self.global_time = global_time
        self.timelock = timelock
        self.alarm_stack = alarm_stack
        self.alarm_lock = alarm_lock

    def run(self):

        self.Running = True

        while self.Running:
            try:
                with self.timelock:
                    self.global_time.update({"plctime" :datetime_in_1e5micro()})
                    print("PLC updating", self.global_time["plctime"])
            except Exception as e:
                print("Exception in plc raised")
                with self.alarm_lock:
                    self.alarm_stack.update({"PLC updating Exception": "PLC timestamp updates ERROR"})
                # self run depend on senario, we want to rerun the module by module
            # it has its own try function so we can skip try function here
            self.ReadAll()
            try:
                with self.command_lock:
                    self.write_data(self.command_data)
                # check alarms
                for keyTT_AD1 in self.TT_AD1_dic:
                    self.check_TT_AD1_alarm(keyTT_AD1)
                for keyTT_AD2 in self.TT_AD2_dic:
                    self.check_TT_AD2_alarm(keyTT_AD2)
                for keyHTRTD in self.HTRTD_dic:
                    self.check_HTRTD_alarm(keyHTRTD)
                for keyPT in self.PT_dic:
                    self.check_PT_alarm(keyPT)
                for keyLL in self.LL_dic:
                    self.check_LL_alarm(keyLL)
                for keyLOOPPID in self.LOOPPID_OUT:
                    self.check_LOOPPID_alarm(keyLOOPPID)
                self.or_alarm_signal()
                time.sleep(self.period)
            except Exception as e:
                # (type, value, traceback) = sys.exc_info()
                # exception_hook(type, value, traceback)
                print("Exception in plc raised",e)
                with self.alarm_lock:
                    self.alarm_stack.update({"PLC updating Exception":"PLC alarm check. Restarting..."})
                # if errors, clear the commands error, otherwise, the error will be constantly looping over
                with self.command_lock:
                    self.command_data.clear()
                # self run depend on senario, we want to rerun the module by module
                break
        self.run()



    def stop(self):
        self.Running = False

    def stack_alarm_msg(self, pid, string):
        with self.alarm_lock:
            self.alarm_stack.update({pid : string})
        # print("stack2", self.alarm_stack)

    def join_stack_into_message(self):
        message = ""
        if len(self.alarm_stack) >= 1:
            for key in self.alarm_stack:
                message = message + "\n" + self.alarm_stack[key]
        return message

    def check_LL_alarm(self, pid):
        # print("check alarm status")
        if self.LL_Activated[pid]:
            if float(self.LL_LowLimit[pid]) > float(self.LL_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if float(self.LL_dic[pid]) <= float(self.LL_LowLimit[pid]):
                    # print(pid , " reading is lower than the low limit")
                    self.LLalarmmsg(pid)


                elif float(self.LL_dic[pid]) >= float(self.LL_HighLimit[pid]):
                    # print(pid,  " reading is higher than the high limit")
                    self.LLalarmmsg(pid)


                else:
                    print(pid, " is in normal range")
                    self.resetLLalarmmsg(pid)


        else:
            self.resetTTAD1alarmmsg(pid)
            pass
    def check_TT_AD1_alarm(self, pid):

        if self.TT_AD1_Activated[pid]:
            if float(self.TT_AD1_LowLimit[pid]) > float(self.TT_AD1_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if float(self.TT_AD1_dic[pid]) <= float(self.TT_AD1_LowLimit[pid]):
                    self.TTAD1alarmmsg(pid)

                    # print(pid , " reading is lower than the low limit")
                elif float(self.TT_AD1_dic[pid]) >= float(self.TT_AD1_HighLimit[pid]):
                    self.TTAD1alarmmsg(pid)

                    # print(pid,  " reading is higher than the high limit")
                else:
                    self.resetTTAD1alarmmsg(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetTTAD1alarmmsg(pid)
            pass
    def check_TT_AD2_alarm(self, pid):

        if self.TT_AD2_Activated[pid]:
            if float(self.TT_AD2_LowLimit[pid]) > float(self.TT_AD2_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if float(self.TT_AD2_dic[pid]) <= float(self.TT_AD2_LowLimit[pid]):
                    self.TTAD2alarmmsg(pid)

                    # print(pid , " reading is lower than the low limit")
                elif float(self.TT_AD2_dic[pid]) >= float(self.TT_AD2_HighLimit[pid]):
                    self.TTAD2alarmmsg(pid)

                    # print(pid,  " reading is higher than the high limit")
                else:
                    self.resetTTAD2alarmmsg(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetTTAD2alarmmsg(pid)
            pass
    def check_HTRTD_alarm(self, pid):

        if self.HTRTD_Activated[pid]:
            if float(self.HTRTD_LowLimit[pid]) > float(self.HTRTD_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if float(self.HTRTD_dic[pid]) <= float(self.HTRTD_LowLimit[pid]):
                    self.HTRTDalarmmsg(pid)

                    # print(pid , " reading is lower than the low limit")
                elif float(self.HTRTD_dic[pid]) >= float(self.HTRTD_HighLimit[pid]):
                    self.HTRTDalarmmsg(pid)

                    # print(pid,  " reading is higher than the high limit")
                else:
                    self.resetHTRTDalarmmsg(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetHTRTDalarmmsg(pid)
            pass


    def check_PT_alarm(self, pid):

        if self.PT_Activated[pid]:
            if float(self.PT_LowLimit[pid]) > float(self.PT_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if float(self.PT_dic[pid]) <= float(self.PT_LowLimit[pid]):
                    self.PTalarmmsg(pid)

                    # print(pid , " reading is lower than the low limit")
                elif float(self.PT_dic[pid]) >= float(self.PT_HighLimit[pid]):
                    self.PTalarmmsg(pid)
                    # print(pid,  " reading is higher than the high limit")
                else:
                    self.resetPTalarmmsg(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetPTalarmmsg(pid)
            pass

    def check_LEFT_REAL_alarm(self, pid):

        if self.LEFT_REAL_Activated[pid]:
            if float(self.LEFT_REAL_LowLimit[pid]) > float(self.LEFT_REAL_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if float(self.LEFT_REAL_dic[pid]) <= float(self.LEFT_REAL_LowLimit[pid]):
                    self.LEFT_REALalarmmsg(pid)

                    # print(pid , " reading is lower than the low limit")
                elif float(self.LEFT_REAL_dic[pid]) >= float(self.LEFT_REAL_HighLimit[pid]):
                    self.LEFT_REALalarmmsg(pid)
                    # print(pid,  " reading is higher than the high limit")
                else:
                    self.resetLEFT_REALalarmmsg(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetLEFT_REALalarmmsg(pid)
            pass

    def check_Din_alarm(self, pid):

        if self.Din_Activated[pid]:
            if float(self.Din_LowLimit[pid]) > float(self.Din_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if float(self.Din_dic[pid]) <= float(self.Din_LowLimit[pid]):
                    self.Dinalarmmsg(pid)

                    # print(pid , " reading is lower than the low limit")
                elif float(self.Din_dic[pid]) >= float(self.Din_HighLimit[pid]):
                    self.Dinalarmmsg(pid)
                    # print(pid,  " reading is higher than the high limit")
                else:
                    self.resetDinalarmmsg(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetDinalarmmsg(pid)
            pass

    def check_LOOPPID_alarm(self, pid):


        if self.LOOPPID_Activated[pid]:
            if float(self.LOOPPID_Alarm_LowLimit[pid]) > float(self.LOOPPID_Alarm_HighLimit[pid]):
                print("Low limit should be less than high limit!")
            else:
                if float(self.LOOPPID_OUT[pid]) <= float(self.LOOPPID_Alarm_LowLimit[pid]):
                    self.LOOPPIDalarmmsg(pid)

                    # print(pid , " reaLOOPPIDg is lower than the low limit")
                elif float(self.LOOPPID_OUT[pid]) >= float(self.LOOPPID_Alarm_HighLimit[pid]):
                    self.LOOPPIDalarmmsg(pid)
                    # print(pid,  " reaLOOPPIDg is higher than the high limit")
                else:
                    self.resetLOOPPIDalarmmsg(pid)
                    # print(pid, " is in normal range")

        else:
            self.resetLOOPPIDalarmmsg(pid)
            pass

    def LLalarmmsg(self, pid):

        self.LL_Alarm[pid] = True
        # and send email or slack messages
        # every time interval send a alarm message
        # print("LL alarm",self.LL_para,self.LL_Alarm)
        if self.LL_para[pid] >= self.LL_rate[pid]:
            msg = "Henry's Panel alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(pid=pid, current=self.LL_dic[pid],
                                                                                                                     high=self.LL_HighLimit[pid], low=self.LL_LowLimit[pid])
            # self.message_manager.tencent_alarm(msg)
            # self.AI_slack_alarm.emit(msg)
            self.stack_alarm_msg(pid, msg)

            self.LL_para[pid] = 0
        self.LL_para[pid] += 1

    def TTAD1alarmmsg(self, pid):
        self.TT_AD1_Alarm[pid] = True
        # and send email or slack messages
        # every time interval send a alarm message
        print(self.TT_AD1_para[pid])
        if self.TT_AD1_para[pid] >= self.TT_AD1_rate[pid]:
            msg = "Henry's Panel alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(pid=pid, current=self.TT_AD1_dic[pid],
                                                                                                                     high=self.TT_AD1_HighLimit[pid], low=self.TT_AD1_LowLimit[pid])
            # self.message_manager.tencent_alarm(msg)
            # self.AI_slack_alarm.emit(msg)
            self.stack_alarm_msg(pid, msg)

            self.TT_AD1_para[pid] = 0
        self.TT_AD1_para[pid] += 1

    def resetTTAD1alarmmsg(self, pid):
        self.TT_AD1_Alarm[pid] = False
        self.alarm_stack.pop(pid, None)
        # self.TT_AD1_para = 0
        # and send email or slack messages

    def TTAD2alarmmsg(self, pid):
        self.TT_AD2_Alarm[pid] = True
        # and send email or slack messages
        # every time interval send a alarm message
        print(self.TT_AD2_para[pid])
        if self.TT_AD2_para[pid] >= self.TT_AD2_rate[pid]:
            msg = "Henry's Panel alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(pid=pid, current=self.TT_AD2_dic[pid],
                                                                                                                     high=self.TT_AD2_HighLimit[pid], low=self.TT_AD2_LowLimit[pid])
            # self.message_manager.tencent_alarm(msg)
            # self.AI_slack_alarm.emit(msg)
            self.stack_alarm_msg(pid, msg)

            self.TT_AD2_para[pid] = 0
        self.TT_AD2_para[pid] += 1

    def resetTTAD2alarmmsg(self, pid):
        self.TT_AD2_Alarm[pid] = False
        self.alarm_stack.pop(pid, None)
        # self.TT_AD2_para = 0
        # and send email or slack messages

    def HTRTDalarmmsg(self, pid):
        self.HTRTD_Alarm[pid] = True
        # and send email or slack messages
        # every time interval send a alarm message
        print(self.HTRTD_para[pid])
        if self.HTRTD_para[pid] >= self.HTRTD_rate[pid]:
            msg = "Henry's Panel alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(pid=pid, current=self.HTRTD_dic[pid],
                                                                                                                     high=self.HTRTD_HighLimit[pid], low=self.HTRTD_LowLimit[pid])
            # self.message_manager.tencent_alarm(msg)
            # self.AI_slack_alarm.emit(msg)
            self.stack_alarm_msg(pid, msg)

            self.HTRTD_para[pid] = 0
        self.HTRTD_para[pid] += 1

    def resetHTRTDalarmmsg(self, pid):
        self.HTRTD_Alarm[pid] = False
        self.alarm_stack.pop(pid, None)
        # self.HTRTD_para = 0
        # and send email or slack messages

    def PTalarmmsg(self, pid):
        self.PT_Alarm[pid] = True
        # and send email or slack messages
        if self.PT_para[pid] >= self.PT_rate[pid]:
            msg = "Henry's Panel alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(pid=pid, current=self.PT_dic[pid],
                                                                                                                     high=self.PT_HighLimit[pid], low=self.PT_LowLimit[pid])

            # self.message_manager.tencent_alarm(msg)
            # self.AI_slack_alarm.emit(msg)
            self.stack_alarm_msg(pid, msg)
            self.PT_para[pid] = 0
        self.PT_para[pid] += 1

    def resetPTalarmmsg(self, pid):
        self.PT_Alarm[pid] = False
        self.alarm_stack.pop(pid, None)
        # self.PT_para = 0
        # and send email or slack messages

    def LEFT_REALalarmmsg(self, pid):
        self.LEFT_REAL_Alarm[pid] = True
        # and send email or slack messages
        if self.LEFT_REAL_para[pid] >= self.LEFT_REAL_rate[pid]:
            msg = "Henry's Panel alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(pid=pid, current=self.LEFT_REAL_dic[pid],
                                                                                                                     high=self.LEFT_REAL_HighLimit[pid], low=self.LEFT_REAL_LowLimit[pid])

            # self.message_manager.tencent_alarm(msg)
            # self.AI_slack_alarm.emit(msg)
            self.stack_alarm_msg(pid, msg)
            self.LEFT_REAL_para[pid] = 0
        self.LEFT_REAL_para[pid] += 1

    def resetLEFT_REALalarmmsg(self, pid):
        self.LEFT_REAL_Alarm[pid] = False
        self.alarm_stack.pop(pid, None)
        # self.LEFT_REAL_para = 0
        # and send email or slack messages

    def Dinalarmmsg(self, pid):
        self.Din_Alarm[pid] = True
        # and send email or slack messages
        if self.Din_para[pid] >= self.Din_rate[pid]:
            msg = "Henry's Panel alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(pid=pid, current=self.Din_dic[pid],
                                                                                                                     high=self.Din_HighLimit[pid], low=self.Din_LowLimit[pid])

            # self.message_manager.tencent_alarm(msg)
            # self.AI_slack_alarm.emit(msg)
            self.stack_alarm_msg(pid, msg)
            self.Din_para[pid] = 0
        self.Din_para[pid] += 1

    def resetDinalarmmsg(self, pid):
        self.Din_Alarm[pid] = False
        self.alarm_stack.pop(pid, None)
        # self.Din_para = 0
        # and send email or slack messages

    def LOOPPIDalarmmsg(self, pid):
        self.LOOPPID_Alarm[pid] = True
        # and send email or slack messages
        if self.LOOPPID_para[pid] >= self.LOOPPID_rate[pid]:
            msg = "Henry's Panel alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(pid=pid, current=self.LOOPPID_OUT[pid],
                                                                                                                     high=self.LOOPPID_Alarm_HighLimit[pid], low=self.LOOPPID_Alarm_LowLimit[pid])
            # print("initial message",msg)
            # self.message_manager.tencent_alarm(msg)
            # self.AI_slack_alarm.emit(msg)
            self.stack_alarm_msg(pid, msg)
            self.LOOPPID_para[pid] = 0
        self.LOOPPID_para[pid] += 1

    def resetLOOPPIDalarmmsg(self, pid):
        self.LOOPPID_Alarm[pid] = False
        self.alarm_stack.pop(pid, None)
        # self.LOOPPID_para = 0
        # and send email or slack messages

    def or_alarm_signal(self):
        # print("or alarm",self.true_in_dic(self.LL_Alarm))
        if (self.true_in_dic(self.PT_Alarm)) or (self.true_in_dic(self.TT_AD1_Alarm)) or(self.true_in_dic(self.TT_AD2_Alarm)) or (self.true_in_dic(self.LEFT_REAL_Alarm)) or (self.true_in_dic(self.Din_Alarm)) or (self.true_in_dic(self.LOOPPID_Alarm)) or (self.true_in_dic(self.LL_Alarm) or (self.true_in_dic(self.HTRTD_Alarm))):
            self.MainAlarm = True
        else:
            self.MainAlarm = False

    def resetLLalarmmsg(self, pid):
        self.LL_Alarm[pid] = False
        self.alarm_stack.pop(pid, None)
        # self.LEFT_REAL_para = 0
        # and send email or slack messages

    def true_in_dic(self,dic):
        value = False
        for key in dic:
            if dic[key]==True:
                value = True

        return value


# Class to update myseeq database

class UpdateDataBase(threading.Thread):

    def __init__(self, plc_data, plc_lock, global_time, timelock, alarm_stack, alarm_lock):
        # inherit the thread method
        super().__init__()
        self.plc_data = plc_data
        self.plc_lock = plc_lock
        self.global_time = global_time
        self.timelock = timelock
        self.alarm_stack = alarm_stack
        self.alarm_lock = alarm_lock


        self.Running = False
        # if loop runs with _counts times with New_Database = False(No written Data), then send alarm to slack. Otherwise, the code normally run(reset the pointer)
        self.Running_counts = 600
        self.Running_pointer = 0
        self.longsleep = 60

        self.base_period = 1

        self.COUPP_ERROR = False
        self.COUPP_ALARM = "k"
        self.COUPP_HOLD = False

        self.para_alarm = copy.copy(env.DATABASE_PARA["alarm"])
        self.rate_alarm = copy.copy(env.DATABASE_RATE["alarm"])
        self.para_TT = copy.copy(env.DATABASE_PARA["TT"])
        self.rate_TT = copy.copy(env.DATABASE_RATE["TT"])
        self.para_PT = copy.copy(env.DATABASE_PARA["PT"])
        self.rate_PT = copy.copy(env.DATABASE_RATE["PT"])
        self.para_REAL = copy.copy(env.DATABASE_PARA["REAL"])
        self.rate_REAL = copy.copy(env.DATABASE_RATE["REAL"])
        self.para_Din = copy.copy(env.DATABASE_PARA["Din"])
        self.rate_Din = copy.copy(env.DATABASE_RATE["Din"])
        # c is for valve status
        self.para_Valve = copy.copy(env.DATABASE_PARA["Valve"])
        self.rate_Valve = copy.copy(env.DATABASE_RATE["Valve"])
        self.para_Switch = copy.copy(env.DATABASE_PARA["Switch"])
        self.rate_Switch = copy.copy(env.DATABASE_RATE["Switch"])
        self.para_LOOPPID = copy.copy(env.DATABASE_PARA["LOOPPID"])
        self.rate_LOOPPID = copy.copy(env.DATABASE_RATE["LOOPPID"])
        self.para_LOOP2PT = copy.copy(env.DATABASE_PARA["LOOP2PT"])
        self.rate_LOOP2PT = copy.copy(env.DATABASE_RATE["LOOP2PT"])
        self.para_FLAG = copy.copy(env.DATABASE_PARA["FLAG"])
        self.rate_FLAG = copy.copy(env.DATABASE_RATE["FLAG"])
        self.para_INTLK_A = copy.copy(env.DATABASE_PARA["INTLK_A"])
        self.rate_INTLK_A = copy.copy(env.DATABASE_RATE["INTLK_A"])
        self.para_INTLK_D = copy.copy(env.DATABASE_PARA["INTLK_D"])
        self.rate_INTLK_D = copy.copy(env.DATABASE_RATE["INTLK_D"])
        self.para_FF = copy.copy(env.DATABASE_PARA["FF"])
        self.rate_FF = copy.copy(env.DATABASE_RATE["FF"])
        self.para_PARAM_F = copy.copy(env.DATABASE_PARA["PARAM_F"])
        self.rate_PARAM_F = copy.copy(env.DATABASE_RATE["PARAM_F"])
        self.para_PARAM_I = copy.copy(env.DATABASE_PARA["PARAM_I"])
        self.rate_PARAM_I = copy.copy(env.DATABASE_RATE["PARAM_I"])
        self.para_PARAM_B = copy.copy(env.DATABASE_PARA["PARAM_B"])
        self.rate_PARAM_B = copy.copy(env.DATABASE_RATE["PARAM_B"])
        self.para_PARAM_T = copy.copy(env.DATABASE_PARA["PARAM_T"])
        self.rate_PARAM_T = copy.copy(env.DATABASE_RATE["PARAM_T"])
        self.para_TIME = copy.copy(env.DATABASE_PARA["TIME"])
        self.rate_TIME = copy.copy(env.DATABASE_RATE["TIME"])
        self.para_LL =copy.copy(env.DATABASE_PARA["LL"])
        self.rate_LL =copy.copy(env.DATABASE_RATE["LL"])


        # status initialization
        self.status = False

        # commit initialization
        self.commit_bool = False
        # INITIALIZATION
        self.TT_AD1_address = copy.copy(sec.TT_AD1_ADDRESS)
        self.TT_AD2_address = copy.copy(sec.TT_AD2_ADDRESS)
        self.HTRTD_address = copy.copy(sec.HTRTD_ADDRESS)
        self.PT_address = copy.copy(sec.PT_ADDRESS)

        self.LEFT_REAL_address = copy.copy(sec.LEFT_REAL_ADDRESS)

        self.TT_AD1_dic = copy.copy(sec.TT_AD1_DIC)
        self.TT_AD1_cali = copy.copy(sec.TT_AD1_CALI)
        self.TT_AD2_dic = copy.copy(sec.TT_AD2_DIC)

        self.HTRTD_dic = copy.copy(sec.HTRTD_DIC)

        self.PT_dic = copy.copy(sec.PT_DIC)

        self.LEFT_REAL_dic = copy.copy(sec.LEFT_REAL_DIC)

        self.TT_AD1_LowLimit = copy.copy(sec.TT_AD1_LOWLIMIT)

        self.TT_AD1_HighLimit = copy.copy(sec.TT_AD1_HIGHLIMIT)

        self.TT_AD2_LowLimit = copy.copy(sec.TT_AD2_LOWLIMIT)

        self.TT_AD2_HighLimit = copy.copy(sec.TT_AD2_HIGHLIMIT)

        self.HTRTD_LowLimit = copy.copy(sec.HTRTD_LOWLIMIT)
        self.HTRTD_HighLimit = copy.copy(sec.HTRTD_HIGHLIMIT)
        self.PT_LowLimit = copy.copy(sec.PT_LOWLIMIT)
        self.PT_HighLimit = copy.copy(sec.PT_HIGHLIMIT)

        self.LEFT_REAL_HighLimit = copy.copy(sec.LEFT_REAL_HIGHLIMIT)
        self.LEFT_REAL_LowLimit = copy.copy(sec.LEFT_REAL_LOWLIMIT)

        self.TT_AD1_Activated = copy.copy(sec.TT_AD1_ACTIVATED)
        self.TT_AD2_Activated = copy.copy(sec.TT_AD2_ACTIVATED)
        self.HTRTD_Activated = copy.copy(sec.HTRTD_ACTIVATED)
        self.PT_Activated = copy.copy(sec.PT_ACTIVATED)
        self.LEFT_REAL_Activated = copy.copy(sec.LEFT_REAL_ACTIVATED)

        self.TT_AD1_Alarm = copy.copy(sec.TT_AD1_ALARM)
        self.TT_AD2_Alarm = copy.copy(sec.TT_AD2_ALARM)
        self.HTRTD_Alarm = copy.copy(sec.HTRTD_ALARM)

        self.PT_Alarm = copy.copy(sec.PT_ALARM)
        self.LEFT_REAL_Alarm = copy.copy(sec.LEFT_REAL_ALARM)
        self.MainAlarm = copy.copy(sec.MAINALARM)
        self.MAN_SET = copy.copy(sec.MAN_SET)

        self.nTT_AD1 = copy.copy(sec.NTT_AD1)
        self.nTT_AD2 = copy.copy(sec.NTT_AD2)
        self.nHTRTD = copy.copy(sec.NHTRTD)
        self.nPT = copy.copy(sec.NPT)
        self.nREAL = copy.copy(sec.NREAL)

        self.PT_setting = copy.copy(sec.PT_SETTING)
        self.nPT_Attribute = copy.copy(sec.NPT_ATTRIBUTE)

        self.Din_address = copy.copy(sec.DIN_ADDRESS)
        self.nDin = copy.copy(sec.NDIN)
        self.Din = copy.copy(sec.DIN)
        self.Din_dic = copy.copy(sec.DIN_DIC)
        self.Din_LowLimit = copy.copy(sec.DIN_LOWLIMIT)
        self.Din_HighLimit = copy.copy(sec.DIN_HIGHLIMIT)
        self.Din_Activated = copy.copy(sec.DIN_ACTIVATED)
        self.Din_Alarm = copy.copy(sec.DIN_ALARM)

        self.valve_address = copy.copy(sec.VALVE_ADDRESS)
        self.nValve = copy.copy(sec.NVALVE)
        self.Valve = copy.copy(sec.VALVE)
        self.Valve_OUT = copy.copy(sec.VALVE_OUT)
        self.Valve_MAN = copy.copy(sec.VALVE_MAN)
        self.Valve_INTLKD = copy.copy(sec.VALVE_INTLKD)
        self.Valve_ERR = copy.copy(sec.VALVE_ERR)
        self.Valve_Busy = copy.copy(sec.VALVE_BUSY)
        self.valve_invert_list = sec.VALVE_INVERT_LIST

        self.LOOPPID_ADR_BASE = copy.copy(sec.LOOPPID_ADR_BASE)

        self.LOOPPID_MODE0 = copy.copy(sec.LOOPPID_MODE0)

        self.LOOPPID_MODE1 = copy.copy(sec.LOOPPID_MODE1)

        self.LOOPPID_MODE2 = copy.copy(sec.LOOPPID_MODE2)

        self.LOOPPID_MODE3 = copy.copy(sec.LOOPPID_MODE3)

        self.LOOPPID_INTLKD = copy.copy(sec.LOOPPID_INTLKD)
        self.LOOPPID_TT = copy.copy(sec.LOOPPID_TT)

        self.LOOPPID_MAN = copy.copy(sec.LOOPPID_MAN)

        self.LOOPPID_ERR = copy.copy(sec.LOOPPID_ERR)

        self.LOOPPID_SATHI = copy.copy(sec.LOOPPID_SATHI)

        self.LOOPPID_SATLO = copy.copy(sec.LOOPPID_SATLO)

        self.LOOPPID_EN = copy.copy(sec.LOOPPID_EN)

        self.LOOPPID_OUT = copy.copy(sec.LOOPPID_OUT)

        self.LOOPPID_IN = copy.copy(sec.LOOPPID_IN)

        self.LOOPPID_HI_LIM = copy.copy(sec.LOOPPID_HI_LIM)

        self.LOOPPID_LO_LIM = copy.copy(sec.LOOPPID_LO_LIM)

        self.LOOPPID_SET0 = copy.copy(sec.LOOPPID_SET0)

        self.LOOPPID_SET1 = copy.copy(sec.LOOPPID_SET1)

        self.LOOPPID_SET2 = copy.copy(sec.LOOPPID_SET2)

        self.LOOPPID_SET3 = copy.copy(sec.LOOPPID_SET3)
        self.LOOPPID_Busy = copy.copy(sec.LOOPPID_BUSY)
        self.LOOPPID_Activated = copy.copy(sec.LOOPPID_ACTIVATED)
        self.LOOPPID_Alarm = copy.copy(sec.LOOPPID_ALARM)
        self.LOOPPID_Alarm_HighLimit = copy.copy(sec.LOOPPID_ALARM_HI_LIM)
        self.LOOPPID_Alarm_LowLimit = copy.copy(sec.LOOPPID_ALARM_LO_LIM)

        self.LOOP2PT_ADR_BASE = copy.copy(sec.LOOP2PT_ADR_BASE)
        self.LOOP2PT_MODE0 = copy.copy(sec.LOOP2PT_MODE0)
        self.LOOP2PT_MODE1 = copy.copy(sec.LOOP2PT_MODE1)
        self.LOOP2PT_MODE2 = copy.copy(sec.LOOP2PT_MODE2)
        self.LOOP2PT_MODE3 = copy.copy(sec.LOOP2PT_MODE3)
        self.LOOP2PT_INTLKD = copy.copy(sec.LOOP2PT_INTLKD)
        self.LOOP2PT_MAN = copy.copy(sec.LOOP2PT_MAN)
        self.LOOP2PT_ERR = copy.copy(sec.LOOP2PT_ERR)
        self.LOOP2PT_OUT = copy.copy(sec.LOOP2PT_OUT)
        self.LOOP2PT_SET1 = copy.copy(sec.LOOP2PT_SET1)
        self.LOOP2PT_SET2 = copy.copy(sec.LOOP2PT_SET2)
        self.LOOP2PT_SET3 = copy.copy(sec.LOOP2PT_SET3)
        self.LOOP2PT_Busy = copy.copy(sec.LOOP2PT_BUSY)

        self.Procedure_address = copy.copy(sec.PROCEDURE_ADDRESS)
        self.Procedure_running = copy.copy(sec.PROCEDURE_RUNNING)
        self.Procedure_INTLKD = copy.copy(sec.PROCEDURE_INTLKD)
        self.Procedure_EXIT = copy.copy(sec.PROCEDURE_EXIT)

        self.INTLK_D_ADDRESS = copy.copy(sec.INTLK_D_ADDRESS)
        self.INTLK_D_DIC = copy.copy(sec.INTLK_D_DIC)
        self.INTLK_D_EN = copy.copy(sec.INTLK_D_EN)
        self.INTLK_D_COND = copy.copy(sec.INTLK_D_COND)
        self.INTLK_D_Busy = copy.copy(sec.INTLK_D_BUSY)
        self.INTLK_A_ADDRESS = copy.copy(sec.INTLK_A_ADDRESS)
        self.INTLK_A_DIC = copy.copy(sec.INTLK_A_DIC)
        self.INTLK_A_EN = copy.copy(sec.INTLK_A_EN)
        self.INTLK_A_COND = copy.copy(sec.INTLK_A_COND)
        self.INTLK_A_SET = copy.copy(sec.INTLK_A_SET)
        self.INTLK_A_Busy = copy.copy(sec.INTLK_A_BUSY)

        self.FLAG_ADDRESS = copy.copy(sec.FLAG_ADDRESS)
        self.FLAG_DIC = copy.copy(sec.FLAG_DIC)
        self.FLAG_INTLKD = copy.copy(sec.FLAG_INTLKD)
        self.FLAG_Busy = copy.copy(sec.FLAG_BUSY)

        self.FF_ADDRESS = copy.copy(sec.FF_ADDRESS)
        self.FF_DIC = copy.copy(sec.FF_DIC)

        self.PARAM_F_ADDRESS = copy.copy(sec.PARAM_F_ADDRESS)
        self.PARAM_F_DIC = copy.copy(sec.PARAM_F_DIC)

        self.PARAM_I_ADDRESS = copy.copy(sec.PARAM_I_ADDRESS)
        self.PARAM_I_DIC = copy.copy(sec.PARAM_I_DIC)

        self.PARAM_B_ADDRESS = copy.copy(sec.PARAM_B_ADDRESS)
        self.PARAM_B_DIC = copy.copy(sec.PARAM_B_DIC)

        self.PARAM_T_ADDRESS = copy.copy(sec.PARAM_T_ADDRESS)
        self.PARAM_T_DIC = copy.copy(sec.PARAM_T_DIC)

        self.TIME_ADDRESS = copy.copy(sec.TIME_ADDRESS)
        self.TIME_DIC = copy.copy(sec.TIME_DIC)

        self.LL_dic = copy.copy(sec.LL_DIC)
        self.LL_address = copy.copy(sec.LL_ADDRESS)
        self.LL_LowLimit = copy.copy(sec.LL_LOWLIMIT)
        self.LL_HighLimit = copy.copy(sec.LL_HIGHLIMIT)
        self.LL_Alarm = copy.copy(sec.LL_ALARM)
        self.LL_Activated = copy.copy(sec.LL_ACTIVATED)
        self.nLL = copy.copy(sec.NLL)

        self.CAP_dic = copy.copy(sec.CAP_DIC)
        self.para_CAP = copy.copy(env.DATABASE_PARA["CAP"])
        self.rate_CAP = copy.copy(env.DATABASE_RATE["CAP"])

        # BUFFER parts
        self.Valve_buffer = copy.copy(sec.VALVE_OUT)
        # self.Switch_buffer = copy.copy(sec.SWITCH_OUT)
        self.Din_buffer = copy.copy(sec.DIN_DIC)
        self.LOOPPID_EN_buffer = copy.copy(sec.LOOPPID_EN)
        self.LOOPPID_MODE0_buffer = copy.copy(sec.LOOPPID_MODE0)
        self.LOOPPID_MODE1_buffer = copy.copy(sec.LOOPPID_MODE1)
        self.LOOPPID_MODE2_buffer = copy.copy(sec.LOOPPID_MODE2)
        self.LOOPPID_MODE3_buffer = copy.copy(sec.LOOPPID_MODE3)
        self.LOOPPID_OUT_buffer = copy.copy(sec.LOOPPID_OUT)
        self.LOOPPID_IN_buffer = copy.copy(sec.LOOPPID_IN)

        self.LOOP2PT_MODE0_buffer = copy.copy(sec.LOOP2PT_MODE0)
        self.LOOP2PT_MODE1_buffer = copy.copy(sec.LOOP2PT_MODE1)
        self.LOOP2PT_MODE2_buffer = copy.copy(sec.LOOP2PT_MODE2)
        self.LOOP2PT_MODE3_buffer = copy.copy(sec.LOOP2PT_MODE3)
        self.LOOP2PT_OUT_buffer = copy.copy(sec.LOOP2PT_OUT)

        self.FLAG_INTLKD_buffer = copy.copy(sec.FLAG_INTLKD)

        self.FF_buffer = copy.copy(sec.FF_DIC)
        self.PARAM_B_buffer = copy.copy(sec.PARAM_B_DIC)

        print("begin updating Database")


    def run(self):

        self.Running = True
        while self.Running:
            try:
                self.dt = datetime_in_1e5micro()
                self.early_dt = early_datetime()
                self.gmt_dt = datetime_in_1e5micro_gmt()
                self.early_gmt_dt = early_datetime_in_1e5micro_gmt()
                with self.timelock:
                    self.global_time.update({"dbtime":self.dt})
                print("Database Updating", self.global_time["dbtime"])

            except Exception as e:
                with self.alarm_lock:
                    self.alarm_stack.update({"Database Exception #1": "Local database timestamp error"})
                print("Error",e)


            try:
                with self.plc_lock:
                    data_received = dict(self.plc_data)
                self.update_value(data_received)
                print("update data from PLC")

            except Exception as e:
                with self.alarm_lock:
                    self.alarm_stack.update({"Database Exception #2": "Local database data reception error"})
                # (type, value, traceback) = sys.exc_info()
                # exception_hook(type, value, traceback)
            try:
                #     # if connected, run the write function, else try to reconnect
                #     # if reconnect process failed, then raise the Error as alarm msg depending on whether self.db exists
                # only when no mysql connections
                # if hasattr(self, 'db') or not self.db.db.is_connected():
                if not hasattr(self, 'db'): # if it doesn't exist, try to create it
                    self.db = mydatabase()
                else:
                    # connection exist but broken, restart it
                    if not self.db.db.is_connected():
                        self.db.db.close()
                        self.db = mydatabase()
                if self.db.db.is_connected():

                    try:
                        # Check if the connection is still alive
                        self.db.db.ping(reconnect=True)
                        self.write_data()
                        print("Data written into database")

                    except mysql.connector.Error as e:
                        # Handle database errors (e.g., connection lost)
                        print("Database error:", e)
                        print("Attempting to reconnect...")
                        with self.alarm_lock:
                            self.alarm_stack.update({"Database Exception #3": "Local database data saving error- Database is disconnected"})
                            print("Database Exception #3: Local database data saving error- Database is disconnected")

            except mysql.connector.Error as e0:
                # Handle connection errors (e.g., initial connection failure)
                print("Error connecting to MySQL database:", e0)
                with self.alarm_lock:
                    self.alarm_stack.update({"Database Exception #4": "Local database data saving error- Database is disconnected"})
                print("Database Exception #4 Local database data saving error- Database is disconnected")



            time.sleep(self.base_period)

        self.run()

    def stop(self):
        self.Running = False

    def update_status(self, status):
        self.status = status

    def update_value(self, dic):
        # print("Database received the data from PLC")
        for key in self.TT_AD1_dic:
            self.TT_AD1_dic[key] = dic["data"]["TT"]["AD1"]["value"][key]
        for key in self.TT_AD2_dic:
            self.TT_AD2_dic[key] = dic["data"]["TT"]["AD2"]["value"][key]
        for key in self.HTRTD_dic:
            self.HTRTD_dic[key] = dic["data"]["TT"]["LS"]["value"][key]
        for key in self.LEFT_REAL_dic:
            self.LEFT_REAL_dic[key] = dic["data"]["LEFT_REAL"]["value"][key]
        for key in self.Din_dic:
            self.Din_dic[key] = dic["data"]["Din"]["value"][key]

        for key in self.PT_dic:
            self.PT_dic[key] = dic["data"]["PT"]["value"][key]
        for key in self.LL_dic:
            self.LL_dic[key] = dic["data"]["LL"]["value"][key]
        for key in self.CAP_dic:
            self.CAP_dic[key] = dic["data"]["CAP"]["value"][key]
        for key in self.TT_AD1_HighLimit:
            self.TT_AD1_HighLimit[key] = dic["data"]["TT"]["AD1"]["high"][key]
        for key in self.TT_AD2_HighLimit:
            self.TT_AD2_HighLimit[key] = dic["data"]["TT"]["AD2"]["high"][key]
        for key in self.HTRTD_HighLimit:
            self.HTRTD_HighLimit[key] = dic["data"]["TT"]["LS"]["high"][key]

        for key in self.PT_HighLimit:
            self.PT_HighLimit[key] = dic["data"]["PT"]["high"][key]
        for key in self.LEFT_REAL_HighLimit:
            self.LEFT_REAL_HighLimit[key] = dic["data"]["LEFT_REAL"]["high"][key]

        for key in self.TT_AD1_LowLimit:
            self.TT_AD1_LowLimit[key] = dic["data"]["TT"]["AD1"]["low"][key]
        for key in self.TT_AD2_LowLimit:
            self.TT_AD2_LowLimit[key] = dic["data"]["TT"]["AD2"]["low"][key]
        for key in self.HTRTD_LowLimit:
            self.HTRTD_LowLimit[key] = dic["data"]["TT"]["LS"]["low"][key]

        for key in self.PT_LowLimit:
            self.PT_LowLimit[key] = dic["data"]["PT"]["low"][key]
        for key in self.LEFT_REAL_LowLimit:
            self.LEFT_REAL_LowLimit[key] = dic["data"]["LEFT_REAL"]["low"][key]

        for key in self.Valve_OUT:
            self.Valve_OUT[key] = dic["data"]["Valve"]["OUT"][key]
        for key in self.Valve_INTLKD:
            self.Valve_INTLKD[key] = dic["data"]["Valve"]["INTLKD"][key]
        for key in self.Valve_MAN:
            self.Valve_MAN[key] = dic["data"]["Valve"]["MAN"][key]
        for key in self.Valve_ERR:
            self.Valve_ERR[key] = dic["data"]["Valve"]["ERR"][key]

        for key in self.TT_AD1_Alarm:
            self.TT_AD1_Alarm[key] = dic["Alarm"]["TT"]["AD1"][key]
        for key in self.TT_AD2_Alarm:
            self.TT_AD2_Alarm[key] = dic["Alarm"]["TT"]["AD2"][key]
        for key in self.HTRTD_Alarm:
            self.HTRTD_Alarm[key] = dic["Alarm"]["TT"]["LS"][key]
        for key in self.PT_dic:
            self.PT_Alarm[key] = dic["Alarm"]["PT"][key]
        for key in self.LEFT_REAL_dic:
            self.LEFT_REAL_Alarm[key] = dic["Alarm"]["LEFT_REAL"][key]
        for key in self.LOOPPID_MODE0:
            self.LOOPPID_MODE0[key] = dic["data"]["LOOPPID"]["MODE0"][key]
        for key in self.LOOPPID_MODE1:
            self.LOOPPID_MODE1[key] = dic["data"]["LOOPPID"]["MODE1"][key]
        for key in self.LOOPPID_MODE2:
            self.LOOPPID_MODE2[key] = dic["data"]["LOOPPID"]["MODE2"][key]
        for key in self.LOOPPID_MODE3:
            self.LOOPPID_MODE3[key] = dic["data"]["LOOPPID"]["MODE3"][key]
        for key in self.LOOPPID_INTLKD:
            self.LOOPPID_INTLKD[key] = dic["data"]["LOOPPID"]["INTLKD"][key]
        for key in self.LOOPPID_MAN:
            self.LOOPPID_MAN[key] = dic["data"]["LOOPPID"]["MAN"][key]
        for key in self.LOOPPID_ERR:
            self.LOOPPID_ERR[key] = dic["data"]["LOOPPID"]["ERR"][key]
        for key in self.LOOPPID_SATHI:
            self.LOOPPID_SATHI[key] = dic["data"]["LOOPPID"]["SATHI"][key]
        for key in self.LOOPPID_SATLO:
            self.LOOPPID_SATLO[key] = dic["data"]["LOOPPID"]["SATLO"][key]
        for key in self.LOOPPID_EN:
            self.LOOPPID_EN[key] = dic["data"]["LOOPPID"]["EN"][key]
        for key in self.LOOPPID_OUT:
            self.LOOPPID_OUT[key] = dic["data"]["LOOPPID"]["OUT"][key]
        for key in self.LOOPPID_IN:
            self.LOOPPID_IN[key] = dic["data"]["LOOPPID"]["IN"][key]
        for key in self.LOOPPID_HI_LIM:
            self.LOOPPID_HI_LIM[key] = dic["data"]["LOOPPID"]["HI_LIM"][key]
        for key in self.LOOPPID_LO_LIM:
            self.LOOPPID_LO_LIM[key] = dic["data"]["LOOPPID"]["LO_LIM"][key]
        for key in self.LOOPPID_SET0:
            self.LOOPPID_SET0[key] = dic["data"]["LOOPPID"]["SET0"][key]
        for key in self.LOOPPID_SET1:
            self.LOOPPID_SET1[key] = dic["data"]["LOOPPID"]["SET1"][key]
        for key in self.LOOPPID_SET2:
            self.LOOPPID_SET2[key] = dic["data"]["LOOPPID"]["SET2"][key]
        for key in self.LOOPPID_SET3:
            self.LOOPPID_SET3[key] = dic["data"]["LOOPPID"]["SET3"][key]
        for key in self.LOOP2PT_OUT:
            self.LOOP2PT_OUT[key] = dic["data"]["LOOP2PT"]["OUT"][key]
        for key in self.LOOP2PT_SET1:
            self.LOOP2PT_SET1[key] = dic["data"]["LOOP2PT"]["SET1"][key]
        for key in self.LOOP2PT_SET2:
            self.LOOP2PT_SET2[key] = dic["data"]["LOOP2PT"]["SET2"][key]
        for key in self.LOOP2PT_SET3:
            self.LOOP2PT_SET3[key] = dic["data"]["LOOP2PT"]["SET3"][key]

        self.MainAlarm = dic["MainAlarm"]
        print("Database received the data from PLC")


    def write_data(self):
        if self.para_TT >= self.rate_TT:
            for key in self.TT_AD1_dic:
                self.db.insert_data_into_stack(key, self.dt, self.TT_AD1_dic[key], self.gmt_dt)
            for key in self.TT_AD2_dic:
                self.db.insert_data_into_stack(key, self.dt, self.TT_AD2_dic[key], self.gmt_dt)
            for key in self.HTRTD_dic:
                self.db.insert_data_into_stack(key, self.dt, self.HTRTD_dic[key], self.gmt_dt)
            # print("write RTDS")
            self.commit_bool = True
            self.para_TT = 0

        if self.para_PT >= self.rate_PT:
            for key in self.PT_dic:
                self.db.insert_data_into_stack(key, self.dt, self.PT_dic[key], self.gmt_dt)
            # print("write pressure transducer")
            self.commit_bool = True
            self.para_PT = 0
        # print(2)
        for key in self.Valve_OUT:
            if self.Valve_OUT[key] != self.Valve_buffer[key]:
                self.db.insert_data_into_stack(key + '_OUT', self.early_dt, self.Valve_buffer[key],
                                                  self.early_gmt_dt)
                self.db.insert_data_into_stack(key + '_OUT', self.dt, self.Valve_OUT[key], self.gmt_dt)
                self.Valve_buffer[key] = self.Valve_OUT[key]
                self.commit_bool = True
                # print(self.Valve_OUT[key], self.gmt_dt)
            else:
                pass

        if self.para_Valve >= self.rate_Valve:
            for key in self.Valve_OUT:
                self.db.insert_data_into_stack(key + '_OUT', self.dt, self.Valve_OUT[key], self.gmt_dt)
                self.Valve_buffer[key] = self.Valve_OUT[key]
                self.commit_bool = True
            self.para_Valve = 0

        if self.para_LL >= self.rate_LL:
            for key in self.LL_dic:
                self.db.insert_data_into_stack(key, self.dt, self.LL_dic[key], self.gmt_dt)
            # print("write pressure transducer")
            self.commit_bool = True
            self.para_LL = 0

        if self.para_CAP >= self.rate_CAP:
            for key in self.CAP_dic:
                self.db.insert_data_into_stack(key, self.dt, self.CAP_dic[key], self.gmt_dt)
            self.commit_bool = True
            self.para_CAP = 0

        # if state of bool variable changes, write the data into databaseF
        # print(5)
        for key in self.LOOPPID_EN:
            # print(key, self.Valve_OUT[key] != self.Valve_buffer[key], self.gmt_dt)
            if self.LOOPPID_EN[key] != self.LOOPPID_EN_buffer[key]:
                self.db.insert_data_into_stack(key + '_EN', self.early_dt, self.LOOPPID_EN_buffer[key],
                                                  self.early_gmt_dt)
                self.db.insert_data_into_stack(key + '_EN', self.dt, self.LOOPPID_EN[key], self.gmt_dt)
                self.LOOPPID_EN_buffer[key] = self.LOOPPID_EN[key]
                self.commit_bool = True
                # print(self.Valve_OUT[key], self.gmt_dt)
            else:
                pass

        for key in self.LOOPPID_MODE0:
            # print(key, self.Valve_OUT[key] != self.Valve_buffer[key], self.gmt_dt)
            if self.LOOPPID_MODE0[key] != self.LOOPPID_MODE0_buffer[key]:
                self.db.insert_data_into_stack(key + '_MODE0', self.early_dt, self.LOOPPID_MODE0_buffer[key],
                                                  self.early_gmt_dt)
                self.db.insert_data_into_stack(key + '_MODE0', self.dt, self.LOOPPID_MODE0[key], self.gmt_dt)
                self.LOOPPID_MODE0_buffer[key] = self.LOOPPID_MODE0[key]
                self.commit_bool = True
                # print(self.Valve_OUT[key], self.gmt_dt)
            else:
                pass

        for key in self.LOOPPID_MODE1:
            # print(key, self.Valve_OUT[key] != self.Valve_buffer[key], self.gmt_dt)
            if self.LOOPPID_MODE1[key] != self.LOOPPID_MODE1_buffer[key]:
                self.db.insert_data_into_stack(key + '_MODE1', self.early_dt, self.LOOPPID_MODE1_buffer[key],
                                                  self.early_gmt_dt)
                self.db.insert_data_into_stack(key + '_MODE1', self.dt, self.LOOPPID_MODE1[key], self.gmt_dt)
                self.LOOPPID_MODE1_buffer[key] = self.LOOPPID_MODE1[key]
                self.commit_bool = True
                # print(self.Valve_OUT[key], self.gmt_dt)
            else:
                pass

        for key in self.LOOPPID_MODE2:
            # print(key, self.Valve_OUT[key] != self.Valve_buffer[key], self.gmt_dt)
            if self.LOOPPID_MODE2[key] != self.LOOPPID_MODE2_buffer[key]:
                self.db.insert_data_into_stack(key + '_MODE2', self.early_dt, self.LOOPPID_MODE2_buffer[key],
                                                  self.early_gmt_dt)
                self.db.insert_data_into_stack(key + '_MODE2', self.dt, self.LOOPPID_MODE2[key], self.gmt_dt)
                self.LOOPPID_MODE2_buffer[key] = self.LOOPPID_MODE2[key]
                self.commit_bool = True
                # print(self.Valve_OUT[key], self.gmt_dt)
            else:
                pass

        for key in self.LOOPPID_MODE3:
            # print(key, self.Valve_OUT[key] != self.Valve_buffer[key], self.gmt_dt)
            if self.LOOPPID_MODE3[key] != self.LOOPPID_MODE3_buffer[key]:
                self.db.insert_data_into_stack(key + '_MODE3', self.early_dt, self.LOOPPID_MODE3_buffer[key],
                                                  self.early_gmt_dt)
                self.db.insert_data_into_stack(key + '_MODE3', self.dt, self.LOOPPID_MODE3[key], self.gmt_dt)
                self.LOOPPID_MODE3_buffer[key] = self.LOOPPID_MODE3[key]
                self.commit_bool = True
                # print(self.Valve_OUT[key], self.gmt_dt)
            else:
                pass

        # if no changes, write the data every fixed time interval
        # print(6)
        if self.para_LOOPPID >= self.rate_LOOPPID:
            for key in self.LOOPPID_EN:
                self.db.insert_data_into_stack(key + '_EN', self.dt, self.LOOPPID_EN[key], self.gmt_dt)
                self.LOOPPID_EN_buffer[key] = self.LOOPPID_EN[key]
            for key in self.LOOPPID_MODE0:
                self.db.insert_data_into_stack(key + '_MODE0', self.dt, self.LOOPPID_MODE0[key], self.gmt_dt)
                self.LOOPPID_MODE0_buffer[key] = self.LOOPPID_MODE0[key]
            for key in self.LOOPPID_MODE1:
                self.db.insert_data_into_stack(key + '_MODE1', self.dt, self.LOOPPID_MODE1[key], self.gmt_dt)
                self.LOOPPID_MODE1_buffer[key] = self.LOOPPID_MODE1[key]
            for key in self.LOOPPID_MODE2:
                self.db.insert_data_into_stack(key + '_MODE2', self.dt, self.LOOPPID_MODE2[key], self.gmt_dt)
                self.LOOPPID_MODE2_buffer[key] = self.LOOPPID_MODE2[key]
            for key in self.LOOPPID_MODE3:
                self.db.insert_data_into_stack(key + '_MODE3', self.dt, self.LOOPPID_MODE3[key], self.gmt_dt)
                self.LOOPPID_MODE3_buffer[key] = self.LOOPPID_MODE3[key]
            # write float data.
            for key in self.LOOPPID_OUT:
                self.db.insert_data_into_stack(key + '_OUT', self.dt, self.LOOPPID_OUT[key], self.gmt_dt)
                self.LOOPPID_OUT_buffer[key] = self.LOOPPID_OUT[key]
            for key in self.LOOPPID_IN:
                self.db.insert_data_into_stack(key + '_IN', self.dt, self.LOOPPID_IN[key], self.gmt_dt)
                self.LOOPPID_IN_buffer[key] = self.LOOPPID_IN[key]
            self.commit_bool = True
            self.para_LOOPPID = 0
        # print(7)

        if self.para_REAL >= self.rate_REAL:
            for key in self.LEFT_REAL_address:
                # print(key, self.LEFT_REAL_dic[key], self.gmt_dt)
                self.db.insert_data_into_stack(key, self.dt, self.LEFT_REAL_dic[key], self.gmt_dt)
                # print("write pressure transducer")
                self.commit_bool = True
            self.para_REAL = 0

        # commit the changes at last step only if it is time to write
        if self.commit_bool:
            # put alll commands into stack which is a pandas dataframe, reorder it by timestamp and then transform them into mysql queries
            self.db.sort_stack()
            self.db.convert_stack_into_queries()
            self.db.drop_stack()
            self.db.db.commit()

        print("Writing PLC data to database...")
        self.para_alarm += 1

        self.para_TT += 1
        self.para_PT += 1
        self.para_Valve += 1
        # self.para_Switch += 1
        self.para_LOOPPID += 1
        self.para_LOOP2PT += 1
        self.para_REAL += 1
        self.para_Din += 1
        self.para_FLAG += 1
        self.para_FF += 1
        self.para_PARAM_T += 1
        self.para_PARAM_I += 1
        self.para_PARAM_B += 1
        self.para_PARAM_F += 1
        self.para_TIME += 1
        self.para_LL += 1
        self.para_CAP += 1


class Message_Manager(threading.Thread):
    # add here the other alarm and database
    def __init__(self, global_time, timelock, alarm_stack, alarm_lock):
        super().__init__()
        self.alarm_init()
        self.txt_alarm_init()
        self.running = True
        self.global_time = global_time
        self.clock = self.global_time["clock"]  # hanging when on hold to slack -> internet connection/slack server
        self.db_time =  self.global_time["dbtime"] # hanging when disconnected from mysql
        self.slack_time = self.global_time["slacktime"]  # hanging when slack fail
        self.plc_time = self.global_time["plctime"]  # hanging when Beckhoff/NI/Arduino fail
        self.socketserver_time = self.global_time["sockettime"]  # hanging when socket to GUI fail
        self.time_lock = timelock

        self.alarm_stack = alarm_stack
        self.alarm_lock = alarm_lock
        self.para_alarm = env.MAINALARM_PARA
        self.rate_alarm = env.MAINALARM_RATE
        self.base_period = 1

    def alarm_init(self):
        # info about tencent mail settings
        self.host_server = "smtp.qq.com"
        self.sender_qq = "390282332"
        self.pwd = "bngozrzmzsbocafa"
        # self.sender_mail = "390282332@qq.com"
        # # self.receiver1_mail = "cdahl@northwestern.edu"
        # self.receiver1_mail = "runzezhang@foxmail.com"
        # self.mail_title = "Alarm from SBC"

        # server to pico watchdog

        # info about slack settings
        # SLACK_BOT_TOKEN is a linux enviromental variable saved locally on sbcslowcontrol machine
        # it can be fetched on slack app page in SBCAlarm app: https://api.slack.com/apps/A035X77RW64/general
        # if not_in_channel error type /invite @SBC_Alarm in channel
        try:
            self.slack_init()
        except (SlackApiError, Exception) as e:
            with self.alarm_lock:
                self.alarm_stack.update({"Slack Exception": "Slack Connection Error"})


    def slack_init(self):
        self.client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        # self.logger = logging.getLogger(__name__)
        self.channel_id = ""


    def txt_alarm_init(self):
        self.sender_email = "henry175nm@gmail.com"
        # self.receiver_email_list = ["runzezhang26@outlook.com"]
        # self.receiver_email_list = ["runzezhang26@outlook.com","2249992847@txt.att.net"]
        self.receiver_email_list = ["runzezhang26@outlook.com", "chami@ucsb.edu"
            , "mtrask@ucsb.edu", "hlippincott@ucsb.edu", "4357142170@tmomail.net","haleyfogg@ucsb.edu"]
        # change receiver email to phonenumber@domain to send text message
        self.subject = "Henry's Panel Alarm"
        self.body = "This is a test email sent using Python and Gmail's SMTP server."
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.smtp_username = "henry175nm@gmail.com"

        self.smtp_password = os.environ.get("GMAIL_TOKEN")
        self.email_para = sec.BROAD_CAST_PARA
        self.email_rate = sec.BROAD_CAST_RATE
    def alarm_module(self, alarm_received):
        with self.alarm_lock:
            alarm_received.update(self.alarm_stack)
        with self.time_lock:
            self.global_time.update({"slacktime": datetime_in_1e5micro()})

        self.run_once(alarm_received)

    def send_email_old(self, message):
        # Create a MIMEText object to represent the email body
        self.message = MIMEMultipart()
        self.message["From"] = self.sender_email
        self.message["To"] = ", ".join(self.receiver_email_list)
        self.message["Subject"] = self.subject
        self.message.attach(MIMEText(message, "plain"))

        # Establish a connection to the SMTP server
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
            # Login to your Gmail account
            server.login(self.smtp_username, self.smtp_password)

            # Send the email
            for recipient_email in self.receiver_email_list:
                server.sendmail(self.sender_email, recipient_email, self.message.as_string())
        print(self.message.as_string())


    def send_email(self, message,server):
        # Create a MIMEText object to represent the email body
        self.message = MIMEMultipart()
        self.message["From"] = self.sender_email
        self.message["To"] = ", ".join(self.receiver_email_list)
        self.message["Subject"] = self.subject
        self.message.attach(MIMEText(message, "plain"))

        # Send the email
        for recipient_email in self.receiver_email_list:
            server.sendmail(self.sender_email, recipient_email, self.message.as_string())
        print("email content",self.message.as_string())

    def slack_alarm(self, message):
        # Call the conversations.list method using the WebClient
        result = self.client.chat_postMessage(
            channel=self.channel_id,
            text=str(message)
            # You could also use a blocks[] array to send richer content
        )
        # Print result, which includes information about the message (like TS)

        print("slackalarm",result)


    def slack_alarm_fake(self, message):
        # try:
        self.client_fake = WebClient(token="1111")
        # Call the conversations.list method using the WebClient
        result = self.client_fake.chat_postMessage(
            channel=self.channel_id,
            text=str(message)

            # You could also use a blocks[] array to send richer content
        )
        # Print result, which includes information about the message (like TS)

        print("slackalarm",result)

        # except SlackApiError as e:
        #     with self.alarm_lock:
        #         self.alarm_stack.update({"Slack Exception": "Slack Connection Error"})
        #     print("Slack",f"Error1: {e}", self.alarm_stack)

    def run(self):
        alarm_received = {}
        while self.running:
            try:
                self.alarm_module(alarm_received)
                
                time.sleep(self.base_period)

            except (SlackApiError,Exception) as e:
                with self.alarm_lock:
                    self.alarm_stack.update({"Slack/Txt Exception": "Slack/Txt Connection Error"})
                print("Slack/txt exception Error2",e)
                # restart itself
                time.sleep(self.base_period*60)
                break
        self.run()
        
    def run_once(self, alarm_received):


        print("slack/txt", alarm_received)
        print("Message Manager running ", self.global_time["slacktime"])

        if self.para_alarm >= self.rate_alarm:
            if alarm_received != {}:
                print("alarm received", alarm_received)
                msg = self.join_stack_into_message(alarm_received)
                msg = str(self.global_time["slacktime"])+ msg
                # mute the alarms for debugging
                context = ssl.create_default_context()
                try:
                    self.slack_alarm(msg)
                except Exception as e:
                    print("slack sending failed:", repr(e))

                try:
                    with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                        server.login(self.smtp_username, self.smtp_password)
                        self.send_email(msg, server)
                except Exception as e:
                    print("Email sending failed:", repr(e))



            # and clear the alarm stack
            with self.alarm_lock:
                self.alarm_stack.clear()
                alarm_received.clear()
                print("alarm stack cleared", self.alarm_stack, alarm_received)
            self.para_alarm = 0
        self.para_alarm += 1



    def join_stack_into_message(self, dic):
        message = ""
        if len(dic) >= 1:
            for key in dic:
                message = message + "\n" + dic[key]
        return message



class LocalWatchdog(threading.Thread):
    def __init__(self, global_time, timelock, alarm_stack, alarm_lock):
        # alarm msg is different from coupp msg
        super().__init__()
        self.global_time = global_time
        self.timelock = timelock
        self.alarm_db = COUPP_database()
        self.alarm_stack = alarm_stack
        self.alarm_lock = alarm_lock
        self.running = True
        # time parameters
        self.clock = self.global_time["clock"]  # hanging when on hold to slack -> internet connection/slack server
        self.db_time = self.global_time["dbtime"]  # hanging when disconnected from mysql
        self.slack_time = self.global_time["slacktime"]  # hanging when ssh fail or coupp mysql fail
        self.plc_time = self.global_time["plctime"]  # hanging when Beckhoff/NI/Arduino fail
        self.socketserver_time = self.global_time["sockettime"]  # hanging when socket to GUI fail
        self.para_coupp = env.COUPP_trigger_PARA
        self.rate_coupp = env.COUPP_trigger_RATE
        self.mid_coupp = env.COUPP_trigger_MID
        self.para_alarm = env.MAINALARM_PARA
        self.rate_alarm = env.MAINALARM_RATE
        self.para_long_alarm = env.MAINALARM_LONG_PARA
        self.rate_long_alarm = env.MAINALARM_LONG_RATE
        self.database_timeout = env.DATABASE_HOLD
        self.plc_timeout = env.PLC_HOLD
        self.socket_timeout = env.SOCKET_HOLD
        self.slack_timeout = env.BROAD_CAST_HOLD
        self.base_period = 1

    def run(self):
        alarm_received = {}
        while self.running:
            try:

                with self.timelock:
                    self.global_time.update({"clock":datetime_in_1e5micro()})
                    # update all times
                    self.clock = self.global_time[
                        "clock"]  # hanging when on hold to slack -> internet connection/slack server
                    self.db_time = self.global_time["dbtime"]  # hanging when disconnected from mysql

                    self.slack_time = self.global_time["slacktime"]  # hanging when ssh fail or coupp mysql fail
                    self.plc_time = self.global_time["plctime"]  # hanging when Beckhoff/NI/Arduino fail
                    self.socketserver_time = self.global_time["sockettime"]

                print("Local watchdog running", self.global_time["clock"], self.global_time["plctime"])

                # Valid when plc is updating.
                # otherwise alarm the plc is disconnected or on hold, add alarm to alarm stack
                # We only consider time_out may happen in socket connections here and socket module will restart itself
                # because it can detect timeout signal by itself
                # Other module, we may just consider that the disconnection can happen and they will restart themselves
                # But good to know time_out and manually restart them
                if (self.clock - self.plc_time).total_seconds() > self.plc_timeout:
                    self.alarm_stack.update({"PLC CONNECTION TIMEOUT": "PLC hasn't update long than {time} s".format(
                        time=self.plc_timeout)})
                # In principle, no need to exist bc if it timeout, COUPP txt message will be sent out,
                # disabled for Henry
                # if (self.clock - self.slack_time).total_seconds() > self.slack_timeout:
                #     self.alarm_stack.update({"SLACK TIMEOUT": "slack hasn't update long than {time} s".format(
                #         time=self.slack_timeout)})
                # because when no client, the server is always on hold
                # if (self.clock - self.socketserver_time).total_seconds() > self.socket_timeout:
                #     alarm_received.update({"SOCKET TIMEOUT": "SOCKET TO GUI hasn't update long than {time} s".format(time=self.socket_timeout)})
                if (self.clock - self.db_time).total_seconds() > self.database_timeout:
                    self.alarm_stack.update({"DATABASE TIMEOUT": "Database hasn't update long than {time} s".format(
                        time=self.database_timeout)})
                with self.alarm_lock:
                    alarm_received.update(self.alarm_stack)
                    alarm_received_txt = self.join_stack_into_message(alarm_received)

                if self.para_alarm >= self.rate_alarm:

                    # send alarm msg to database, Otherwise, send text message about alarm
                    # if alarm_received_txt == "":
                    #     self.alarm_db.ssh_write()
                    # else:
                    #     self.alarm_db.ssh_alarm(message=alarm_received_txt)
                    self.para_alarm = 0
                    # loop is active in case slack channel isinactive.
                    # this is 300s loop, if longer than this, the alarms will be cleared out.
                    if self.para_long_alarm >= self.rate_long_alarm:
                        with self.alarm_lock:
                            alarm_received.clear()
                            self.alarm_stack.clear()
                        self.para_long_alarm = 0
                self.para_alarm += 1
                self.para_long_alarm += 1
                self.para_coupp = 0
                time.sleep(self.base_period)

            except (sshtunnel.BaseSSHTunnelForwarderError, pymysql.Error,Exception)  as e:
                if self.para_coupp <= self.mid_coupp:
                    with self.alarm_lock:
                        self.alarm_stack.update({"COUPP_server_connection_error": "Failed to connected to watchdog machine "
                                                                              "on COUPP server. Restarting"})
                elif  self.para_coupp >= self.rate_coupp:
                    self.para_coupp = 0
                self.para_coupp += 1 # now the COUPP connection message will trigger twice per hour:
                print("watchdog Error",e)
                # restart itself
                time.sleep(self.base_period * 60)
                break
        self.run()

    def join_stack_into_message(self, dic):
        message = ""
        if len(dic) >= 1:
            for key in dic:
                message = message + "\n" + dic[key]
        return message


class UpdateServer(threading.Thread):
    def __init__(self, plc_data, plc_lock, command_data, command_lock, global_time, timelock, alarm_lock, alarm_stack):
        super().__init__()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.global_time = global_time
        self.sockettime = global_time["sockettime"]
        self.timelock = timelock
        self.host = '127.0.0.1'
        self.port = 6666
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print("Server listening on {host}:{port}".format(host=self.host, port = self.port))

        self.plc_data = plc_data
        self.plc_lock = plc_lock
        self.command_data = command_data
        self.command_lock = command_lock
        self.alarm_lock = alarm_lock
        self.alarm_stack = alarm_stack
        self.period = 1

        # troubleshooting: print out the data to check if all RTDs and PTs are being sent to the GUI
        # for element in self.plc_data:
        #     print(element, self.plc_data[element])

        self.data_package = pickle.dumps(self.plc_data)

    def run(self):
        self.Running = True


        while self.Running:
            try:
                conn, addr = self.server_socket.accept()

                print(f"Connection from {addr}")

                # Set a timeout for socket operations to 10 seconds
                conn.settimeout(10)
                while True:
                    with self.timelock:
                        self.global_time.update({"sockettime":datetime_in_1e5micro()})
                        print("Socket Server Updating", self.global_time["sockettime"])

                    received_data = pickle.loads(self.receive_data(conn))
                    self.update_data_signal(received_data)
                    #pack data and send out

                    self.pack_data(conn)


                    time.sleep(self.period)  # Sleep for 1 seconds before sending data again

            except socket.timeout:
                print("Connection timed out. Restarting server...")
                conn.close()
            except BrokenPipeError:
                print("Client disconnected. Waiting for the next connection...")
                conn.close()  # Sleep for 1 second before sending data again
            except Exception as e:
                print(f"Exception: {e}")
                conn.close()
            finally:
                # with self.alarm_lock:
                #     self.alarm_stack.update({"Socket Server updating Exception":"Socket Server updating loop broke. Restarting..."})
                break

        self.run()

    def stop(self):
        self.server_socket.close()
        self.Running = False

    def update_data_signal(self, received_dict):
        with self.command_lock:
            self.command_data.update(received_dict)
        # print("command data in server socket", self.command_data)
    def pack_data(self, conn):
        data_transfer = pickle.dumps(self.plc_data)

        # Send JSON data to the client
        conn.sendall(len(data_transfer).to_bytes(4, byteorder='big'))

        # Send the serialized data in chunks
        for i in range(0, len(data_transfer), 1024):
            chunk = data_transfer[i:i + 1024]
            conn.sendall(chunk)
    def receive_data(self, conn):
        data_length_bytes = conn.recv(4)
        data_length = struct.unpack('!I', data_length_bytes)[0]

        # Receive the serialized data in chunks
        received_data = b''
        while len(received_data) < data_length:
            chunk = conn.recv(min(1024, data_length - len(received_data)))
            if not chunk:
                break
            received_data += chunk
        return received_data


class MainClass():
    def __init__(self):
        self.plc_data = copy.deepcopy(env.DIC_PACK)
        self.global_time={"plctime":datetime_in_1e5micro(),"dbtime":datetime_in_1e5micro(),"slacktime":datetime_in_1e5micro(),"sockettime":datetime_in_1e5micro(),
                          "clock":datetime_in_1e5micro()}
        self.plc_lock = threading.Lock()
        self.command_data = {}
        self.command_lock = threading.Lock()
        self.alarm_stack  = {}
        self.alarm_lock = threading.Lock()
        self.timelock = threading.Lock()
        self.StartUpdater()


    def StartUpdater(self):

        # Read PLC value on another thread
        self.threadPLC = UpdatePLC(plc_data=self.plc_data, plc_lock=self.plc_lock, command_data=self.command_data,
                                   command_lock=self.command_lock, global_time=self.global_time, timelock=self.timelock,
                                   alarm_stack=self.alarm_stack, alarm_lock=self.alarm_lock)

        self.threadDatabase = UpdateDataBase(plc_data=self.plc_data, plc_lock=self.plc_lock, global_time=self.global_time,
                                             timelock=self.timelock, alarm_stack=self.alarm_stack, alarm_lock=self.alarm_lock)

        self.threadWatchdog = LocalWatchdog(global_time=self.global_time,
                                            timelock=self.timelock,
                                            alarm_stack=self.alarm_stack, alarm_lock=self.alarm_lock)

        self.threadSocket = UpdateServer(plc_data=self.plc_data, plc_lock=self.plc_lock, command_data=self.command_data,
                                         command_lock=self.command_lock, global_time=self.global_time,
                                         timelock=self.timelock, alarm_lock=self.alarm_lock, alarm_stack=self.alarm_stack)

        self.threadMessager = Message_Manager(global_time=self.global_time, timelock=self.timelock,
                                              alarm_stack=self.alarm_stack, alarm_lock=self.alarm_lock)

        # wait for PLC initialization finished
        self.threadPLC.start()
        time.sleep(0.5)
        self.threadDatabase.start()
        time.sleep(0.1)
        self.threadWatchdog.start()
        time.sleep(0.1)
        self.threadSocket.start()
        time.sleep(0.1)
        self.threadMessager.start()


    def StopUpdater(self):
        self.threadPLC.join()
        time.sleep(1)
        self.threadDatabase.join()
        time.sleep(1)
        self.threadWatchdog.join()
        time.sleep(1)
        self.threadSocket.join()
        time.sleep(1)
        self.threadMessager.join()
        time.sleep(1)
        for i in range(10):
            print(i)
            time.sleep(1)




if __name__ == "__main__":
    MC = MainClass()