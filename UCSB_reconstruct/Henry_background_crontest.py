# """
# Class PLC is used to read/write via modbus to the temperature PLC
#
# To read the variable, just call the ReadAll() method
# To write to a variable, call the proper setXXX() method
#
# By: Mathieu Laurin
#
# v1.0 Initial code 25/11/19 ML
# v1.1 Initialize values, flag when values are updated more modbus variables 04/03/20 ML
# """
# #
# # import struct, time, zmq, sys, pickle, copy, logging, threading, queue, socket, json
# # import numpy as np
# # import pymodbus.exceptions
# # import sshtunnel
# # from SBC_watchdog_database import *
# # from email.mime.text import MIMEText
# # from email.header import Header
# # from smtplib import SMTP_SSL
# # import requests
# # import logging, os
# # from slack_sdk import WebClient
# # from slack_sdk.errors import SlackApiError
# # import SBC_env as env
# # import SBC_alarm_autoload as AL
# #
# # # delete random number package when you read real data from PLC
# # import random
# # from pymodbus.client.sync import ModbusTcpClient
# #
# # # Initialization of Address, Value Matrix
# #
# # logging.basicConfig(filename="/home/hep/sbc_error_log.log")
# # sys._excepthook = sys.excepthook


def test_crontab(string):
    file_path = '/home/hep/bkglog.txt'
    with open(file_path, 'w') as file:
        file.write(string + '\n')

# # def exception_hook(exctype, value, traceback):
# #     print("ExceptType: ", exctype, "Value: ", value, "Traceback: ", traceback)
# #     # sys._excepthook(exctype, value, traceback)
# #     sys.exit(1)
# #
# #
# # sys.excepthook = exception_hook
#
#
# # output address to attribute function in FP ()
# def FPADS_OUT_AT(outaddress):
#     # 1e5 digit
#     e5 = outaddress // 10000
#     e4 = (outaddress % 10000) // 1000
#     e3 = (outaddress % 1000) // 100
#     e2 = (outaddress % 100) // 10
#     e1 = (outaddress % 10) // 1
#     new_e5 = e5 - 2
#     new_e4 = e4
#     new_e321 = (e3 * 100 + e2 * 10 + e1) * 4
#     new_address = new_e5 * 10000 + new_e4 * 1000 + new_e321
#     print(e5, e4, e3, e2, e1)
#     print(new_address)
#     return new_address
#
#
# class PLC:
#     def __init__(self, plc_data, plc_lock, command_data, command_lock, alarm_stack, alarm_lock):
#         self.plc_data = plc_data
#         self.plc_lock = plc_lock
#         self.command_data = command_data
#         self.command_lock = command_lock
#         self.alarm_stack =  alarm_stack
#         self.alarm_lock = alarm_lock
#         IP_NI = "192.168.137.62"
#         PORT_NI = 502
#
#         self.Client_NI = ModbusTcpClient(IP_NI, port=PORT_NI)
#         try:
#             self.Connected_NI = self.Client_NI.connect()
#             print("NI connected: " + str(self.Connected_NI))
#         except Exception as e:
#             print("NI connection exceptions")
#
#         IP_BO = "192.168.137.11"
#         PORT_BO = 502
#         self.Client_BO = ModbusTcpClient(IP_BO, port=PORT_BO)
#         try:
#             self.Connected_BO = self.Client_BO.connect()
#             print(" Beckoff connected: " + str(self.Connected_BO))
#         except Exception as e:
#             print("BO connection exceptions")
#
#         IP_AD = "192.168.137.150"
#         PORT_AD = 502
#         self.Client_AD = ModbusTcpClient(IP_AD, port=PORT_AD)
#         try:
#             self.Connected_AD = self.Client_AD.connect()
#             print(" Ardunio connected: " + str(self.Connected_AD))
#         except Exception as e:
#             print("AD connection exceptions")
#
#         # wait 1 second to init
#         time.sleep(1)
#
#         self.TT_FP_address = copy.copy(env.TT_FP_ADDRESS)
#
#         self.TT_BO_address = copy.copy(env.TT_BO_ADDRESS)
#
#         self.PT_address = copy.copy(env.PT_ADDRESS)
#
#         self.LEFT_REAL_address = copy.copy(env.LEFT_REAL_ADDRESS)
#
#         self.AD_address = copy.copy(env.AD_ADDRESS)
#
#         self.TT_FP_dic = copy.copy(env.TT_FP_DIC)
#
#         self.TT_BO_dic = copy.copy(env.TT_BO_DIC)
#
#         self.PT_dic = copy.copy(env.PT_DIC)
#
#         self.LEFT_REAL_dic = copy.copy(env.LEFT_REAL_DIC)
#         self.AD_dic = copy.copy(env.AD_DIC)
#
#         self.TT_FP_LowLimit = copy.copy(env.TT_FP_LOWLIMIT)
#
#         self.TT_FP_HighLimit = copy.copy(env.TT_FP_HIGHLIMIT)
#
#         self.TT_BO_LowLimit = copy.copy(env.TT_BO_LOWLIMIT)
#
#         self.TT_BO_HighLimit = copy.copy(env.TT_BO_HIGHLIMIT)
#
#         self.PT_LowLimit = copy.copy(env.PT_LOWLIMIT)
#         self.PT_HighLimit = copy.copy(env.PT_HIGHLIMIT)
#
#         self.LEFT_REAL_HighLimit = copy.copy(env.LEFT_REAL_HIGHLIMIT)
#         self.LEFT_REAL_LowLimit = copy.copy(env.LEFT_REAL_LOWLIMIT)
#
#         self.AD_HighLimit = copy.copy(env.AD_HIGHLIMIT)
#         self.AD_LowLimit = copy.copy(env.AD_LOWLIMIT)
#
#         self.TT_FP_Activated = copy.copy(env.TT_FP_ACTIVATED)
#
#         self.TT_BO_Activated = copy.copy(env.TT_BO_ACTIVATED)
#
#         self.PT_Activated = copy.copy(env.PT_ACTIVATED)
#         self.LEFT_REAL_Activated = copy.copy(env.LEFT_REAL_ACTIVATED)
#         self.AD_Activated = copy.copy(env.AD_ACTIVATED)
#
#         self.TT_FP_Alarm = copy.copy(env.TT_FP_ALARM)
#
#         self.TT_BO_Alarm = copy.copy(env.TT_BO_ALARM)
#
#         self.PT_Alarm = copy.copy(env.PT_ALARM)
#         self.LEFT_REAL_Alarm = copy.copy(env.LEFT_REAL_ALARM)
#         self.AD_Alarm = copy.copy(env.AD_ALARM)
#         self.MainAlarm = copy.copy(env.MAINALARM)
#         self.MAN_SET = copy.copy(env.MAN_SET)
#         self.nTT_BO = copy.copy(env.NTT_BO)
#         self.nTT_FP = copy.copy(env.NTT_FP)
#         self.nPT = copy.copy(env.NPT)
#         self.nREAL = copy.copy(env.NREAL)
#
#         self.TT_BO_setting = copy.copy(env.TT_BO_SETTING)
#         self.nTT_BO_Attribute = copy.copy(env.NTT_BO_ATTRIBUTE)
#         self.PT_setting = copy.copy(env.PT_SETTING)
#         self.nPT_Attribute = copy.copy(env.NPT_ATTRIBUTE)
#
#         self.Switch_address = copy.copy(env.SWITCH_ADDRESS)
#         self.nSwitch = copy.copy(env.NSWITCH)
#         self.Switch = copy.copy(env.SWITCH)
#         self.Switch_OUT = copy.copy(env.SWITCH_OUT)
#         self.Switch_MAN = copy.copy(env.SWITCH_MAN)
#         self.Switch_INTLKD = copy.copy(env.SWITCH_INTLKD)
#         self.Switch_ERR = copy.copy(env.SWITCH_ERR)
#
#         self.Din_address = copy.copy(env.DIN_ADDRESS)
#         self.nDin = copy.copy(env.NDIN)
#         self.Din = copy.copy(env.DIN)
#         self.Din_dic = copy.copy(env.DIN_DIC)
#         self.Din_LowLimit = copy.copy(env.DIN_LOWLIMIT)
#         self.Din_HighLimit = copy.copy(env.DIN_HIGHLIMIT)
#         self.Din_Activated = copy.copy(env.DIN_ACTIVATED)
#         self.Din_Alarm = copy.copy(env.DIN_ALARM)
#
#         self.valve_address = copy.copy(env.VALVE_ADDRESS)
#         self.nValve = copy.copy(env.NVALVE)
#         self.Valve = copy.copy(env.VALVE)
#         self.Valve_OUT = copy.copy(env.VALVE_OUT)
#         self.Valve_MAN = copy.copy(env.VALVE_MAN)
#         self.Valve_INTLKD = copy.copy(env.VALVE_INTLKD)
#         self.Valve_ERR = copy.copy(env.VALVE_ERR)
#         self.Valve_Busy = copy.copy(env.VALVE_BUSY)
#
#         self.LOOPPID_ADR_BASE = copy.copy(env.LOOPPID_ADR_BASE)
#         self.LOOPPID_MODE0 = copy.copy(env.LOOPPID_MODE0)
#         self.LOOPPID_MODE1 = copy.copy(env.LOOPPID_MODE1)
#         self.LOOPPID_MODE2 = copy.copy(env.LOOPPID_MODE2)
#         self.LOOPPID_MODE3 = copy.copy(env.LOOPPID_MODE3)
#         self.LOOPPID_INTLKD = copy.copy(env.LOOPPID_INTLKD)
#         self.LOOPPID_MAN = copy.copy(env.LOOPPID_MAN)
#         self.LOOPPID_ERR = copy.copy(env.LOOPPID_ERR)
#         self.LOOPPID_SATHI = copy.copy(env.LOOPPID_SATHI)
#         self.LOOPPID_SATLO = copy.copy(env.LOOPPID_SATLO)
#         self.LOOPPID_EN = copy.copy(env.LOOPPID_EN)
#         self.LOOPPID_OUT = copy.copy(env.LOOPPID_OUT)
#         self.LOOPPID_IN = copy.copy(env.LOOPPID_IN)
#         self.LOOPPID_HI_LIM = copy.copy(env.LOOPPID_HI_LIM)
#         self.LOOPPID_LO_LIM = copy.copy(env.LOOPPID_LO_LIM)
#         self.LOOPPID_SET0 = copy.copy(env.LOOPPID_SET0)
#         self.LOOPPID_SET1 = copy.copy(env.LOOPPID_SET1)
#         self.LOOPPID_SET2 = copy.copy(env.LOOPPID_SET2)
#         self.LOOPPID_SET3 = copy.copy(env.LOOPPID_SET3)
#         self.LOOPPID_Busy = copy.copy(env.LOOPPID_BUSY)
#         self.LOOPPID_Activated = copy.copy(env.LOOPPID_ACTIVATED)
#         self.LOOPPID_Alarm = copy.copy(env.LOOPPID_ALARM)
#         self.LOOPPID_Alarm_HighLimit = copy.copy(env.LOOPPID_ALARM_HI_LIM)
#         self.LOOPPID_Alarm_LowLimit = copy.copy(env.LOOPPID_ALARM_LO_LIM)
#
#         self.LOOP2PT_ADR_BASE = copy.copy(env.LOOP2PT_ADR_BASE)
#         self.LOOP2PT_MODE0 = copy.copy(env.LOOP2PT_MODE0)
#         self.LOOP2PT_MODE1 = copy.copy(env.LOOP2PT_MODE1)
#         self.LOOP2PT_MODE2 = copy.copy(env.LOOP2PT_MODE2)
#         self.LOOP2PT_MODE3 = copy.copy(env.LOOP2PT_MODE3)
#         self.LOOP2PT_INTLKD = copy.copy(env.LOOP2PT_INTLKD)
#         self.LOOP2PT_MAN = copy.copy(env.LOOP2PT_MAN)
#         self.LOOP2PT_ERR = copy.copy(env.LOOP2PT_ERR)
#         self.LOOP2PT_OUT = copy.copy(env.LOOP2PT_OUT)
#         self.LOOP2PT_SET1 = copy.copy(env.LOOP2PT_SET1)
#         self.LOOP2PT_SET2 = copy.copy(env.LOOP2PT_SET2)
#         self.LOOP2PT_SET3 = copy.copy(env.LOOP2PT_SET3)
#         self.LOOP2PT_Busy = copy.copy(env.LOOP2PT_BUSY)
#
#         self.Procedure_address = copy.copy(env.PROCEDURE_ADDRESS)
#         self.Procedure_running = copy.copy(env.PROCEDURE_RUNNING)
#         self.Procedure_INTLKD = copy.copy(env.PROCEDURE_INTLKD)
#         self.Procedure_EXIT = copy.copy(env.PROCEDURE_EXIT)
#
#         self.INTLK_D_ADDRESS = copy.copy(env.INTLK_D_ADDRESS)
#         self.INTLK_D_DIC = copy.copy(env.INTLK_D_DIC)
#         self.INTLK_D_EN = copy.copy(env.INTLK_D_EN)
#         self.INTLK_D_COND = copy.copy(env.INTLK_D_COND)
#         self.INTLK_D_Busy = copy.copy(env.INTLK_D_BUSY)
#         self.INTLK_A_ADDRESS = copy.copy(env.INTLK_A_ADDRESS)
#         self.INTLK_A_DIC = copy.copy(env.INTLK_A_DIC)
#         self.INTLK_A_EN = copy.copy(env.INTLK_A_EN)
#         self.INTLK_A_COND = copy.copy(env.INTLK_A_COND)
#         self.INTLK_A_SET = copy.copy(env.INTLK_A_SET)
#         self.INTLK_A_Busy = copy.copy(env.INTLK_A_BUSY)
#
#         self.FLAG_ADDRESS = copy.copy(env.FLAG_ADDRESS)
#         self.FLAG_DIC = copy.copy(env.FLAG_DIC)
#         self.FLAG_INTLKD = copy.copy(env.FLAG_INTLKD)
#         self.FLAG_Busy = copy.copy(env.FLAG_BUSY)
#
#         self.FF_ADDRESS = copy.copy(env.FF_ADDRESS)
#         self.FF_DIC = copy.copy(env.FF_DIC)
#
#         self.PARAM_F_ADDRESS = copy.copy(env.PARAM_F_ADDRESS)
#         self.PARAM_F_DIC = copy.copy(env.PARAM_F_DIC)
#
#         self.PARAM_I_ADDRESS = copy.copy(env.PARAM_I_ADDRESS)
#         self.PARAM_I_DIC = copy.copy(env.PARAM_I_DIC)
#
#         self.PARAM_B_ADDRESS = copy.copy(env.PARAM_B_ADDRESS)
#         self.PARAM_B_DIC = copy.copy(env.PARAM_B_DIC)
#
#         self.PARAM_T_ADDRESS = copy.copy(env.PARAM_T_ADDRESS)
#         self.PARAM_T_DIC = copy.copy(env.PARAM_T_DIC)
#
#         self.TIME_ADDRESS = copy.copy(env.TIME_ADDRESS)
#         self.TIME_DIC = copy.copy(env.TIME_DIC)
#
#         self.Ini_Check = env.INI_CHECK
#
#         self.data_dic = {"data": {"TT": {
#             "FP": {"value": self.TT_FP_dic, "high": self.TT_FP_HighLimit, "low": self.TT_FP_LowLimit},
#             "BO": {"value": self.TT_BO_dic, "high": self.TT_BO_HighLimit, "low": self.TT_BO_LowLimit}},
#             "PT": {"value": self.PT_dic, "high": self.PT_HighLimit,
#                    "low": self.PT_LowLimit},
#             "LEFT_REAL": {"value": self.LEFT_REAL_dic, "high": self.LEFT_REAL_HighLimit,
#                           "low": self.LEFT_REAL_LowLimit},
#             "AD": {"value": self.AD_dic, "high": self.AD_HighLimit,
#                    "low": self.AD_LowLimit},
#             "Valve": {"OUT": self.Valve_OUT,
#                       "INTLKD": self.Valve_INTLKD,
#                       "MAN": self.Valve_MAN,
#                       "ERR": self.Valve_ERR,
#                       "Busy": self.Valve_Busy},
#             "Switch": {"OUT": self.Switch_OUT,
#                        "INTLKD": self.Switch_INTLKD,
#                        "MAN": self.Switch_MAN,
#                        "ERR": self.Switch_ERR},
#             "Din": {'value': self.Din_dic, "high": self.Din_HighLimit,
#                     "low": self.Din_LowLimit},
#             "LOOPPID": {"MODE0": self.LOOPPID_MODE0,
#                         "MODE1": self.LOOPPID_MODE1,
#                         "MODE2": self.LOOPPID_MODE2,
#                         "MODE3": self.LOOPPID_MODE3,
#                         "INTLKD": self.LOOPPID_INTLKD,
#                         "MAN": self.LOOPPID_MAN,
#                         "ERR": self.LOOPPID_ERR,
#                         "SATHI": self.LOOPPID_SATHI,
#                         "SATLO": self.LOOPPID_SATLO,
#                         "EN": self.LOOPPID_EN,
#                         "OUT": self.LOOPPID_OUT,
#                         "IN": self.LOOPPID_IN,
#                         "HI_LIM": self.LOOPPID_HI_LIM,
#                         "LO_LIM": self.LOOPPID_LO_LIM,
#                         "SET0": self.LOOPPID_SET0,
#                         "SET1": self.LOOPPID_SET1,
#                         "SET2": self.LOOPPID_SET2,
#                         "SET3": self.LOOPPID_SET3,
#                         "Busy": self.LOOPPID_Busy,
#                         "Alarm": self.LOOPPID_Alarm,
#                         "Alarm_HighLimit": self.LOOPPID_Alarm_HighLimit,
#                         "Alarm_LowLimit": self.LOOPPID_Alarm_LowLimit},
#             "LOOP2PT": {"MODE0": self.LOOP2PT_MODE0,
#                         "MODE1": self.LOOP2PT_MODE1,
#                         "MODE2": self.LOOP2PT_MODE2,
#                         "MODE3": self.LOOP2PT_MODE3,
#                         "INTLKD": self.LOOP2PT_INTLKD,
#                         "MAN": self.LOOP2PT_MAN,
#                         "ERR": self.LOOP2PT_ERR,
#                         "OUT": self.LOOP2PT_OUT,
#                         "SET1": self.LOOP2PT_SET1,
#                         "SET2": self.LOOP2PT_SET2,
#                         "SET3": self.LOOP2PT_SET3,
#                         "Busy": self.LOOP2PT_Busy},
#             "INTLK_D": {"value": self.INTLK_D_DIC,
#                         "EN": self.INTLK_D_EN,
#                         "COND": self.INTLK_D_COND,
#                         "Busy": self.INTLK_D_Busy},
#             "INTLK_A": {"value": self.INTLK_A_DIC,
#                         "EN": self.INTLK_A_EN,
#                         "COND": self.INTLK_A_COND,
#                         "SET": self.INTLK_A_SET,
#                         "Busy": self.INTLK_A_Busy},
#             "FLAG": {"value": self.FLAG_DIC,
#                      "INTLKD": self.FLAG_INTLKD,
#                      "Busy": self.FLAG_Busy},
#             "Procedure": {"Running": self.Procedure_running,
#                           "INTLKD": self.Procedure_INTLKD, "EXIT": self.Procedure_EXIT},
#             "FF": self.FF_DIC,
#             "PARA_I": self.PARAM_I_DIC,
#             "PARA_F": self.PARAM_F_DIC,
#             "PARA_B": self.PARAM_B_DIC,
#             "PARA_T": self.PARAM_T_DIC,
#             "TIME": self.TIME_DIC},
#             "Alarm": {"TT": {"FP": self.TT_FP_Alarm,
#                              "BO": self.TT_BO_Alarm},
#                       "PT": self.PT_Alarm,
#                       "LEFT_REAL": self.LEFT_REAL_Alarm,
#                       "AD": self.AD_Alarm,
#                       "Din": self.Din_Alarm,
#                       "LOOPPID": self.LOOPPID_Alarm},
#             "Active": {"TT": {"FP": self.TT_FP_Activated,
#                               "BO": self.TT_BO_Activated},
#                        "PT": self.PT_Activated,
#                        "LEFT_REAL": self.LEFT_REAL_Activated,
#                        "AD": self.AD_Activated,
#                        "Din": self.Din_Activated,
#                        "LOOPPID": self.LOOPPID_Activated,
#                        "INI_CHECK": self.Ini_Check},
#             "MainAlarm": self.MainAlarm
#         }
#
#         self.load_alarm_config()
#
#     def __del__(self):
#         self.Client_NI.close()
#         self.Client_BO.close()
#         self.Client_AD.close()
#
#     def load_alarm_config(self):
#         self.alarm_config = AL.Alarm_Setting()
#         self.alarm_config.read_Information()
#         for key in self.TT_FP_HighLimit:
#             try:
#                 self.TT_FP_HighLimit[key] = self.alarm_config.high_dic[key]
#             except:
#                 pass
#         for key in self.TT_BO_HighLimit:
#             try:
#                 self.TT_BO_HighLimit[key] = self.alarm_config.high_dic[key]
#             except:
#                 pass
#         for key in self.PT_HighLimit:
#             try:
#                 self.PT_HighLimit[key] = self.alarm_config.high_dic[key]
#             except:
#                 pass
#         for key in self.LEFT_REAL_HighLimit:
#             try:
#                 self.LEFT_REAL_HighLimit[key] = self.alarm_config.high_dic[key]
#             except:
#                 pass
#         for key in self.AD_HighLimit:
#             try:
#                 self.AD_HighLimit[key] = self.alarm_config.high_dic[key]
#             except:
#                 pass
#
#         for key in self.TT_FP_LowLimit:
#             try:
#                 self.TT_FP_LowLimit[key] = self.alarm_config.low_dic[key]
#             except:
#                 pass
#         for key in self.TT_BO_LowLimit:
#             try:
#                 self.TT_BO_LowLimit[key] = self.alarm_config.low_dic[key]
#             except:
#                 pass
#         for key in self.PT_LowLimit:
#             try:
#                 self.PT_LowLimit[key] = self.alarm_config.low_dic[key]
#             except:
#                 pass
#         for key in self.LEFT_REAL_LowLimit:
#             try:
#                 self.LEFT_REAL_LowLimit[key] = self.alarm_config.low_dic[key]
#             except:
#                 pass
#         for key in self.AD_LowLimit:
#             try:
#                 self.AD_LowLimit[key] = self.alarm_config.low_dic[key]
#             except:
#                 pass
#
#         for key in self.TT_FP_Activated:
#             try:
#                 self.TT_FP_Activated[key] = self.alarm_config.active_dic[key]
#             except:
#                 pass
#         for key in self.TT_BO_Activated:
#             try:
#                 self.TT_BO_Activated[key] = self.alarm_config.active_dic[key]
#             except:
#                 pass
#         for key in self.PT_Activated:
#             try:
#                 self.PT_Activated[key] = self.alarm_config.active_dic[key]
#             except:
#                 pass
#
#         for key in self.LEFT_REAL_Activated:
#             try:
#                 self.LEFT_REAL_Activated[key] = self.alarm_config.active_dic[key]
#             except:
#                 pass
#         for key in self.AD_Activated:
#             try:
#                 self.AD_Activated[key] = self.alarm_config.active_dic[key]
#             except:
#                 pass
#
#         for key in self.Din_LowLimit:
#             try:
#                 self.Din_LowLimit[key] = self.alarm_config.low_dic[key]
#             except:
#                 pass
#         for key in self.Din_HighLimit:
#             try:
#                 self.Din_HighLimit[key] = self.alarm_config.high_dic[key]
#             except:
#                 pass
#         for key in self.Din_Activated:
#             try:
#                 self.Din_Activated[key] = self.alarm_config.active_dic[key]
#             except:
#                 pass
#
#         for key in self.LOOPPID_Alarm_LowLimit:
#             # self.LOOPPID_SET_LO_LIM(address=self.LOOPPID_ADR_BASE[key],
#             #                         value=self.alarm_config.low_dic[key])
#             try:
#                 self.LOOPPID_Alarm_LowLimit[key] = self.alarm_config.low_dic[key]
#             except:
#                 pass
#
#         for key in self.LOOPPID_Alarm_HighLimit:
#             try:
#                 # self.LOOPPID_SET_HI_LIM(address=self.LOOPPID_ADR_BASE[key],
#                 #                         value=self.alarm_config.high_dic[key])
#                 self.LOOPPID_Alarm_HighLimit[key] = self.alarm_config.high_dic[key]
#             except:
#                 pass
#
#         for key in self.LOOPPID_Activated:
#             try:
#                 self.LOOPPID_Activated[key] = self.alarm_config.active_dic[key]
#             except:
#                 pass
#         # after the initilaztion, set the flag as true so that GUI can start load this config
#         with self.plc_lock:
#             self.data_dic["Active"]["INI_CHECK"] = True
#             self.plc_data.update(self.data_dic)
#
#
#
#     def ReadAll(self):
#
#         # and not holding
#         if not self.Client_NI.is_socket_open():
#             try:
#                 self.Client_NI.connect()
#                 print("NI Reconnected")
#             except Exception as e:
#                 print("NI Reconnect failed, trying again")
#                 # Wait for 5 seconds before retrying
#             finally:
#                 self.Read_NI_empty()
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"NI disconnection alarm":"National Instrument modbus is disconnected. Restarting..."})
#         else:
#             try:
#                 self.Read_NI()
#             except Exception as e:
#                 pass
#
#
#
#         #########################################################################
#         if not self.Client_BO.is_socket_open():
#             try:
#                 self.Client_BO.connect()
#                 print("BO Reconnected")
#             except Exception as e:
#                 print("BO Reconnect failed, trying again")
#                 # Wait for 5 seconds before retrying
#             finally:
#                 self.Read_BO_empty()
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"BO disconnection alarm":"Beckhoff modbus is disconnected. Restarting..."})
#         else:
#             try:
#                 self.Read_BO()
#             except Exception as e:
#                 pass
#
#         if not self.Client_AD.is_socket_open():
#             try:
#                 self.Client_AD.connect()
#                 print("AD Reconnected")
#             except Exception as e:
#                 print("AD Reconnect failed, trying again")
#                 # Wait for 5 seconds before retrying
#             finally:
#                 self.Read_AD_empty()
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"AD disconnection alarm":"Ardunio modbus is disconnected. Restarting..."})
#         else:
#             try:
#                 self.Read_AD()
#             except Exception as e:
#                 pass
#         with self.plc_lock:
#             self.plc_data.update(self.data_dic)
#
#
#
#             #########################################################################################################
#
#
#
#         return 0
#
#
#     def Read_NI(self):
#         Raw_RTDs_FP = {}
#         for key in self.TT_FP_address:
#             Raw_RTDs_FP[key] = self.Client_NI.read_holding_registers(self.TT_FP_address[key], count=2, unit=0x01)
#             # also transform C into K if value is not NULL
#             read_value = round(struct.unpack("<f", struct.pack("<HH", Raw_RTDs_FP[key].getRegister(1),
#                                                                Raw_RTDs_FP[key].getRegister(0)))[0], 3)
#             if read_value < 849:
#
#                 self.TT_FP_dic[key] = 273.15 + read_value
#             else:
#                 self.TT_FP_dic[key] = read_value
#     def Read_NI_empty(self):
#         for key in self.TT_FP_address:
#             self.TT_FP_dic[key] = 300
#
#     def Read_BO(self):
#         Raw_BO_TT_BO = {}
#         for key in self.TT_BO_address:
#             Raw_BO_TT_BO[key] = self.Client_BO.read_holding_registers(self.TT_BO_address[key], count=2, unit=0x01)
#             self.TT_BO_dic[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_BO_TT_BO[key].getRegister(1),
#                                                 Raw_BO_TT_BO[key].getRegister(0)))[0], 3)
#
#         Raw_BO_PT = {}
#         for key in self.PT_address:
#             Raw_BO_PT[key] = self.Client_BO.read_holding_registers(self.PT_address[key], count=2, unit=0x01)
#             self.PT_dic[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_BO_PT[key].getRegister(0 + 1),
#                                                 Raw_BO_PT[key].getRegister(0)))[0], 3)
#         # print("PT dic",self.PT_dic)
#
#         Raw_BO_REAL = {}
#         for key in self.LEFT_REAL_address:
#             Raw_BO_REAL[key] = self.Client_BO.read_holding_registers(self.LEFT_REAL_address[key], count=2,
#                                                                      unit=0x01)
#             self.LEFT_REAL_dic[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_BO_REAL[key].getRegister(0 + 1),
#                                                 Raw_BO_REAL[key].getRegister(0)))[0], 3)
#
#             # print(key, "'s' value is", self.PT_dic[key])
#
#         Raw_BO_Valve = {}
#         Raw_BO_Valve_OUT = {}
#         for key in self.valve_address:
#             Raw_BO_Valve[key] = self.Client_BO.read_holding_registers(self.valve_address[key], count=1, unit=0x01)
#             self.Valve[key] = struct.pack("H", Raw_BO_Valve[key].getRegister(0))
#
#             self.Valve_OUT[key] = self.ReadCoil(1, self.valve_address[key])
#             self.Valve_Busy[key] = self.ReadCoil(2, self.valve_address[key]) or self.ReadCoil(4, self.valve_address[
#                 key])
#             self.Valve_INTLKD[key] = self.ReadCoil(8, self.valve_address[key])
#             self.Valve_MAN[key] = self.ReadCoil(16, self.valve_address[key])
#             self.Valve_ERR[key] = self.ReadCoil(32, self.valve_address[key])
#
#         Raw_BO_Switch = {}
#
#         for key in self.Switch_address:
#             Raw_BO_Switch[key] = self.Client_BO.read_holding_registers(self.Switch_address[key], count=1, unit=0x01)
#             self.Switch[key] = struct.pack("H", Raw_BO_Switch[key].getRegister(0))
#
#             self.Switch_OUT[key] = self.ReadCoil(1, self.Switch_address[key])
#             self.Switch_INTLKD[key] = self.ReadCoil(8, self.Switch_address[key])
#             self.Switch_MAN[key] = self.ReadCoil(16, self.Switch_address[key])
#             self.Switch_ERR[key] = self.ReadCoil(32, self.Switch_address[key])
#
#         # Din's address is a tuple, first number is BO address, the second number is the digit
#         Raw_BO_Din = {}
#
#         for key in self.Din_address:
#             Raw_BO_Din[key] = self.Client_BO.read_holding_registers(self.Din_address[key][0], count=1, unit=0x01)
#             # print(Raw_BO_Din[key])
#             self.Din[key] = struct.pack("H", Raw_BO_Din[key].getRegister(0))
#
#             self.Din_dic[key] = self.ReadCoil(2 ** (self.Din_address[key][1]), self.Din_address[key][0])
#
#         Raw_LOOPPID_2 = {}
#         Raw_LOOPPID_4 = {}
#         Raw_LOOPPID_6 = {}
#         Raw_LOOPPID_8 = {}
#         Raw_LOOPPID_10 = {}
#         Raw_LOOPPID_12 = {}
#         Raw_LOOPPID_14 = {}
#         Raw_LOOPPID_16 = {}
#         for key in self.LOOPPID_ADR_BASE:
#             self.LOOPPID_MODE0[key] = self.ReadCoil(1, self.LOOPPID_ADR_BASE[key])
#             self.LOOPPID_MODE1[key] = self.ReadCoil(2, self.LOOPPID_ADR_BASE[key])
#             self.LOOPPID_MODE2[key] = self.ReadCoil(2 ** 2, self.LOOPPID_ADR_BASE[key])
#             self.LOOPPID_MODE3[key] = self.ReadCoil(2 ** 3, self.LOOPPID_ADR_BASE[key])
#             self.LOOPPID_INTLKD[key] = self.ReadCoil(2 ** 8, self.LOOPPID_ADR_BASE[key])
#             self.LOOPPID_MAN[key] = self.ReadCoil(2 ** 9, self.LOOPPID_ADR_BASE[key])
#             self.LOOPPID_ERR[key] = self.ReadCoil(2 ** 10, self.LOOPPID_ADR_BASE[key])
#             self.LOOPPID_SATHI[key] = self.ReadCoil(2 ** 11, self.LOOPPID_ADR_BASE[key])
#             self.LOOPPID_SATLO[key] = self.ReadCoil(2 ** 12, self.LOOPPID_ADR_BASE[key])
#             self.LOOPPID_EN[key] = self.ReadCoil(2 ** 15, self.LOOPPID_ADR_BASE[key])
#             Raw_LOOPPID_2[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 2, count=2,
#                                                                        unit=0x01)
#             Raw_LOOPPID_4[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 4, count=2,
#                                                                        unit=0x01)
#             Raw_LOOPPID_6[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 6, count=2,
#                                                                        unit=0x01)
#             Raw_LOOPPID_8[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 8, count=2,
#                                                                        unit=0x01)
#             Raw_LOOPPID_10[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 10, count=2,
#                                                                         unit=0x01)
#             Raw_LOOPPID_12[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 12, count=2,
#                                                                         unit=0x01)
#             Raw_LOOPPID_14[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 14, count=2,
#                                                                         unit=0x01)
#             Raw_LOOPPID_16[key] = self.Client_BO.read_holding_registers(self.LOOPPID_ADR_BASE[key] + 16, count=2,
#                                                                         unit=0x01)
#
#             self.LOOPPID_OUT[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_2[key].getRegister(1),
#                                                 Raw_LOOPPID_2[key].getRegister(0)))[0], 3)
#
#             self.LOOPPID_IN[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_4[key].getRegister(0 + 1),
#                                                 Raw_LOOPPID_4[key].getRegister(0)))[0], 3)
#             self.LOOPPID_HI_LIM[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_6[key].getRegister(0 + 1),
#                                                 Raw_LOOPPID_6[key].getRegister(0)))[0], 3)
#             self.LOOPPID_LO_LIM[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_8[key].getRegister(0 + 1),
#                                                 Raw_LOOPPID_8[key].getRegister(0)))[0], 3)
#             self.LOOPPID_SET0[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_10[key].getRegister(0 + 1),
#                                                 Raw_LOOPPID_10[key].getRegister(0)))[0], 3)
#             self.LOOPPID_SET1[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_12[key].getRegister(0 + 1),
#                                                 Raw_LOOPPID_12[key].getRegister(0)))[0], 3)
#             self.LOOPPID_SET2[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_14[key].getRegister(0 + 1),
#                                                 Raw_LOOPPID_14[key].getRegister(0)))[0], 3)
#             self.LOOPPID_SET3[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOPPID_16[key].getRegister(0 + 1),
#                                                 Raw_LOOPPID_16[key].getRegister(0)))[0], 3)
#
#             self.LOOPPID_Busy[key] = self.ReadCoil(2 ** 13, self.LOOPPID_ADR_BASE[key]) or self.ReadCoil(2 ** 14,
#                                                                                                          self.LOOPPID_ADR_BASE[
#                                                                                                              key])
#
#         ##########################################################################################
#
#         Raw_LOOP2PT_2 = {}
#         Raw_LOOP2PT_4 = {}
#         Raw_LOOP2PT_6 = {}
#
#         for key in self.LOOP2PT_ADR_BASE:
#             self.LOOP2PT_OUT[key] = self.ReadCoil(1, self.LOOP2PT_ADR_BASE[key])
#             self.LOOP2PT_INTLKD[key] = self.ReadCoil(2 ** 3, self.LOOP2PT_ADR_BASE[key])
#             self.LOOP2PT_MAN[key] = self.ReadCoil(2 ** 4, self.LOOP2PT_ADR_BASE[key])
#             self.LOOP2PT_ERR[key] = self.ReadCoil(2 ** 5, self.LOOP2PT_ADR_BASE[key])
#             self.LOOP2PT_MODE0[key] = self.ReadCoil(2 ** 6, self.LOOP2PT_ADR_BASE[key])
#             self.LOOP2PT_MODE1[key] = self.ReadCoil(2 ** 7, self.LOOP2PT_ADR_BASE[key])
#             self.LOOP2PT_MODE2[key] = self.ReadCoil(2 ** 8, self.LOOP2PT_ADR_BASE[key])
#             self.LOOP2PT_MODE3[key] = self.ReadCoil(2 ** 9, self.LOOP2PT_ADR_BASE[key])
#
#             Raw_LOOP2PT_2[key] = self.Client_BO.read_holding_registers(self.LOOP2PT_ADR_BASE[key] + 2, count=2,
#                                                                        unit=0x01)
#             Raw_LOOP2PT_4[key] = self.Client_BO.read_holding_registers(self.LOOP2PT_ADR_BASE[key] + 4, count=2,
#                                                                        unit=0x01)
#             Raw_LOOP2PT_6[key] = self.Client_BO.read_holding_registers(self.LOOP2PT_ADR_BASE[key] + 6, count=2,
#                                                                        unit=0x01)
#
#             self.LOOP2PT_SET1[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOP2PT_2[key].getRegister(1),
#                                                 Raw_LOOP2PT_2[key].getRegister(0)))[0], 3)
#
#             self.LOOP2PT_SET2[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOP2PT_4[key].getRegister(0 + 1),
#                                                 Raw_LOOP2PT_4[key].getRegister(0)))[0], 3)
#             self.LOOP2PT_SET3[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_LOOP2PT_6[key].getRegister(0 + 1),
#                                                 Raw_LOOP2PT_6[key].getRegister(0)))[0], 3)
#             self.LOOP2PT_Busy[key] = self.ReadCoil(2 ** 1, self.LOOP2PT_ADR_BASE[key]) or self.ReadCoil(
#                 2 ** 2, self.LOOP2PT_ADR_BASE[key])
#
#         ############################################################################################
#         # procedure
#         Raw_Procedure = {}
#         Raw_Procedure_OUT = {}
#         for key in self.Procedure_address:
#             Raw_Procedure[key] = self.Client_BO.read_holding_registers(self.Procedure_address[key] + 1, count=1,
#                                                                        unit=0x01)
#
#             self.Procedure_running[key] = self.ReadCoil(1, self.Procedure_address[key])
#             self.Procedure_INTLKD[key] = self.ReadCoil(2, self.Procedure_address[key])
#             self.Procedure_EXIT[key] = Raw_Procedure[key].getRegister(0)
#
#         ##################################################################################################
#         Raw_INTLK_A = {}
#         for key in self.INTLK_A_ADDRESS:
#             Raw_INTLK_A[key] = self.Client_BO.read_holding_registers(self.INTLK_A_ADDRESS[key] + 2, count=2,
#                                                                      unit=0x01)
#             self.INTLK_A_SET[key] = round(
#                 struct.unpack(">f", struct.pack(">HH", Raw_INTLK_A[key].getRegister(1),
#                                                 Raw_INTLK_A[key].getRegister(0)))[0], 3)
#             self.INTLK_A_DIC[key] = self.ReadCoil(1, self.INTLK_A_ADDRESS[key])
#             self.INTLK_A_EN[key] = self.ReadCoil(2 ** 1, self.INTLK_A_ADDRESS[key])
#             self.INTLK_A_COND[key] = self.ReadCoil(2 ** 2, self.INTLK_A_ADDRESS[key])
#             self.INTLK_A_Busy[key] = self.ReadCoil(2 ** 2, self.INTLK_A_ADDRESS[key]) or self.ReadCoil(
#                 2 ** 3, self.INTLK_A_ADDRESS[key])
#
#         for key in self.INTLK_D_ADDRESS:
#             self.INTLK_D_DIC[key] = self.ReadCoil(1, self.INTLK_D_ADDRESS[key])
#             self.INTLK_D_EN[key] = self.ReadCoil(2 ** 1, self.INTLK_D_ADDRESS[key])
#             self.INTLK_D_COND[key] = self.ReadCoil(2 ** 2, self.INTLK_D_ADDRESS[key])
#             self.INTLK_D_Busy[key] = self.ReadCoil(2 ** 2, self.INTLK_D_ADDRESS[key]) or self.ReadCoil(
#                 2 ** 3, self.INTLK_D_ADDRESS[key])
#
#         ############################################################################################
#         # FLAG
#         for key in self.FLAG_ADDRESS:
#             self.FLAG_DIC[key] = self.ReadCoil(1, self.FLAG_ADDRESS[key])
#             # print("\n",self.FLAG_DIC,"\n")
#             self.FLAG_INTLKD[key] = self.ReadCoil(2 ** 3, self.FLAG_ADDRESS[key])
#             self.FLAG_Busy[key] = self.ReadCoil(2 ** 1, self.FLAG_ADDRESS[key]) or self.ReadCoil(
#                 2 ** 2, self.FLAG_ADDRESS[key])
#
#         # print("PLC FLAG", self.FLAG_DIC, datetime.datetime.now())
#
#         #######################################################################################################
#
#         ##FF
#         Raw_FF = {}
#         for key in self.FF_ADDRESS:
#             Raw_FF[key] = self.Client_BO.read_holding_registers(self.FF_ADDRESS[key], count=2, unit=0x01)
#             self.FF_DIC[key] = \
#                 struct.unpack(">I", struct.pack(">HH", Raw_FF[key].getRegister(1), Raw_FF[key].getRegister(0)))[0]
#
#         # print("FF",self.FF_DIC)
#
#         ## PARAMETER
#         Raw_PARAM_F = {}
#         for key in self.PARAM_F_ADDRESS:
#             Raw_PARAM_F[key] = self.Client_BO.read_holding_registers(self.PARAM_F_ADDRESS[key], count=2, unit=0x01)
#             self.PARAM_F_DIC[key] = struct.unpack(">f", struct.pack(">HH", Raw_PARAM_F[key].getRegister(1),
#                                                                     Raw_PARAM_F[key].getRegister(0)))[0]
#
#         # print("PARAM_F", self.PARAM_F_DIC)
#
#         Raw_PARAM_I = {}
#         for key in self.PARAM_I_ADDRESS:
#             Raw_PARAM_I[key] = self.Client_BO.read_holding_registers(self.PARAM_I_ADDRESS[key], count=1, unit=0x01)
#             self.PARAM_I_DIC[key] = Raw_PARAM_I[key].getRegister(0)
#
#         # print("PARAM_I", self.PARAM_I_DIC)
#
#         for key in self.PARAM_B_ADDRESS:
#             self.PARAM_B_DIC[key] = self.ReadCoil(2 ** (self.PARAM_B_ADDRESS[key][1]), self.PARAM_B_ADDRESS[key][0])
#
#         # print("PARAM_B", self.PARAM_B_DIC)
#
#         Raw_PARAM_T = {}
#         for key in self.PARAM_T_ADDRESS:
#             Raw_PARAM_T[key] = self.Client_BO.read_holding_registers(self.PARAM_T_ADDRESS[key], count=2, unit=0x01)
#             self.PARAM_T_DIC[key] = struct.unpack(">I", struct.pack(">HH", Raw_PARAM_T[key].getRegister(1),
#                                                                     Raw_PARAM_T[key].getRegister(0)))[0]
#
#         # print("PARAM_T", self.PARAM_T_DIC)
#
#         ###TIME
#         Raw_TIME = {}
#         for key in self.TIME_ADDRESS:
#             Raw_TIME[key] = self.Client_BO.read_holding_registers(self.TIME_ADDRESS[key], count=2, unit=0x01)
#             self.TIME_DIC[key] = \
#                 struct.unpack(">I", struct.pack(">HH", Raw_TIME[key].getRegister(1), Raw_TIME[key].getRegister(0)))[
#                     0]
#         # print("TIME", self.TIME_DIC)
#
#
#     def Read_NI_empty(self):
#         for key in self.TT_FP_address:
#             self.TT_FP_dic[key] = 0
#
#     def Read_BO_empty(self):
#         for key in self.TT_BO_address:
#             self.TT_BO_dic[key] = 0
#
#         for key in self.PT_address:
#             self.PT_dic[key] = 0
#
#         for key in self.LEFT_REAL_address:
#             self.LEFT_REAL_dic[key] = 0
#
#             # print(key, "'s' value is", self.PT_dic[key])
#
#
#         for key in self.valve_address:
#
#             self.Valve_OUT[key] = 0
#             self.Valve_Busy[key] = 0
#             self.Valve_INTLKD[key] = 0
#             self.Valve_MAN[key] = 0
#             self.Valve_ERR[key] = 0
#
#         for key in self.Switch_address:
#             self.Switch_OUT[key] = 0
#             self.Switch_INTLKD[key] = 0
#             self.Switch_MAN[key] = 0
#             self.Switch_ERR[key] = 0
#
#         for key in self.Din_address:
#             self.Din_dic[key] = 0
#
#         for key in self.LOOPPID_ADR_BASE:
#             self.LOOPPID_OUT[key] = 0
#             self.LOOPPID_IN[key] = 0
#             self.LOOPPID_HI_LIM[key] = 0
#             self.LOOPPID_LO_LIM[key] = 0
#             self.LOOPPID_SET0[key] = 0
#             self.LOOPPID_SET1[key] = 0
#             self.LOOPPID_SET2[key] = 0
#             self.LOOPPID_SET3[key] = 0
#             self.LOOPPID_Busy[key] = 0
#
#         ##########################################################################################
#
#
#
#         for key in self.LOOP2PT_ADR_BASE:
#             self.LOOP2PT_SET1[key] = 0
#             self.LOOP2PT_SET2[key] = 0
#             self.LOOP2PT_SET3[key] = 0
#             self.LOOP2PT_Busy[key] = 0
#
#         ############################################################################################
#         # procedure
#
#         for key in self.Procedure_address:
#
#             self.Procedure_running[key] = 0
#             self.Procedure_INTLKD[key] = 0
#             self.Procedure_EXIT[key] = 0
#
#         ##################################################################################################
#
#         for key in self.INTLK_A_ADDRESS:
#
#             self.INTLK_A_DIC[key] = 0
#             self.INTLK_A_EN[key] = 0
#             self.INTLK_A_COND[key] = 0
#             self.INTLK_A_Busy[key] = 0
#
#         for key in self.INTLK_D_ADDRESS:
#             self.INTLK_D_DIC[key] = 0
#             self.INTLK_D_EN[key] = 0
#             self.INTLK_D_COND[key] = 0
#             self.INTLK_D_Busy[key] = 0
#
#         ############################################################################################
#         # FLAG
#         for key in self.FLAG_ADDRESS:
#             self.FLAG_DIC[key] = 0
#             self.FLAG_INTLKD[key] = 0
#             self.FLAG_Busy[key] = 0
#
#         # print("PLC FLAG", self.FLAG_DIC, datetime.datetime.now())
#
#         #######################################################################################################
#
#         ##FF
#         for key in self.FF_ADDRESS:
#             self.FF_DIC[key] = 0
#
#         ## PARAMETER
#         Raw_PARAM_F = {}
#         for key in self.PARAM_F_ADDRESS:
#             self.PARAM_F_DIC[key] = 0
#
#         for key in self.PARAM_I_ADDRESS:
#             self.PARAM_I_DIC[key] = 0
#
#         for key in self.PARAM_B_ADDRESS:
#             self.PARAM_B_DIC[key] = 0
#
#         for key in self.PARAM_T_ADDRESS:
#             self.PARAM_T_DIC[key] = 0
#
#         ###TIME
#         for key in self.TIME_ADDRESS:
#             self.TIME_DIC[key] = 0
#
#     def Read_AD(self):
#         Raw_AD = {}
#         Raw_inter_AD = {}
#         for key in self.AD_address:
#             Raw_AD[key] = self.Client_AD.read_holding_registers(self.AD_address[key], count=2, unit=0x01)
#             Raw_inter_AD[key] = \
#                 struct.unpack("<f", struct.pack("<HH", Raw_AD[key].getRegister(1), Raw_AD[key].getRegister(0)))[0]
#             if Raw_inter_AD[key] != -1:
#                 self.AD_dic[key] = round(Raw_inter_AD[key] / (Raw_inter_AD[key] + 1) * 100, 2)
#             else:
#                 self.AD_dic[key] = -1
#
#     def Read_AD_empty(self):
#         for key in self.AD_address:
#             self.AD_dic[key] = -1
#
#     def write_data(self, received_dict):
#         message = received_dict
#         # print("write data in plc module",message)
#         if not "MAN_SET" in message:
#             if message == {}:
#                 pass
#             else:
#                 for key in message:
#                     # print("key type",message[key]["type"])
#                     if message[key]["type"] == "valve":
#                         print("Valve", datetime_in_1e5micro())
#                         if message[key]["operation"] == "OPEN":
#                             self.WriteBase2(address=message[key]["address"])
#                         elif message[key]["operation"] == "CLOSE":
#                             self.WriteBase4(address=message[key]["address"])
#                         else:
#                             pass
#                         # write success signal
#
#                     if message[key]["type"] == "switch":
#                         if message[key]["operation"] == "ON":
#                             self.WriteBase2(address=message[key]["address"])
#                         elif message[key]["operation"] == "OFF":
#                             self.WriteBase4(address=message[key]["address"])
#                         else:
#                             pass
#                     elif message[key]["type"] == "TT":
#                         if message[key]["server"] == "BO":
#                             # Update is to decide whether write new Low/High limit values into bkg code
#                             if message[key]["operation"]["Update"]:
#                                 self.TT_BO_Activated[key] = message[key]["operation"]["Act"]
#                                 self.TT_BO_LowLimit[key] = message[key]["operation"]["LowLimit"]
#                                 self.TT_BO_HighLimit[key] = message[key]["operation"]["HighLimit"]
#                             else:
#                                 self.TT_BO_Activated[key] = message[key]["operation"]["Act"]
#                                 # print("check writing", key,self.TT_BO_Activated[key])
#
#                         elif message[key]["server"] == "FP":
#                             if message[key]["operation"]["Update"]:
#                                 self.TT_FP_Activated[key] = message[key]["operation"]["Act"]
#                                 self.TT_FP_LowLimit[key] = message[key]["operation"]["LowLimit"]
#                                 self.TT_FP_HighLimit[key] = message[key]["operation"]["HighLimit"]
#                             else:
#                                 self.TT_FP_Activated[key] = message[key]["operation"]["Act"]
#                         else:
#                             pass
#                     elif message[key]["type"] == "PT":
#                         if message[key]["server"] == "BO":
#                             if message[key]["operation"]["Update"]:
#                                 self.PT_Activated[key] = message[key]["operation"]["Act"]
#                                 self.PT_LowLimit[key] = message[key]["operation"]["LowLimit"]
#                                 self.PT_HighLimit[key] = message[key]["operation"]["HighLimit"]
#                             else:
#                                 self.PT_Activated[key] = message[key]["operation"]["Act"]
#                         else:
#                             pass
#                     elif message[key]["type"] == "LEFT":
#                         if message[key]["server"] == "BO":
#                             if message[key]["operation"]["Update"]:
#                                 self.LEFT_REAL_Activated[key] = message[key]["operation"]["Act"]
#                                 self.LEFT_REAL_LowLimit[key] = message[key]["operation"]["LowLimit"]
#                                 self.LEFT_REAL_HighLimit[key] = message[key]["operation"]["HighLimit"]
#                             else:
#                                 self.LEFT_REAL_Activated[key] = message[key]["operation"]["Act"]
#                         else:
#                             pass
#                     elif message[key]["type"] == "AD":
#                         if message[key]["server"] == "AD":
#                             if message[key]["operation"]["Update"]:
#                                 self.AD_Activated[key] = message[key]["operation"]["Act"]
#                                 self.AD_LowLimit[key] = message[key]["operation"]["LowLimit"]
#                                 self.AD_HighLimit[key] = message[key]["operation"]["HighLimit"]
#                             else:
#                                 self.AD_Activated[key] = message[key]["operation"]["Act"]
#                         else:
#                             pass
#
#                     elif message[key]["type"] == "Din":
#                         if message[key]["server"] == "BO":
#                             if message[key]["operation"]["Update"]:
#                                 self.Din_Activated[key] = message[key]["operation"]["Act"]
#                                 self.Din_LowLimit[key] = message[key]["operation"]["LowLimit"]
#                                 self.Din_HighLimit[key] = message[key]["operation"]["HighLimit"]
#                             else:
#                                 self.Din_Activated[key] = message[key]["operation"]["Act"]
#                         else:
#                             pass
#
#                     elif message[key]["type"] == "LOOPPID_alarm":
#                         if message[key]["server"] == "BO":
#                             if message[key]["operation"]["Update"]:
#                                 self.LOOPPID_Activated[key] = message[key]["operation"]["Act"]
#                                 # self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
#                                 #                             value=message[key]["operation"]["LowLimit"])
#                                 # self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
#                                 #                             value=message[key]["operation"]["HighLimit"])
#                                 self.LOOPPID_Alarm_HighLimit[key] = message[key]["operation"]["HighLimit"]
#                                 self.LOOPPID_Alarm_LowLimit[key] = message[key]["operation"]["LowLimit"]
#
#
#                             else:
#                                 self.LOOPPID_Activated[key] = message[key]["operation"]["Act"]
#                         else:
#                             pass
#
#                     elif message[key]["type"] == "Procedure":
#                         if message[key]["server"] == "BO":
#                             if message[key]["operation"]["Start"]:
#                                 self.WriteBase4(address=message[key]["address"])
#                             elif message[key]["operation"]["Stop"]:
#                                 self.WriteBase8(address=message[key]["address"])
#                             elif message[key]["operation"]["Abort"]:
#                                 self.WriteBase16(address=message[key]["address"])
#                             else:
#                                 pass
#                         else:
#                             pass
#
#                     elif message[key]["type"] == "Procedure_TS":
#                         if message[key]["server"] == "BO":
#                             if message[key]["operation"]["RST_FF"]:
#                                 self.WriteFF(self.FF_ADDRESS["TS_ADDREM_FF"])
#                             if message[key]["operation"]["update"]:
#                                 self.Write_BO_2_int16(self.PARAM_I_ADDRESS["TS_SEL"],
#                                                           message[key]["operation"]["SEL"])
#                                 self.Write_BO_2(self.PARAM_F_ADDRESS["TS_ADDREM_MASS"],
#                                                     message[key]["operation"]["ADDREM_MASS"])
#                                 self.Write_BO_2_int32(self.PARAM_T_ADDRESS["TS_ADDREM_MAXTIME"],
#                                                           round(float(message[key]["operation"]["MAXTIME"]) * 1000))
#
#                             else:
#                                 pass
#                         else:
#                             pass
#
#                     elif message[key]["type"] == "Procedure_PC":
#                         if message[key]["server"] == "BO":
#                             if message[key]["operation"]["ABORT_FF"]:
#                                 self.WriteFF(self.FF_ADDRESS["PCYCLE_ABORT_FF"])
#                             if message[key]["operation"]["FASTCOMP_FF"]:
#                                 self.WriteFF(self.FF_ADDRESS["PCYCLE_FASTCOMP_FF"])
#                             if message[key]["operation"]["SLOWCOMP_FF"]:
#                                 self.WriteFF(self.FF_ADDRESS["PCYCLE_SLOWCOMP_FF"])
#                             if message[key]["operation"]["CYLEQ_FF"]:
#                                 self.WriteFF(self.FF_ADDRESS["PCYCLE_CYLEQ_FF"])
#                             if message[key]["operation"]["ACCHARGE_FF"]:
#                                 self.WriteFF(self.FF_ADDRESS["PCYCLE_ACCHARGE_FF"])
#                             if message[key]["operation"]["CYLBLEED_FF"]:
#                                 self.WriteFF(self.FF_ADDRESS["PCYCLE_CYLBLEED_FF"])
#
#                             if message[key]["operation"]["update"]:
#                                 self.Write_BO_2(self.PARAM_F_ADDRESS["PSET"], message[key]["operation"]["PSET"])
#                                 self.Write_BO_2_int32(self.PARAM_T_ADDRESS["MAXEXPTIME"],
#                                                           round(float(message[key]["operation"]["MAXEXPTIME"]) * 1000))
#                                 self.Write_BO_2_int32(self.PARAM_T_ADDRESS["MAXEQTIME"],
#                                                           round(float(message[key]["operation"]["MAXEXQTIME"]) * 1000))
#                                 self.Write_BO_2(self.PARAM_F_ADDRESS["MAXEQPDIFF"],
#                                                     message[key]["operation"]["MAXEQPDIFF"])
#                                 self.Write_BO_2_int32(self.PARAM_T_ADDRESS["MAXACCTIME"],
#                                                           round(float(message[key]["operation"]["MAXACCTIME"]) * 1000))
#                                 self.Write_BO_2(self.PARAM_F_ADDRESS["MAXACCDPDT"],
#                                                     message[key]["operation"]["MAXACCDPDT"])
#
#                                 self.Write_BO_2_int32(self.PARAM_T_ADDRESS["MAXBLEEDTIME"],
#                                                           round(
#                                                               float(message[key]["operation"]["MAXBLEEDTIME"]) * 1000))
#                                 self.Write_BO_2(self.PARAM_F_ADDRESS["MAXBLEEDDPDT"],
#                                                     message[key]["operation"]["MAXBLEEDDPDT"])
#                                 self.Write_BO_2(self.PARAM_F_ADDRESS["SLOWCOMP_SET"],
#                                                     message[key]["operation"]["SLOWCOMP_SET"])
#
#                             else:
#                                 pass
#                         else:
#                             pass
#
#
#                     elif message[key]["type"] == "heater_power":
#                         if message[key]["operation"] == "EN":
#                             self.LOOPPID_OUT_ENA(address=message[key]["address"])
#                         elif message[key]["operation"] == "DISEN":
#                             self.LOOPPID_OUT_DIS(address=message[key]["address"])
#                         else:
#                             pass
#
#                         #
#                         # if message[key]["operation"] == "SETMODE":
#                         #     self.LOOPPID_SET_MODE(address = message[key]["address"], mode = message[key]["value"])
#                         # else:
#                         #     pass
#                     elif message[key]["type"] == "heater_para":
#                         if message[key]["operation"] == "SET0":
#                             # self.LOOPPID_SET_MODE(address=message[key]["address"], mode= 0)
#                             self.LOOPPID_SETPOINT(address=message[key]["address"],
#                                                       setpoint=message[key]["value"]["SETPOINT"], mode=0)
#                             # self.LOOPPID_HI_LIM(address=message[key]["address"], value=message[key]["value"]["HI_LIM"])
#                             # self.LOOPPID_LO_LIM(address=message[key]["address"], value=message[key]["value"]["LO_LIM"])
#                             self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
#                                                         value=message[key]["value"]["HI_LIM"])
#                             self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
#                                                         value=message[key]["value"]["LO_LIM"])
#
#                         elif message[key]["operation"] == "SET1":
#                             # self.LOOPPID_SET_MODE(address=message[key]["address"], mode=1)
#                             self.LOOPPID_SETPOINT(address=message[key]["address"],
#                                                       setpoint=message[key]["value"]["SETPOINT"], mode=1)
#                             self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
#                                                         value=message[key]["value"]["HI_LIM"])
#                             self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
#                                                         value=message[key]["value"]["LO_LIM"])
#                         elif message[key]["operation"] == "SET2":
#                             # self.LOOPPID_SET_MODE(address=message[key]["address"], mode=2)
#                             self.LOOPPID_SETPOINT(address=message[key]["address"],
#                                                       setpoint=message[key]["value"]["SETPOINT"], mode=2)
#                             self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
#                                                         value=message[key]["value"]["HI_LIM"])
#                             self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
#                                                         value=message[key]["value"]["LO_LIM"])
#                         elif message[key]["operation"] == "SET3":
#                             # self.LOOPPID_SET_MODE(address=message[key]["address"], mode=3)
#                             self.LOOPPID_SETPOINT(address=message[key]["address"],
#                                                       setpoint=message[key]["value"]["SETPOINT"], mode=3)
#                             self.LOOPPID_SET_HI_LIM(address=message[key]["address"],
#                                                         value=message[key]["value"]["HI_LIM"])
#                             self.LOOPPID_SET_LO_LIM(address=message[key]["address"],
#                                                         value=message[key]["value"]["LO_LIM"])
#                         else:
#                             pass
#
#                     elif message[key]["type"] == "heater_setmode":
#                         if message[key]["operation"] == "SET0":
#                             self.LOOPPID_SET_MODE(address=message[key]["address"], mode=0)
#
#                         elif message[key]["operation"] == "SET1":
#                             # print(True)
#                             self.LOOPPID_SET_MODE(address=message[key]["address"], mode=1)
#
#                         elif message[key]["operation"] == "SET2":
#                             self.LOOPPID_SET_MODE(address=message[key]["address"], mode=2)
#
#                         elif message[key]["operation"] == "SET3":
#                             self.LOOPPID_SET_MODE(address=message[key]["address"], mode=3)
#
#                         else:
#                             pass
#
#
#
#                     elif message[key]["type"] == "LOOP2PT_power":
#                         print("PUMP", datetime_in_1e5micro())
#                         if message[key]["operation"] == "OPEN":
#                             self.LOOP2PT_OPEN(address=message[key]["address"])
#                         elif message[key]["operation"] == "CLOSE":
#                             self.LOOP2PT_CLOSE(address=message[key]["address"])
#                         else:
#                             pass
#
#                     elif message[key]["type"] == "LOOP2PT_para":
#
#                         if message[key]["operation"] == "SET1":
#                             # self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=1)
#                             self.LOOP2PT_SETPOINT(address=message[key]["address"],
#                                                       setpoint=message[key]["value"]["SETPOINT"], mode=1)
#
#                         elif message[key]["operation"] == "SET2":
#                             # self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=2)
#                             self.LOOP2PT_SETPOINT(address=message[key]["address"],
#                                                       setpoint=message[key]["value"]["SETPOINT"], mode=2)
#
#                         elif message[key]["operation"] == "SET3":
#                             # self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=3)
#                             self.LOOP2PT_SETPOINT(address=message[key]["address"],
#                                                       setpoint=message[key]["value"]["SETPOINT"], mode=3)
#                         else:
#                             pass
#
#                     elif message[key]["type"] == "LOOP2PT_setmode":
#                         if message[key]["operation"] == "SET0":
#                             self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=0)
#
#                         elif message[key]["operation"] == "SET1":
#                             self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=1)
#
#                         elif message[key]["operation"] == "SET2":
#                             self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=2)
#
#                         elif message[key]["operation"] == "SET3":
#                             self.LOOP2PT_SET_MODE(address=message[key]["address"], mode=3)
#
#                         else:
#                             pass
#                     elif message[key]["type"] == "INTLK_A":
#                         if message[key]["server"] == "BO":
#                             if message[key]["operation"] == "ON":
#                                 self.WriteBase8(address=message[key]["address"])
#                             elif message[key]["operation"] == "OFF":
#                                 self.WriteBase16(address=message[key]["address"])
#                             elif message[key]["operation"] == "RESET":
#                                 self.WriteBase32(address=message[key]["address"])
#                             elif message[key]["operation"] == "update":
#                                 self.Write_BO_2(message[key]["address"] + 2, message[key]["value"])
#                             else:
#                                 pass
#                     elif message[key]["type"] == "INTLK_D":
#                         if message[key]["server"] == "BO":
#                             if message[key]["operation"] == "ON":
#                                 self.WriteBase8(address=message[key]["address"])
#                             elif message[key]["operation"] == "OFF":
#                                 self.WriteBase16(address=message[key]["address"])
#                             elif message[key]["operation"] == "RESET":
#                                 self.WriteBase32(address=message[key]["address"])
#                             else:
#                                 pass
#                     elif message[key]["type"] == "FLAG":
#                         print("time", datetime.datetime.now())
#                         if message[key]["operation"] == "OPEN":
#                             self.WriteBase2(address=message[key]["address"])
#                         elif message[key]["operation"] == "CLOSE":
#                             self.WriteBase4(address=message[key]["address"])
#                         else:
#                             pass
#                     else:
#                         pass
#
#         elif "MAN_SET" in message:
#             # manually set the configuration
#             for key in message["MAN_SET"]["data"]["TT"]["FP"]["high"]:
#                 self.TT_FP_HighLimit[key] = message["MAN_SET"]["data"]["TT"]["FP"]["high"][key]
#
#             for key in message["MAN_SET"]["data"]["TT"]["BO"]["high"]:
#                 self.TT_BO_HighLimit[key] = message["MAN_SET"]["data"]["TT"]["BO"]["high"][key]
#
#             for key in message["MAN_SET"]["data"]["PT"]["high"]:
#                 self.PT_HighLimit[key] = message["MAN_SET"]["data"]["PT"]["high"][key]
#
#             for key in message["MAN_SET"]["data"]["LEFT_REAL"]["high"]:
#                 self.LEFT_REAL_HighLimit[key] = message["MAN_SET"]["data"]["LEFT_REAL"]["high"][key]
#             for key in message["MAN_SET"]["data"]["AD"]["high"]:
#                 self.AD_HighLimit[key] = message["MAN_SET"]["data"]["AD"]["high"][key]
#
#             for key in message["MAN_SET"]["data"]["Din"]["high"]:
#                 self.Din_HighLimit[key] = message["MAN_SET"]["data"]["Din"]["high"][key]
#
#             for key in message["MAN_SET"]["data"]["LOOPPID"]["Alarm_HighLimit"]:
#                 self.LOOPPID_Alarm_HighLimit[key] = message["MAN_SET"]["data"]["LOOPPID"]["Alarm_HighLimit"][key]
#
#             for key in message["MAN_SET"]["data"]["TT"]["FP"]["low"]:
#                 self.TT_FP_LowLimit[key] = message["MAN_SET"]["data"]["TT"]["FP"]["low"][key]
#
#             for key in message["MAN_SET"]["data"]["TT"]["BO"]["low"]:
#                 self.TT_BO_LowLimit[key] = message["MAN_SET"]["data"]["TT"]["BO"]["low"][key]
#
#             for key in message["MAN_SET"]["data"]["PT"]["low"]:
#                 self.PT_LowLimit[key] = message["MAN_SET"]["data"]["PT"]["low"][key]
#
#             for key in message["MAN_SET"]["data"]["LEFT_REAL"]["low"]:
#                 self.LEFT_REAL_LowLimit[key] = message["MAN_SET"]["data"]["LEFT_REAL"]["low"][key]
#             for key in message["MAN_SET"]["data"]["AD"]["low"]:
#                 self.AD_LowLimit[key] = message["MAN_SET"]["data"]["AD"]["low"][key]
#
#             for key in message["MAN_SET"]["data"]["Din"]["low"]:
#                 self.Din_LowLimit[key] = message["MAN_SET"]["data"]["Din"]["low"][key]
#
#             for key in message["MAN_SET"]["data"]["LOOPPID"]["Alarm_LowLimit"]:
#                 self.LOOPPID_Alarm_LowLimit[key] = message["MAN_SET"]["data"]["LOOPPID"]["Alarm_LowLimit"][key]
#
#             for key in message["MAN_SET"]["Active"]["TT"]["FP"]:
#                 self.TT_FP_Activated[key] = message["MAN_SET"]["Active"]["TT"]["FP"][key]
#
#             for key in message["MAN_SET"]["Active"]["TT"]["BO"]:
#                 self.TT_BO_Activated[key] = message["MAN_SET"]["Active"]["TT"]["BO"][key]
#
#             for key in message["MAN_SET"]["Active"]["PT"]:
#                 self.PT_Activated[key] = message["MAN_SET"]["Active"]["PT"][key]
#
#             for key in message["MAN_SET"]["Active"]["LEFT_REAL"]:
#                 self.LEFT_REAL_Activated[key] = message["MAN_SET"]["Active"]["LEFT_REAL"][key]
#             for key in message["MAN_SET"]["Active"]["AD"]:
#                 self.AD_Activated[key] = message["MAN_SET"]["Active"]["AD"][key]
#
#             for key in message["MAN_SET"]["Active"]["Din"]:
#                 self.Din_Activated[key] = message["MAN_SET"]["Active"]["Din"][key]
#
#             for key in message["MAN_SET"]["Active"]["LOOPPID"]:
#                 self.LOOPPID_Activated[key] = message["MAN_SET"]["Active"]["LOOPPID"][key]
#         else:
#             print(
#                 "Failed to load data from Client. MAN_SET is not either in or not in the received directory. Please check the code")
#         received_dict.clear()
#
#     def Read_BO_1(self, address):
#         Raw_BO = self.Client_BO.read_holding_registers(address, count=1, unit=0x01)
#         output_BO = struct.pack("H", Raw_BO.getRegister(0))
#         # print("valve value is", output_BO)
#         return output_BO
#
#     def Read_BO_2(self, address):
#         Raw_BO = self.Client_BO.read_holding_registers(address, count=2, unit=0x01)
#         output_BO = round(struct.unpack(">f", struct.pack(">HH", Raw_BO.getRegister(1), Raw_BO.getRegister(0)))[
#                               0], 3)
#         # print("valve value is", output_BO)
#         return output_BO
#
#     def float_to_2words(self, value):
#         fl = float(value)
#         x = np.arange(fl, fl + 1, dtype='<f4')
#         if len(x) == 1:
#             word = x.tobytes()
#             piece1, piece2 = struct.unpack('<HH', word)
#         else:
#             print("ERROR in float to words")
#         return piece1, piece2
#
#     def int16_to_word(self, value):
#         try:
#             it = int(value)
#             x = np.arange(it, it + 1, dtype='<i2')
#             if len(x) == 1:
#                 word = x.tobytes()
#             else:
#                 print("ERROR in float to words")
#             return word
#         except:
#             return 0
#
#     def int32_to_2words(self, value):
#         try:
#             it = int(value)
#             x = np.arange(it, it + 1, dtype='<i4')
#             if len(x) == 1:
#                 word = x.tobytes()
#                 piece1, piece2 = struct.unpack('<HH', word)
#             else:
#                 print("ERROR in float to words")
#             return piece1, piece2
#         except:
#             return 0
#
#     def Write_BO_2(self, address, value):
#         word1, word2 = self.float_to_2words(value)
#         print('words', word1, word2)
#         # pay attention to endian relationship
#         Raw1 = self.Client_BO.write_register(address, value=word1, unit=0x01)
#         Raw2 = self.Client_BO.write_register(address + 1, value=word2, unit=0x01)
#
#         print("write result = ", Raw1, Raw2)
#
#     def Write_BO_2_int16(self, address, value):
#         word = self.int16_to_word(value)
#         print('word', word)
#         # pay attention to endian relationship
#         Raw = self.Client_BO.write_register(address, value=word, unit=0x01)
#
#         print("write result = ", Raw)
#
#     def Write_BO_2_int32(self, address, value):
#         word1, word2 = self.int32_to_2words(value)
#         print('words', word1, word2)
#         # pay attention to endian relationship
#         Raw1 = self.Client_BO.write_register(address, value=word1, unit=0x01)
#         Raw2 = self.Client_BO.write_register(address + 1, value=word2, unit=0x01)
#
#         print("write result = ", Raw1, Raw2)
#
#     def WriteBase2(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x0002
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write base2 result=", Raw)
#
#     def WriteBase4(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x0004
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write base4 result=", Raw)
#
#     def WriteBase8(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x0008
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write base8 result=", Raw)
#
#     def WriteBase16(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x0010
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write base16 result=", Raw)
#
#     def WriteBase32(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x0020
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write base32 result=", Raw)
#
#     def WriteFF(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x8000
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write FF result=", Raw)
#
#     def Reset(self, address):
#         Raw = self.Client_BO.write_register(address, value=0x0010, unit=0x01)
#         print("write Reset result=", Raw)
#
#     # mask is a number to read a particular digit. for example, if you want to read 3rd digit, the mask is 0100(binary)
#     def ReadCoil(self, mask, address):
#         output_BO = self.Read_BO_1(address)
#         masked_output = struct.unpack("H", output_BO)[0] & mask
#         if masked_output == 0:
#             return False
#         else:
#             return True
#
#     def ReadFPAttribute(self, address):
#         Raw = self.Client_NI.read_holding_registers(address, count=1, unit=0x01)
#         output = struct.pack("H", Raw.getRegister(0))
#         # print(Raw.getRegister(0))
#         return output
#
#     def SetFPRTDAttri(self, mode, address):
#         # Highly suggested firstly read the value and then set as the FP menu suggests
#         # mode should be wrtten in 0x
#         # we use Read_BO_1 function because it can be used here, i.e read 2 word at a certain address
#         output = self.ReadFPAttribute(address)
#         print("output", address, output)
#         Raw = self.Client_NI.write_register(address, value=mode, unit=0x01)
#         print("write open result=", Raw)
#         return 0
#
#     def LOOPPID_SET_MODE(self, address, mode=0):
#         output_BO = self.Read_BO_1(address)
#         if mode == 0:
#             input_BO = struct.unpack("H", output_BO)[0] | 0x0010
#             Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         elif mode == 1:
#             input_BO = struct.unpack("H", output_BO)[0] | 0x0020
#             Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         elif mode == 2:
#             input_BO = struct.unpack("H", output_BO)[0] | 0x0040
#             Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         elif mode == 3:
#             input_BO = struct.unpack("H", output_BO)[0] | 0x0080
#             Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         else:
#             Raw = "ERROR in LOOPPID SET MODE"
#
#         print("write result:", "mode=", Raw)
#
#     def LOOPPID_OUT_ENA(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x2000
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write OUT result=", Raw)
#
#     def LOOPPID_OUT_DIS(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x4000
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write OUT result=", Raw)
#
#     def LOOPPID_SETPOINT(self, address, setpoint, mode=0):
#         if mode == 0:
#             self.Write_BO_2(address + 10, setpoint)
#         elif mode == 1:
#             self.Write_BO_2(address + 12, setpoint)
#         elif mode == 2:
#             self.Write_BO_2(address + 14, setpoint)
#         elif mode == 3:
#             self.Write_BO_2(address + 16, setpoint)
#         else:
#             pass
#
#         print("LOOPPID_SETPOINT")
#
#     def LOOPPID_SET_HI_LIM(self, address, value):
#         self.Write_BO_2(address + 6, value)
#         print("LOOPPID_HI")
#
#     def LOOPPID_SET_LO_LIM(self, address, value):
#         self.Write_BO_2(address + 8, value)
#         print("LOOPPID_LO")
#
#     def LOOP2PT_SET_MODE(self, address, mode=0):
#         output_BO = self.Read_BO_1(address)
#         if mode == 0:
#             input_BO = struct.unpack("H", output_BO)[0] | 0x0400
#             Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         elif mode == 1:
#             input_BO = struct.unpack("H", output_BO)[0] | 0x0800
#             Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         elif mode == 2:
#             input_BO = struct.unpack("H", output_BO)[0] | 0x1000
#             Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         elif mode == 3:
#             input_BO = struct.unpack("H", output_BO)[0] | 0x2000
#             Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         else:
#             Raw = "ERROR in LOOP2PT SET MODE"
#
#         print("write result:", "mode=", Raw)
#
#     def LOOP2PT_OPEN(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x0002
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write OUT result=", Raw)
#
#     def LOOP2PT_CLOSE(self, address):
#         output_BO = self.Read_BO_1(address)
#         input_BO = struct.unpack("H", output_BO)[0] | 0x004
#         Raw = self.Client_BO.write_register(address, value=input_BO, unit=0x01)
#         print("write OUT result=", Raw)
#
#     def LOOP2PT_SETPOINT(self, address, setpoint, mode):
#         if mode == 1:
#             self.Write_BO_2(address + 2, setpoint)
#         elif mode == 2:
#             self.Write_BO_2(address + 4, setpoint)
#         elif mode == 3:
#             self.Write_BO_2(address + 6, setpoint)
#         else:
#             pass
#
#         print("LOOPPID_SETPOINT")
#
#     def WriteFloat(self, Address, value):
#         if self.Connected_NI:
#             value = round(value, 3)
#             Dummy = self.Client_NI.write_register(Address, struct.unpack("<HH", struct.pack("<f", value))[1], unit=0x01)
#             Dummy = self.Client_NI.write_register(Address + 1, struct.unpack("<HH", struct.pack("<f", value))[0],
#                                                unit=0x01)
#
#             time.sleep(0.1)
#
#             Raw = self.Client_NI.read_holding_registers(Address, count=2, unit=0x01)
#             rvalue = round(struct.unpack("<f", struct.pack("<HH", Raw.getRegister(1), Raw.getRegister(0)))[0], 3)
#
#             if value == rvalue:
#                 return 0
#             else:
#                 return 2
#         else:
#             return 1
#
#     def WriteBool(self, Address, Bit, value):
#         if self.Connected_NI:
#             Raw = self.Client_NI.read_coils(Address, count=Bit, unit=0x01)
#             Raw.bits[Bit] = value
#             Dummy = self.Client_NI.write_coil(Address, Raw, unit=0x01)
#
#             time.sleep(0.1)
#
#             Raw = self.Client_NI.read_coils(Address, count=Bit, unit=0x01)
#             rvalue = Raw.bits[Bit]
#
#             if value == rvalue:
#                 return 0
#             else:
#                 return 2
#         else:
#             return 1
#
#
# # Class to read PLC value every 2 sec
# class UpdatePLC(PLC, threading.Thread):
#
#     def __init__(self, plc_data, plc_lock, command_data, command_lock, alarm_stack, alarm_lock,global_time, timelock, *args, **kwargs):
#         PLC.__init__(self, plc_data, plc_lock, command_data, command_lock, alarm_stack, alarm_lock)
#         threading.Thread.__init__(self, *args, **kwargs)
#         self.Running = False
#         self.period = 1
#         # every pid should have one unique para and rate
#         self.TT_FP_para = env.TT_FP_PARA
#         self.TT_FP_rate = env.TT_FP_RATE
#         self.TT_BO_para = env.TT_BO_PARA
#         self.TT_BO_rate = env.TT_BO_RATE
#         self.PT_para = env.PT_PARA
#         self.PT_rate = env.PT_RATE
#         self.PR_CYCLE_para = 0
#         self.PR_CYCLE_rate = 30
#         self.LEFT_REAL_para = env.LEFT_REAL_PARA
#         self.LEFT_REAL_rate = env.LEFT_REAL_RATE
#         self.AD_para = env.AD_PARA
#         self.AD_rate = env.AD_RATE
#         self.Din_para = env.DIN_PARA
#         self.Din_rate = env.DIN_RATE
#         self.LOOPPID_para = env.LOOPPID_PARA
#         self.LOOPPID_rate = env.LOOPPID_RATE
#         self.mainalarm_para = env.MAINALARM_PARA
#         self.mainalarm_rate = env.MAINALARM_RATE
#         self.global_time = global_time
#         self.timelock = timelock
#         self.alarm_stack = alarm_stack
#         self.alarm_lock = alarm_lock
#
#     def run(self):
#
#         self.Running = True
#
#         while self.Running:
#             try:
#                 with self.timelock:
#                     self.global_time.update({"plctime" :datetime_in_1e5micro()})
#                     test_crontab(str(self.global_time["plctime"]))
#                     print("PLC updating", self.global_time["plctime"])
#             except Exception as e:
#                 print("Exception in plc raised")
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"PLC updating Exception": "PLC timestamp updates ERROR"})
#                 # self run depend on senario, we want to rerun the module by module
#             # it has its own try function so we can skip try function here
#             self.ReadAll()
#             try:
#                 with self.command_lock:
#                     self.write_data(self.command_data)
#                 # check alarms
#                 for keyTT_FP in self.TT_FP_dic:
#                     self.check_TT_FP_alarm(keyTT_FP)
#                 for keyTT_BO in self.TT_BO_dic:
#                     self.check_TT_BO_alarm(keyTT_BO)
#                 for keyPT in self.PT_dic:
#                     self.check_PT_alarm(keyPT)
#                 for keyLEFT_REAL in self.LEFT_REAL_dic:
#                     self.check_LEFT_REAL_alarm(keyLEFT_REAL)
#                 for keyAD in self.AD_dic:
#                     self.check_AD_alarm(keyAD)
#                 for keyDin in self.Din_dic:
#                     self.check_Din_alarm(keyDin)
#                 for keyLOOPPID in self.LOOPPID_OUT:
#                     self.check_LOOPPID_alarm(keyLOOPPID)
#                 self.or_alarm_signal()
#                 time.sleep(self.period)
#             except Exception as e:
#                 # (type, value, traceback) = sys.exc_info()
#                 # exception_hook(type, value, traceback)
#                 print("Exception in plc raised")
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"PLC updating Exception":"PLC alarm check. Restarting..."})
#                 # self run depend on senario, we want to rerun the module by module
#                 break
#         self.run()
#
#
#
#     def stop(self):
#         self.Running = False
#
#     def stack_alarm_msg(self, pid, string):
#         with self.alarm_lock:
#             self.alarm_stack.update({pid : string})
#         # print("stack2", self.alarm_stack)
#
#     def join_stack_into_message(self):
#         message = ""
#         if len(self.alarm_stack) >= 1:
#             for key in self.alarm_stack:
#                 message = message + "\n" + self.alarm_stack[key]
#         return message
#
#     def check_TT_FP_alarm(self, pid):
#
#         if self.TT_FP_Activated[pid]:
#             if float(self.TT_FP_LowLimit[pid]) >= float(self.TT_FP_HighLimit[pid]):
#                 print("Low limit should be less than high limit!")
#             else:
#                 if float(self.TT_FP_dic[pid]) <= float(self.TT_FP_LowLimit[pid]):
#                     self.TTFPalarmmsg(pid)
#
#                     # print(pid , " reading is lower than the low limit")
#                 elif float(self.TT_FP_dic[pid]) >= float(self.TT_FP_HighLimit[pid]):
#                     self.TTFPalarmmsg(pid)
#
#                     # print(pid,  " reading is higher than the high limit")
#                 else:
#                     self.resetTTFPalarmmsg(pid)
#                     # print(pid, " is in normal range")
#
#         else:
#             self.resetTTFPalarmmsg(pid)
#             pass
#
#     def check_TT_BO_alarm(self, pid):
#
#         if self.TT_BO_Activated[pid]:
#             if float(self.TT_BO_LowLimit[pid]) >= float(self.TT_BO_HighLimit[pid]):
#                 print("Low limit should be less than high limit!")
#             else:
#                 if float(self.TT_BO_dic[pid]) <= float(self.TT_BO_LowLimit[pid]):
#                     self.TTBOalarmmsg(pid)
#
#                     # print(pid , " reading is lower than the low limit")
#                 elif float(self.TT_BO_dic[pid]) >= float(self.TT_BO_HighLimit[pid]):
#                     self.TTBOalarmmsg(pid)
#
#                     # print(pid,  " reading is higher than the high limit")
#                 else:
#                     self.resetTTBOalarmmsg(pid)
#                     # print(pid, " is in normal range")
#
#         else:
#             self.resetTTBOalarmmsg(pid)
#             pass
#
#     def check_PT_alarm(self, pid):
#
#         if self.PT_Activated[pid]:
#             if float(self.PT_LowLimit[pid]) >= float(self.PT_HighLimit[pid]):
#                 print("Low limit should be less than high limit!")
#             else:
#                 if float(self.PT_dic[pid]) <= float(self.PT_LowLimit[pid]):
#                     self.PTalarmmsg(pid)
#
#                     # print(pid , " reading is lower than the low limit")
#                 elif float(self.PT_dic[pid]) >= float(self.PT_HighLimit[pid]):
#                     self.PTalarmmsg(pid)
#                     # print(pid,  " reading is higher than the high limit")
#                 else:
#                     self.resetPTalarmmsg(pid)
#                     # print(pid, " is in normal range")
#
#         else:
#             self.resetPTalarmmsg(pid)
#             pass
#
#     def check_LEFT_REAL_alarm(self, pid):
#
#         if self.LEFT_REAL_Activated[pid]:
#             if float(self.LEFT_REAL_LowLimit[pid]) >= float(self.LEFT_REAL_HighLimit[pid]):
#                 print("Low limit should be less than high limit!")
#             else:
#                 if float(self.LEFT_REAL_dic[pid]) <= float(self.LEFT_REAL_LowLimit[pid]):
#                     self.LEFT_REALalarmmsg(pid)
#
#                     # print(pid , " reading is lower than the low limit")
#                 elif float(self.LEFT_REAL_dic[pid]) >= float(self.LEFT_REAL_HighLimit[pid]):
#                     self.LEFT_REALalarmmsg(pid)
#                     # print(pid,  " reading is higher than the high limit")
#                 else:
#                     self.resetLEFT_REALalarmmsg(pid)
#                     # print(pid, " is in normal range")
#
#         else:
#             self.resetLEFT_REALalarmmsg(pid)
#             pass
#
#     def check_AD_alarm(self, pid):
#
#         if self.AD_Activated[pid]:
#             if float(self.AD_LowLimit[pid]) >= float(self.AD_HighLimit[pid]):
#                 print("Low limit should be less than high limit!")
#             else:
#                 if float(self.AD_dic[pid]) <= float(self.AD_LowLimit[pid]):
#                     self.ADalarmmsg(pid)
#
#                     # print(pid , " reading is lower than the low limit")
#                 elif float(self.AD_dic[pid]) >= float(self.AD_HighLimit[pid]):
#                     self.ADalarmmsg(pid)
#                     # print(pid,  " reading is higher than the high limit")
#                 else:
#                     self.resetADalarmmsg(pid)
#                     # print(pid, " is in normal range")
#
#         else:
#             self.resetADalarmmsg(pid)
#             pass
#
#     def check_Din_alarm(self, pid):
#
#         if self.Din_Activated[pid]:
#             if float(self.Din_LowLimit[pid]) >= float(self.Din_HighLimit[pid]):
#                 print("Low limit should be less than high limit!")
#             else:
#                 if float(self.Din_dic[pid]) <= float(self.Din_LowLimit[pid]):
#                     self.Dinalarmmsg(pid)
#
#                     # print(pid , " reading is lower than the low limit")
#                 elif float(self.Din_dic[pid]) >= float(self.Din_HighLimit[pid]):
#                     self.Dinalarmmsg(pid)
#                     # print(pid,  " reading is higher than the high limit")
#                 else:
#                     self.resetDinalarmmsg(pid)
#                     # print(pid, " is in normal range")
#
#         else:
#             self.resetDinalarmmsg(pid)
#             pass
#
#     def check_LOOPPID_alarm(self, pid):
#
#
#         if self.LOOPPID_Activated[pid]:
#             if float(self.LOOPPID_Alarm_LowLimit[pid]) >= float(self.LOOPPID_Alarm_HighLimit[pid]):
#                 print("Low limit should be less than high limit!")
#             else:
#                 if float(self.LOOPPID_OUT[pid]) <= float(self.LOOPPID_Alarm_LowLimit[pid]):
#                     self.LOOPPIDalarmmsg(pid)
#
#                     # print(pid , " reaLOOPPIDg is lower than the low limit")
#                 elif float(self.LOOPPID_OUT[pid]) >= float(self.LOOPPID_Alarm_HighLimit[pid]):
#                     self.LOOPPIDalarmmsg(pid)
#                     # print(pid,  " reaLOOPPIDg is higher than the high limit")
#                 else:
#                     self.resetLOOPPIDalarmmsg(pid)
#                     # print(pid, " is in normal range")
#
#         else:
#             self.resetLOOPPIDalarmmsg(pid)
#             pass
#
#     def TTFPalarmmsg(self, pid):
#         self.TT_FP_Alarm[pid] = True
#         # and send email or slack messages
#         # every time interval send a alarm message
#         if self.TT_FP_para[pid] >= self.TT_FP_rate[pid]:
#             msg = "SBC alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(
#                 pid=pid, current=self.TT_FP_dic[pid],
#                 high=self.TT_FP_HighLimit[pid], low=self.TT_FP_LowLimit[pid])
#             # self.message_manager.tencent_alarm(msg)
#             self.stack_alarm_msg(pid, msg)
#
#             self.TT_FP_para[pid] = 0
#         self.TT_FP_para[pid] += 1
#
#     def resetTTFPalarmmsg(self, pid):
#         self.TT_FP_Alarm[pid] = False
#         self.alarm_stack.pop(pid, None)
#         # self.TT_FP_para = 0
#         # and send email or slack messages
#
#     def TTBOalarmmsg(self, pid):
#         self.TT_BO_Alarm[pid] = True
#         # and send email or slack messages
#         # print(self.TT_BO_para[pid])
#         if self.TT_BO_para[pid] >= self.TT_BO_rate[pid]:
#             msg = "SBC alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(
#                 pid=pid, current=self.TT_BO_dic[pid],
#                 high=self.TT_BO_HighLimit[pid], low=self.TT_BO_LowLimit[pid])
#             # self.message_manager.tencent_alarm(msg)
#             self.stack_alarm_msg(pid, msg)
#             self.TT_BO_para[pid] = 0
#
#         self.TT_BO_para[pid] += 1
#
#     def resetTTBOalarmmsg(self, pid):
#         self.TT_BO_Alarm[pid] = False
#         self.alarm_stack.pop(pid, None)
#         # self.TT_BO_para = 0
#         # and send email or slack messages
#
#     def PTalarmmsg(self, pid):
#         self.PT_Alarm[pid] = True
#         # and send email or slack messages
#         if self.PT_para[pid] >= self.PT_rate[pid]:
#             msg = "SBC alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(
#                 pid=pid, current=self.PT_dic[pid],
#                 high=self.PT_HighLimit[pid], low=self.PT_LowLimit[pid])
#
#             # self.message_manager.tencent_alarm(msg)
#             self.stack_alarm_msg(pid, msg)
#             self.PT_para[pid] = 0
#         self.PT_para[pid] += 1
#
#     def resetPTalarmmsg(self, pid):
#         self.PT_Alarm[pid] = False
#         self.alarm_stack.pop(pid, None)
#         # self.PT_para = 0
#         # and send email or slack messages
#
#     def LEFT_REALalarmmsg(self, pid):
#         self.LEFT_REAL_Alarm[pid] = True
#         # and send email or slack messages
#         if self.LEFT_REAL_para[pid] >= self.LEFT_REAL_rate[pid]:
#             msg = "SBC alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(
#                 pid=pid, current=self.LEFT_REAL_dic[pid],
#                 high=self.LEFT_REAL_HighLimit[pid], low=self.LEFT_REAL_LowLimit[pid])
#
#             # self.message_manager.tencent_alarm(msg)
#             self.stack_alarm_msg(pid, msg)
#             self.LEFT_REAL_para[pid] = 0
#         self.LEFT_REAL_para[pid] += 1
#
#     def resetLEFT_REALalarmmsg(self, pid):
#         self.LEFT_REAL_Alarm[pid] = False
#         self.alarm_stack.pop(pid, None)
#         # self.LEFT_REAL_para = 0
#         # and send email or slack messages
#
#     def ADalarmmsg(self, pid):
#         self.AD_Alarm[pid] = True
#         # and send email or slack messages
#         if self.AD_para[pid] >= self.AD_rate[pid]:
#             msg = "SBC alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(
#                 pid=pid, current=self.AD_dic[pid],
#                 high=self.AD_HighLimit[pid], low=self.AD_LowLimit[pid])
#
#             # self.message_manager.tencent_alarm(msg)
#             self.stack_alarm_msg(pid, msg)
#             self.AD_para[pid] = 0
#         self.AD_para[pid] += 1
#
#     def resetADalarmmsg(self, pid):
#         self.AD_Alarm[pid] = False
#         self.alarm_stack.pop(pid, None)
#         # self.AD_para = 0
#         # and send email or slack messages
#
#     def Dinalarmmsg(self, pid):
#         self.Din_Alarm[pid] = True
#         # and send email or slack messages
#         if self.Din_para[pid] >= self.Din_rate[pid]:
#             msg = "SBC alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(
#                 pid=pid, current=self.Din_dic[pid],
#                 high=self.Din_HighLimit[pid], low=self.Din_LowLimit[pid])
#
#             # self.message_manager.tencent_alarm(msg)
#             self.stack_alarm_msg(pid, msg)
#             self.Din_para[pid] = 0
#         self.Din_para[pid] += 1
#
#     def resetDinalarmmsg(self, pid):
#         self.Din_Alarm[pid] = False
#         self.alarm_stack.pop(pid, None)
#         # self.Din_para = 0
#         # and send email or slack messages
#
#     def LOOPPIDalarmmsg(self, pid):
#         self.LOOPPID_Alarm[pid] = True
#         # and send email or slack messages
#         if self.LOOPPID_para[pid] >= self.LOOPPID_rate[pid]:
#             msg = "SBC alarm: {pid} is out of range: CURRENT VALUE: {current}, LO_LIM: {low}, HI_LIM: {high}".format(
#                 pid=pid, current=self.LOOPPID_OUT[pid],
#                 high=self.LOOPPID_Alarm_HighLimit[pid], low=self.LOOPPID_Alarm_LowLimit[pid])
#
#             # self.message_manager.tencent_alarm(msg)
#             self.stack_alarm_msg(pid, msg)
#             self.LOOPPID_para[pid] = 0
#         self.LOOPPID_para[pid] += 1
#
#     def resetLOOPPIDalarmmsg(self, pid):
#         self.LOOPPID_Alarm[pid] = False
#         self.alarm_stack.pop(pid, None)
#         # self.LOOPPID_para = 0
#         # and send email or slack messages
#
#     def or_alarm_signal(self):
#         # print("\n or_signal",self.PT_Alarm,self.true_in_dictionary(self.PT_Alarm))
#         if self.true_in_dictionary(self.TT_BO_Alarm) or self.true_in_dictionary(
#                 self.PT_Alarm) or self.true_in_dictionary(self.TT_FP_Alarm) or self.true_in_dictionary(
#             self.LEFT_REAL_Alarm) or self.true_in_dictionary(self.Din_Alarm) or self.true_in_dictionary(
#             self.LOOPPID_Alarm) or self.true_in_dictionary(self.AD_Alarm):
#             self.MainAlarm = True
#         else:
#             self.MainAlarm = False
#
#     def true_in_dictionary(self, dictionary):
#         result = False
#         for key in dictionary:
#             result = result or dictionary[key]
#         return result
#
#
# # Class to update myseeq database
# class UpdateDataBase(threading.Thread):
#
#     def __init__(self, plc_data, plc_lock, global_time, timelock, alarm_stack, alarm_lock):
#         # inherit the thread method
#         super().__init__()
#         self.plc_data = plc_data
#         self.plc_lock = plc_lock
#         self.global_time = global_time
#         self.timelock = timelock
#         self.alarm_stack = alarm_stack
#         self.alarm_lock = alarm_lock
#
#
#         self.Running = False
#         # if loop runs with _counts times with New_Database = False(No written Data), then send alarm to slack. Otherwise, the code normally run(reset the pointer)
#         self.Running_counts = 600
#         self.Running_pointer = 0
#         self.longsleep = 60
#
#         self.base_period = 1
#
#         self.COUPP_ERROR = False
#         self.COUPP_ALARM = "k"
#         self.COUPP_HOLD = False
#
#         self.para_alarm = copy.copy(env.DATABASE_PARA["alarm"])
#         self.rate_alarm = copy.copy(env.DATABASE_RATE["alarm"])
#         self.para_TT = copy.copy(env.DATABASE_PARA["TT"])
#         self.rate_TT = copy.copy(env.DATABASE_RATE["TT"])
#         self.para_PT = copy.copy(env.DATABASE_PARA["PT"])
#         self.rate_PT = copy.copy(env.DATABASE_RATE["PT"])
#         self.para_REAL = copy.copy(env.DATABASE_PARA["REAL"])
#         self.rate_REAL = copy.copy(env.DATABASE_RATE["REAL"])
#         self.para_AD = copy.copy(env.DATABASE_PARA["AD"])
#         self.rate_AD = copy.copy(env.DATABASE_RATE["AD"])
#         self.para_Din = copy.copy(env.DATABASE_PARA["Din"])
#         self.rate_Din = copy.copy(env.DATABASE_RATE["Din"])
#         # c is for valve status
#         self.para_Valve = copy.copy(env.DATABASE_PARA["Valve"])
#         self.rate_Valve = copy.copy(env.DATABASE_RATE["Valve"])
#         self.para_Switch = copy.copy(env.DATABASE_PARA["Switch"])
#         self.rate_Switch = copy.copy(env.DATABASE_RATE["Switch"])
#         self.para_LOOPPID = copy.copy(env.DATABASE_PARA["LOOPPID"])
#         self.rate_LOOPPID = copy.copy(env.DATABASE_RATE["LOOPPID"])
#         self.para_LOOP2PT = copy.copy(env.DATABASE_PARA["LOOP2PT"])
#         self.rate_LOOP2PT = copy.copy(env.DATABASE_RATE["LOOP2PT"])
#         self.para_FLAG = copy.copy(env.DATABASE_PARA["FLAG"])
#         self.rate_FLAG = copy.copy(env.DATABASE_RATE["FLAG"])
#         self.para_INTLK_A = copy.copy(env.DATABASE_PARA["INTLK_A"])
#         self.rate_INTLK_A = copy.copy(env.DATABASE_RATE["INTLK_A"])
#         self.para_INTLK_D = copy.copy(env.DATABASE_PARA["INTLK_D"])
#         self.rate_INTLK_D = copy.copy(env.DATABASE_RATE["INTLK_D"])
#         self.para_FF = copy.copy(env.DATABASE_PARA["FF"])
#         self.rate_FF = copy.copy(env.DATABASE_RATE["FF"])
#         self.para_PARAM_F = copy.copy(env.DATABASE_PARA["PARAM_F"])
#         self.rate_PARAM_F = copy.copy(env.DATABASE_RATE["PARAM_F"])
#         self.para_PARAM_I = copy.copy(env.DATABASE_PARA["PARAM_I"])
#         self.rate_PARAM_I = copy.copy(env.DATABASE_RATE["PARAM_I"])
#         self.para_PARAM_B = copy.copy(env.DATABASE_PARA["PARAM_B"])
#         self.rate_PARAM_B = copy.copy(env.DATABASE_RATE["PARAM_B"])
#         self.para_PARAM_T = copy.copy(env.DATABASE_PARA["PARAM_T"])
#         self.rate_PARAM_T = copy.copy(env.DATABASE_RATE["PARAM_T"])
#         self.para_TIME = copy.copy(env.DATABASE_PARA["TIME"])
#         self.rate_TIME = copy.copy(env.DATABASE_RATE["TIME"])
#
#         # status initialization
#         self.status = False
#
#         # commit initialization
#         self.commit_bool = False
#         # INITIALIZATION
#         self.TT_FP_address = copy.copy(env.TT_FP_ADDRESS)
#         self.TT_BO_address = copy.copy(env.TT_BO_ADDRESS)
#         self.PT_address = copy.copy(env.PT_ADDRESS)
#         self.LEFT_REAL_address = copy.copy(env.LEFT_REAL_ADDRESS)
#         self.AD_address = copy.copy(env.AD_ADDRESS)
#         self.TT_FP_dic = copy.copy(env.TT_FP_DIC)
#         self.TT_BO_dic = copy.copy(env.TT_BO_DIC)
#         self.PT_dic = copy.copy(env.PT_DIC)
#         self.LEFT_REAL_dic = copy.copy(env.LEFT_REAL_DIC)
#         self.AD_dic = copy.copy(env.AD_DIC)
#         self.TT_FP_LowLimit = copy.copy(env.TT_FP_LOWLIMIT)
#         self.TT_FP_HighLimit = copy.copy(env.TT_FP_HIGHLIMIT)
#         self.TT_BO_LowLimit = copy.copy(env.TT_BO_LOWLIMIT)
#         self.TT_BO_HighLimit = copy.copy(env.TT_BO_HIGHLIMIT)
#
#         self.PT_LowLimit = copy.copy(env.PT_LOWLIMIT)
#         self.PT_HighLimit = copy.copy(env.PT_HIGHLIMIT)
#         self.LEFT_REAL_HighLimit = copy.copy(env.LEFT_REAL_HIGHLIMIT)
#         self.LEFT_REAL_LowLimit = copy.copy(env.LEFT_REAL_LOWLIMIT)
#         self.AD_HighLimit = copy.copy(env.AD_HIGHLIMIT)
#         self.AD_LowLimit = copy.copy(env.AD_LOWLIMIT)
#         self.TT_FP_Activated = copy.copy(env.TT_FP_ACTIVATED)
#         self.TT_BO_Activated = copy.copy(env.TT_BO_ACTIVATED)
#         self.PT_Activated = copy.copy(env.PT_ACTIVATED)
#         self.LEFT_REAL_Activated = copy.copy(env.LEFT_REAL_ACTIVATED)
#         self.AD_Activated = copy.copy(env.AD_ACTIVATED)
#
#         self.TT_FP_Alarm = copy.copy(env.TT_FP_ALARM)
#         self.TT_BO_Alarm = copy.copy(env.TT_BO_ALARM)
#         self.PT_Alarm = copy.copy(env.PT_ALARM)
#         self.LEFT_REAL_Alarm = copy.copy(env.LEFT_REAL_ALARM)
#         self.AD_Alarm = copy.copy(env.AD_ALARM)
#         self.MainAlarm = copy.copy(env.MAINALARM)
#         self.MAN_SET = copy.copy(env.MAN_SET)
#         self.nTT_BO = copy.copy(env.NTT_BO)
#         self.nTT_FP = copy.copy(env.NTT_FP)
#         self.nPT = copy.copy(env.NPT)
#         self.nREAL = copy.copy(env.NREAL)
#
#         self.TT_BO_setting = copy.copy(env.TT_BO_SETTING)
#         self.nTT_BO_Attribute = copy.copy(env.NTT_BO_ATTRIBUTE)
#         self.PT_setting = copy.copy(env.PT_SETTING)
#         self.nPT_Attribute = copy.copy(env.NPT_ATTRIBUTE)
#
#         self.Switch_address = copy.copy(env.SWITCH_ADDRESS)
#         self.nSwitch = copy.copy(env.NSWITCH)
#         self.Switch = copy.copy(env.SWITCH)
#         self.Switch_OUT = copy.copy(env.SWITCH_OUT)
#         self.Switch_MAN = copy.copy(env.SWITCH_MAN)
#         self.Switch_INTLKD = copy.copy(env.SWITCH_INTLKD)
#         self.Switch_ERR = copy.copy(env.SWITCH_ERR)
#         self.Din_address = copy.copy(env.DIN_ADDRESS)
#         self.nDin = copy.copy(env.NDIN)
#         self.Din = copy.copy(env.DIN)
#         self.Din_dic = copy.copy(env.DIN_DIC)
#         self.valve_address = copy.copy(env.VALVE_ADDRESS)
#         self.nValve = copy.copy(env.NVALVE)
#         self.Valve = copy.copy(env.VALVE)
#         self.Valve_OUT = copy.copy(env.VALVE_OUT)
#         self.Valve_MAN = copy.copy(env.VALVE_MAN)
#         self.Valve_INTLKD = copy.copy(env.VALVE_INTLKD)
#         self.Valve_ERR = copy.copy(env.VALVE_ERR)
#         self.LOOPPID_ADR_BASE = copy.copy(env.LOOPPID_ADR_BASE)
#         self.LOOPPID_MODE0 = copy.copy(env.LOOPPID_MODE0)
#         self.LOOPPID_MODE1 = copy.copy(env.LOOPPID_MODE1)
#         self.LOOPPID_MODE2 = copy.copy(env.LOOPPID_MODE2)
#         self.LOOPPID_MODE3 = copy.copy(env.LOOPPID_MODE3)
#         self.LOOPPID_INTLKD = copy.copy(env.LOOPPID_INTLKD)
#         self.LOOPPID_MAN = copy.copy(env.LOOPPID_MAN)
#         self.LOOPPID_ERR = copy.copy(env.LOOPPID_ERR)
#         self.LOOPPID_SATHI = copy.copy(env.LOOPPID_SATHI)
#         self.LOOPPID_SATLO = copy.copy(env.LOOPPID_SATLO)
#         self.LOOPPID_EN = copy.copy(env.LOOPPID_EN)
#         self.LOOPPID_OUT = copy.copy(env.LOOPPID_OUT)
#         self.LOOPPID_IN = copy.copy(env.LOOPPID_IN)
#         self.LOOPPID_HI_LIM = copy.copy(env.LOOPPID_HI_LIM)
#         self.LOOPPID_LO_LIM = copy.copy(env.LOOPPID_LO_LIM)
#         self.LOOPPID_SET0 = copy.copy(env.LOOPPID_SET0)
#         self.LOOPPID_SET1 = copy.copy(env.LOOPPID_SET1)
#         self.LOOPPID_SET2 = copy.copy(env.LOOPPID_SET2)
#         self.LOOPPID_SET3 = copy.copy(env.LOOPPID_SET3)
#         self.LOOP2PT_ADR_BASE = copy.copy(env.LOOP2PT_ADR_BASE)
#         self.LOOP2PT_MODE0 = copy.copy(env.LOOP2PT_MODE0)
#         self.LOOP2PT_MODE1 = copy.copy(env.LOOP2PT_MODE1)
#         self.LOOP2PT_MODE2 = copy.copy(env.LOOP2PT_MODE2)
#         self.LOOP2PT_MODE3 = copy.copy(env.LOOP2PT_MODE3)
#         self.LOOP2PT_INTLKD = copy.copy(env.LOOP2PT_INTLKD)
#         self.LOOP2PT_MAN = copy.copy(env.LOOP2PT_MAN)
#         self.LOOP2PT_ERR = copy.copy(env.LOOP2PT_ERR)
#         self.LOOP2PT_OUT = copy.copy(env.LOOP2PT_OUT)
#         self.LOOP2PT_SET1 = copy.copy(env.LOOP2PT_SET1)
#         self.LOOP2PT_SET2 = copy.copy(env.LOOP2PT_SET2)
#         self.LOOP2PT_SET3 = copy.copy(env.LOOP2PT_SET3)
#         self.Procedure_address = copy.copy(env.PROCEDURE_ADDRESS)
#         self.Procedure_running = copy.copy(env.PROCEDURE_RUNNING)
#         self.Procedure_INTLKD = copy.copy(env.PROCEDURE_INTLKD)
#         self.Procedure_EXIT = copy.copy(env.PROCEDURE_EXIT)
#         self.FLAG_ADDRESS = copy.copy(env.FLAG_ADDRESS)
#         self.FLAG_DIC = copy.copy(env.FLAG_DIC)
#         self.FLAG_INTLKD = copy.copy(env.FLAG_INTLKD)
#         self.FLAG_Busy = copy.copy(env.FLAG_BUSY)
#
#         self.FF_ADDRESS = copy.copy(env.FF_ADDRESS)
#         self.FF_DIC = copy.copy(env.FF_DIC)
#
#         self.PARAM_F_ADDRESS = copy.copy(env.PARAM_F_ADDRESS)
#         self.PARAM_F_DIC = copy.copy(env.PARAM_F_DIC)
#         self.PARAM_I_ADDRESS = copy.copy(env.PARAM_I_ADDRESS)
#         self.PARAM_I_DIC = copy.copy(env.PARAM_I_DIC)
#         self.PARAM_B_ADDRESS = copy.copy(env.PARAM_B_ADDRESS)
#         self.PARAM_B_DIC = copy.copy(env.PARAM_B_DIC)
#         self.PARAM_T_ADDRESS = copy.copy(env.PARAM_T_ADDRESS)
#         self.PARAM_T_DIC = copy.copy(env.PARAM_T_DIC)
#         self.TIME_ADDRESS = copy.copy(env.TIME_ADDRESS)
#         self.TIME_DIC = copy.copy(env.TIME_DIC)
#
#         # BUFFER parts
#         self.Valve_buffer = copy.copy(env.VALVE_OUT)
#         self.Switch_buffer = copy.copy(env.SWITCH_OUT)
#         self.Din_buffer = copy.copy(env.DIN_DIC)
#         self.LOOPPID_EN_buffer = copy.copy(env.LOOPPID_EN)
#         self.LOOPPID_MODE0_buffer = copy.copy(env.LOOPPID_MODE0)
#         self.LOOPPID_MODE1_buffer = copy.copy(env.LOOPPID_MODE1)
#         self.LOOPPID_MODE2_buffer = copy.copy(env.LOOPPID_MODE2)
#         self.LOOPPID_MODE3_buffer = copy.copy(env.LOOPPID_MODE3)
#         self.LOOPPID_OUT_buffer = copy.copy(env.LOOPPID_OUT)
#         self.LOOPPID_IN_buffer = copy.copy(env.LOOPPID_IN)
#
#         self.LOOP2PT_MODE0_buffer = copy.copy(env.LOOP2PT_MODE0)
#         self.LOOP2PT_MODE1_buffer = copy.copy(env.LOOP2PT_MODE1)
#         self.LOOP2PT_MODE2_buffer = copy.copy(env.LOOP2PT_MODE2)
#         self.LOOP2PT_MODE3_buffer = copy.copy(env.LOOP2PT_MODE3)
#         self.LOOP2PT_OUT_buffer = copy.copy(env.LOOP2PT_OUT)
#
#         self.FLAG_INTLKD_buffer = copy.copy(env.FLAG_INTLKD)
#
#         self.FF_buffer = copy.copy(env.FF_DIC)
#         self.PARAM_B_buffer = copy.copy(env.PARAM_B_DIC)
#
#         print("begin updating Database")
#
#
#     def run(self):
#
#         self.Running = True
#         while self.Running:
#             try:
#                 self.dt = datetime_in_1e5micro()
#                 self.early_dt = early_datetime()
#                 with self.timelock:
#                     self.global_time.update({"dbtime":self.dt})
#                 print("Database Updating", self.global_time["dbtime"])
#
#             except Exception as e:
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"Database Exception #1": "Local database timestamp error"})
#                 print("Error",e)
#
#
#             try:
#                 with self.plc_lock:
#                     data_received = dict(self.plc_data)
#                 self.update_value(data_received)
#                 print("received data from PLC")
#
#             except Exception as e:
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"Database Exception #2": "Local database data reception error"})
#                 # (type, value, traceback) = sys.exc_info()
#                 # exception_hook(type, value, traceback)
#             try:
#                 #     # if connected, run the write function, else try to reconnect
#                 #     # if reconnect process failed, then raise the Error as alarm msg depending on whether self.db exists
#                 # only when no mysql connections
#                 # if hasattr(self, 'db') or not self.db.db.is_connected():
#                 if not hasattr(self, 'db'): # if it doesn't exist, try to create it
#                     self.db = mydatabase()
#                 else:
#                     # connection exist but broken, restart it
#                     if not self.db.db.is_connected():
#                         self.db.db.close()
#                         self.db = mydatabase()
#                 if self.db.db.is_connected():
#
#                     try:
#                         # Check if the connection is still alive
#                         self.db.db.ping(reconnect=True)
#                         self.write_data()
#                         print("Data written into database")
#
#                     except mysql.connector.Error as e:
#                         # Handle database errors (e.g., connection lost)
#                         print("Database error:", e)
#                         print("Attempting to reconnect...")
#                         with self.alarm_lock:
#                             self.alarm_stack.update({"Database Exception #3": "Local database data saving error- Database is disconnected"})
#                             print("Database Exception #3: Local database data saving error- Database is disconnected")
#
#             except mysql.connector.Error as e0:
#                 # Handle connection errors (e.g., initial connection failure)
#                 print("Error connecting to MySQL database:", e0)
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"Database Exception #4": "Local database data saving error- Database is disconnected"})
#                 print("Database Exception #4 Local database data saving error- Database is disconnected")
#
#
#
#             time.sleep(self.base_period)
#
#         self.run()
#
#     def stop(self):
#         self.Running = False
#
#     def update_status(self, status):
#         self.status = status
#
#     def update_value(self, dic):
#         # print("Database received the data from PLC")
#         for key in self.TT_FP_dic:
#             self.TT_FP_dic[key] = dic["data"]["TT"]["FP"]["value"][key]
#
#         for key in self.TT_BO_dic:
#             self.TT_BO_dic[key] = dic["data"]["TT"]["BO"]["value"][key]
#         for key in self.PT_dic:
#             self.PT_dic[key] = dic["data"]["PT"]["value"][key]
#         for key in self.LEFT_REAL_dic:
#             self.LEFT_REAL_dic[key] = dic["data"]["LEFT_REAL"]["value"][key]
#         for key in self.AD_dic:
#             self.AD_dic[key] = dic["data"]["AD"]["value"][key]
#
#         for key in self.TT_FP_HighLimit:
#             self.TT_FP_HighLimit[key] = dic["data"]["TT"]["FP"]["high"][key]
#         for key in self.TT_BO_HighLimit:
#             self.TT_BO_HighLimit[key] = dic["data"]["TT"]["BO"]["high"][key]
#         for key in self.PT_HighLimit:
#             self.PT_HighLimit[key] = dic["data"]["PT"]["high"][key]
#         for key in self.LEFT_REAL_HighLimit:
#             self.LEFT_REAL_HighLimit[key] = dic["data"]["LEFT_REAL"]["high"][key]
#         for key in self.AD_HighLimit:
#             self.AD_HighLimit[key] = dic["data"]["AD"]["high"][key]
#
#         for key in self.TT_FP_LowLimit:
#             self.TT_FP_LowLimit[key] = dic["data"]["TT"]["FP"]["low"][key]
#         for key in self.TT_BO_LowLimit:
#             self.TT_BO_LowLimit[key] = dic["data"]["TT"]["BO"]["low"][key]
#         for key in self.PT_LowLimit:
#             self.PT_LowLimit[key] = dic["data"]["PT"]["low"][key]
#         for key in self.LEFT_REAL_LowLimit:
#             self.LEFT_REAL_LowLimit[key] = dic["data"]["LEFT_REAL"]["low"][key]
#         for key in self.AD_LowLimit:
#             self.AD_LowLimit[key] = dic["data"]["AD"]["low"][key]
#
#         for key in self.Valve_OUT:
#             self.Valve_OUT[key] = dic["data"]["Valve"]["OUT"][key]
#         for key in self.Valve_INTLKD:
#             self.Valve_INTLKD[key] = dic["data"]["Valve"]["INTLKD"][key]
#         for key in self.Valve_MAN:
#             self.Valve_MAN[key] = dic["data"]["Valve"]["MAN"][key]
#         for key in self.Valve_ERR:
#             self.Valve_ERR[key] = dic["data"]["Valve"]["ERR"][key]
#
#         for key in self.Switch_OUT:
#             self.Switch_OUT[key] = dic["data"]["Switch"]["OUT"][key]
#         for key in self.Switch_INTLKD:
#             self.Switch_INTLKD[key] = dic["data"]["Switch"]["INTLKD"][key]
#         for key in self.Switch_MAN:
#             self.Switch_MAN[key] = dic["data"]["Switch"]["MAN"][key]
#         for key in self.Switch_ERR:
#             self.Switch_ERR[key] = dic["data"]["Switch"]["ERR"][key]
#
#         for key in self.Din_dic:
#             self.Din_dic[key] = dic["data"]["Din"]["value"][key]
#
#         for key in self.TT_FP_Alarm:
#             self.TT_FP_Alarm[key] = dic["Alarm"]["TT"]["FP"][key]
#         for key in self.TT_BO_Alarm:
#             self.TT_BO_Alarm[key] = dic["Alarm"]["TT"]["BO"][key]
#         for key in self.PT_dic:
#             self.PT_Alarm[key] = dic["Alarm"]["PT"][key]
#         for key in self.LEFT_REAL_dic:
#             self.LEFT_REAL_Alarm[key] = dic["Alarm"]["LEFT_REAL"][key]
#         for key in self.AD_dic:
#             self.AD_Alarm[key] = dic["Alarm"]["AD"][key]
#
#         for key in self.LOOPPID_MODE0:
#             self.LOOPPID_MODE0[key] = dic["data"]["LOOPPID"]["MODE0"][key]
#         for key in self.LOOPPID_MODE1:
#             self.LOOPPID_MODE1[key] = dic["data"]["LOOPPID"]["MODE1"][key]
#         for key in self.LOOPPID_MODE2:
#             self.LOOPPID_MODE2[key] = dic["data"]["LOOPPID"]["MODE2"][key]
#         for key in self.LOOPPID_MODE3:
#             self.LOOPPID_MODE3[key] = dic["data"]["LOOPPID"]["MODE3"][key]
#         for key in self.LOOPPID_INTLKD:
#             self.LOOPPID_INTLKD[key] = dic["data"]["LOOPPID"]["INTLKD"][key]
#         for key in self.LOOPPID_MAN:
#             self.LOOPPID_MAN[key] = dic["data"]["LOOPPID"]["MAN"][key]
#         for key in self.LOOPPID_ERR:
#             self.LOOPPID_ERR[key] = dic["data"]["LOOPPID"]["ERR"][key]
#         for key in self.LOOPPID_SATHI:
#             self.LOOPPID_SATHI[key] = dic["data"]["LOOPPID"]["SATHI"][key]
#         for key in self.LOOPPID_SATLO:
#             self.LOOPPID_SATLO[key] = dic["data"]["LOOPPID"]["SATLO"][key]
#         for key in self.LOOPPID_EN:
#             self.LOOPPID_EN[key] = dic["data"]["LOOPPID"]["EN"][key]
#         for key in self.LOOPPID_OUT:
#             self.LOOPPID_OUT[key] = dic["data"]["LOOPPID"]["OUT"][key]
#         for key in self.LOOPPID_IN:
#             self.LOOPPID_IN[key] = dic["data"]["LOOPPID"]["IN"][key]
#         for key in self.LOOPPID_HI_LIM:
#             self.LOOPPID_HI_LIM[key] = dic["data"]["LOOPPID"]["HI_LIM"][key]
#         for key in self.LOOPPID_LO_LIM:
#             self.LOOPPID_LO_LIM[key] = dic["data"]["LOOPPID"]["LO_LIM"][key]
#         for key in self.LOOPPID_SET0:
#             self.LOOPPID_SET0[key] = dic["data"]["LOOPPID"]["SET0"][key]
#         for key in self.LOOPPID_SET1:
#             self.LOOPPID_SET1[key] = dic["data"]["LOOPPID"]["SET1"][key]
#         for key in self.LOOPPID_SET2:
#             self.LOOPPID_SET2[key] = dic["data"]["LOOPPID"]["SET2"][key]
#         for key in self.LOOPPID_SET3:
#             self.LOOPPID_SET3[key] = dic["data"]["LOOPPID"]["SET3"][key]
#
#         for key in self.LOOP2PT_OUT:
#             self.LOOP2PT_OUT[key] = dic["data"]["LOOP2PT"]["OUT"][key]
#         for key in self.LOOP2PT_SET1:
#             self.LOOP2PT_SET1[key] = dic["data"]["LOOP2PT"]["SET1"][key]
#         for key in self.LOOP2PT_SET2:
#             self.LOOP2PT_SET2[key] = dic["data"]["LOOP2PT"]["SET2"][key]
#         for key in self.LOOP2PT_SET3:
#             self.LOOP2PT_SET3[key] = dic["data"]["LOOP2PT"]["SET3"][key]
#
#         for key in self.Procedure_running:
#             self.Procedure_running[key] = dic["data"]["Procedure"]["Running"][key]
#         for key in self.Procedure_INTLKD:
#             self.Procedure_INTLKD[key] = dic["data"]["Procedure"]["INTLKD"][key]
#         for key in self.Procedure_EXIT:
#             self.Procedure_EXIT[key] = dic["data"]["Procedure"]["EXIT"][key]
#
#         for key in self.FLAG_DIC:
#             self.FLAG_DIC[key] = dic["data"]["FLAG"]["value"][key]
#         for key in self.FLAG_INTLKD:
#             self.FLAG_INTLKD[key] = dic["data"]["FLAG"]["INTLKD"][key]
#
#         for key in self.FF_DIC:
#             self.FF_DIC[key] = dic["data"]["FF"][key]
#         for key in self.PARAM_F_DIC:
#             self.PARAM_F_DIC[key] = dic["data"]["PARA_F"][key]
#
#         for key in self.PARAM_I_DIC:
#             self.PARAM_I_DIC[key] = dic["data"]["PARA_I"][key]
#         for key in self.PARAM_B_DIC:
#             self.PARAM_B_DIC[key] = dic["data"]["PARA_B"][key]
#         for key in self.PARAM_T_DIC:
#             self.PARAM_T_DIC[key] = dic["data"]["PARA_T"][key]
#         for key in self.TIME_DIC:
#             self.TIME_DIC[key] = dic["data"]["TIME"][key]
#
#         self.MainAlarm = dic["MainAlarm"]
#
#         print("Database received the data")
#
#     def write_data(self):
#         if self.para_TT >= self.rate_TT:
#             for key in self.TT_FP_dic:
#                 self.db.insert_data_into_stack(key, self.dt, self.TT_FP_dic[key])
#             for key in self.TT_BO_dic:
#                 self.db.insert_data_into_stack(key, self.dt, self.TT_BO_dic[key])
#             self.commit_bool = True
#             self.para_TT = 0
#         if self.para_PT >= self.rate_PT:
#             for key in self.PT_dic:
#                 self.db.insert_data_into_stack(key, self.dt, self.PT_dic[key])
#             # print("write pressure transducer")
#             self.commit_bool = True
#             self.para_PT = 0
#         # print(2)
#         for key in self.Valve_OUT:
#             if self.Valve_OUT[key] != self.Valve_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_OUT', self.early_dt, self.Valve_buffer[key])
#                 self.db.insert_data_into_stack(key + '_OUT', self.dt, self.Valve_OUT[key])
#                 self.Valve_buffer[key] = self.Valve_OUT[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         if self.para_Valve >= self.rate_Valve:
#             for key in self.Valve_OUT:
#                 self.db.insert_data_into_stack(key + '_OUT', self.dt, self.Valve_OUT[key])
#                 self.Valve_buffer[key] = self.Valve_OUT[key]
#                 self.commit_bool = True
#             self.para_Valve = 0
#         # print(3)
#         for key in self.Switch_OUT:
#             # print(key, self.Switch_OUT[key] != self.Switch_buffer[key])
#             if self.Switch_OUT[key] != self.Switch_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_OUT', self.early_dt, self.Switch_buffer[key])
#                 self.db.insert_data_into_stack(key + '_OUT', self.dt, self.Switch_OUT[key])
#                 self.Switch_buffer[key] = self.Switch_OUT[key]
#                 self.commit_bool = True
#                 # print(self.Switch_OUT[key])
#             else:
#                 pass
#
#         if self.para_Switch >= self.rate_Switch:
#             for key in self.Switch_OUT:
#                 self.db.insert_data_into_stack(key + '_OUT', self.dt, self.Switch_OUT[key])
#                 self.Switch_buffer[key] = self.Switch_OUT[key]
#                 self.commit_bool = True
#             self.para_Switch = 0
#         # print(4)
#         for key in self.Din_dic:
#             # print(key, self.Switch_OUT[key] != self.Switch_buffer[key])
#             if self.Din_dic[key] != self.Din_buffer[key]:
#                 self.db.insert_data_into_stack(key, self.early_dt, self.Din_buffer[key])
#                 self.db.insert_data_into_stack(key, self.dt, self.Din_dic[key])
#                 self.Din_buffer[key] = self.Din_dic[key]
#                 self.commit_bool = True
#             else:
#                 pass
#
#         if self.para_Din >= self.rate_Din:
#             for key in self.Din_dic:
#                 self.db.insert_data_into_stack(key, self.dt, self.Din_dic[key])
#                 self.Din_buffer[key] = self.Din_dic[key]
#             self.commit_bool = True
#             self.para_Din = 0
#
#         # if state of bool variable changes, write the data into database
#         # print(5)
#         for key in self.LOOPPID_EN:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.LOOPPID_EN[key] != self.LOOPPID_EN_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_EN', self.early_dt, self.LOOPPID_EN_buffer[key])
#                 self.db.insert_data_into_stack(key + '_EN', self.dt, self.LOOPPID_EN[key])
#                 self.LOOPPID_EN_buffer[key] = self.LOOPPID_EN[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         for key in self.LOOPPID_MODE0:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.LOOPPID_MODE0[key] != self.LOOPPID_MODE0_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_MODE0', self.early_dt, self.LOOPPID_MODE0_buffer[key])
#                 self.db.insert_data_into_stack(key + '_MODE0', self.dt, self.LOOPPID_MODE0[key])
#                 self.LOOPPID_MODE0_buffer[key] = self.LOOPPID_MODE0[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         for key in self.LOOPPID_MODE1:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.LOOPPID_MODE1[key] != self.LOOPPID_MODE1_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_MODE1', self.early_dt, self.LOOPPID_MODE1_buffer[key])
#                 self.db.insert_data_into_stack(key + '_MODE1', self.dt, self.LOOPPID_MODE1[key])
#                 self.LOOPPID_MODE1_buffer[key] = self.LOOPPID_MODE1[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         for key in self.LOOPPID_MODE2:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.LOOPPID_MODE2[key] != self.LOOPPID_MODE2_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_MODE2', self.early_dt, self.LOOPPID_MODE2_buffer[key])
#                 self.db.insert_data_into_stack(key + '_MODE2', self.dt, self.LOOPPID_MODE2[key])
#                 self.LOOPPID_MODE2_buffer[key] = self.LOOPPID_MODE2[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         for key in self.LOOPPID_MODE3:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.LOOPPID_MODE3[key] != self.LOOPPID_MODE3_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_MODE3', self.early_dt, self.LOOPPID_MODE3_buffer[key])
#                 self.db.insert_data_into_stack(key + '_MODE3', self.dt, self.LOOPPID_MODE3[key])
#                 self.LOOPPID_MODE3_buffer[key] = self.LOOPPID_MODE3[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         # if no changes, write the data every fixed time interval
#         # print(6)
#         if self.para_LOOPPID >= self.rate_LOOPPID:
#             for key in self.LOOPPID_EN:
#                 self.db.insert_data_into_stack(key + '_EN', self.dt, self.LOOPPID_EN[key])
#                 self.LOOPPID_EN_buffer[key] = self.LOOPPID_EN[key]
#             for key in self.LOOPPID_MODE0:
#                 self.db.insert_data_into_stack(key + '_MODE0', self.dt, self.LOOPPID_MODE0[key])
#                 self.LOOPPID_MODE0_buffer[key] = self.LOOPPID_MODE0[key]
#             for key in self.LOOPPID_MODE1:
#                 self.db.insert_data_into_stack(key + '_MODE1', self.dt, self.LOOPPID_MODE1[key])
#                 self.LOOPPID_MODE1_buffer[key] = self.LOOPPID_MODE1[key]
#             for key in self.LOOPPID_MODE2:
#                 self.db.insert_data_into_stack(key + '_MODE2', self.dt, self.LOOPPID_MODE2[key])
#                 self.LOOPPID_MODE2_buffer[key] = self.LOOPPID_MODE2[key]
#             for key in self.LOOPPID_MODE3:
#                 self.db.insert_data_into_stack(key + '_MODE3', self.dt, self.LOOPPID_MODE3[key])
#                 self.LOOPPID_MODE3_buffer[key] = self.LOOPPID_MODE3[key]
#             # write float data.
#             for key in self.LOOPPID_OUT:
#                 self.db.insert_data_into_stack(key + '_OUT', self.dt, self.LOOPPID_OUT[key])
#                 self.LOOPPID_OUT_buffer[key] = self.LOOPPID_OUT[key]
#             for key in self.LOOPPID_IN:
#                 self.db.insert_data_into_stack(key + '_IN', self.dt, self.LOOPPID_IN[key])
#                 self.LOOPPID_IN_buffer[key] = self.LOOPPID_IN[key]
#             self.commit_bool = True
#             self.para_LOOPPID = 0
#         # print(7)
#
#         for key in self.LOOP2PT_OUT:
#             # print(7)
#             # print(8)
#             # print(key, self.LOOP2PT_OUT[key])
#             if self.LOOP2PT_OUT[key] != self.LOOP2PT_OUT_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_OUT', self.early_dt, self.LOOP2PT_OUT_buffer[key])
#                 self.db.insert_data_into_stack(key + '_OUT', self.dt, self.LOOP2PT_OUT[key])
#                 self.LOOP2PT_OUT_buffer[key] = self.LOOP2PT_OUT[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         for key in self.LOOP2PT_MODE0:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.LOOP2PT_MODE0[key] != self.LOOP2PT_MODE0_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_MODE0', self.early_dt, self.LOOP2PT_MODE0_buffer[key])
#                 self.db.insert_data_into_stack(key + '_MODE0', self.dt, self.LOOP2PT_MODE0[key])
#                 self.LOOP2PT_MODE0_buffer[key] = self.LOOP2PT_MODE0[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         for key in self.LOOP2PT_MODE1:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.LOOP2PT_MODE1[key] != self.LOOP2PT_MODE1_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_MODE1', self.early_dt, self.LOOP2PT_MODE1_buffer[key])
#                 self.db.insert_data_into_stack(key + '_MODE1', self.dt, self.LOOP2PT_MODE1[key])
#                 self.LOOP2PT_MODE1_buffer[key] = self.LOOP2PT_MODE1[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#         for key in self.LOOP2PT_MODE2:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.LOOP2PT_MODE2[key] != self.LOOP2PT_MODE2_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_MODE2', self.early_dt, self.LOOP2PT_MODE2_buffer[key])
#                 self.db.insert_data_into_stack(key + '_MODE2', self.dt, self.LOOP2PT_MODE2[key])
#                 self.LOOP2PT_MODE2_buffer[key] = self.LOOP2PT_MODE2[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#         for key in self.LOOP2PT_MODE3:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.LOOP2PT_MODE3[key] != self.LOOP2PT_MODE3_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_MODE3', self.early_dt, self.LOOP2PT_MODE3_buffer[key])
#                 self.db.insert_data_into_stack(key + '_MODE3', self.dt, self.LOOP2PT_MODE3[key])
#                 self.LOOP2PT_MODE3_buffer[key] = self.LOOP2PT_MODE3[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#         if self.para_LOOP2PT >= self.rate_LOOP2PT:
#
#             for key in self.LOOP2PT_MODE0:
#                 self.db.insert_data_into_stack(key + '_MODE0', self.dt, self.LOOP2PT_MODE0[key])
#                 self.LOOP2PT_MODE0_buffer[key] = self.LOOP2PT_MODE0[key]
#             for key in self.LOOP2PT_MODE1:
#                 self.db.insert_data_into_stack(key + '_MODE1', self.dt, self.LOOP2PT_MODE1[key])
#                 self.LOOP2PT_MODE1_buffer[key] = self.LOOP2PT_MODE1[key]
#             for key in self.LOOP2PT_MODE2:
#                 self.db.insert_data_into_stack(key + '_MODE2', self.dt, self.LOOP2PT_MODE2[key])
#                 self.LOOP2PT_MODE2_buffer[key] = self.LOOP2PT_MODE2[key]
#             for key in self.LOOP2PT_MODE3:
#                 self.db.insert_data_into_stack(key + '_MODE3', self.dt, self.LOOP2PT_MODE3[key])
#                 self.LOOP2PT_MODE3_buffer[key] = self.LOOP2PT_MODE3[key]
#             # write float data.
#             for key in self.LOOP2PT_OUT:
#                 self.db.insert_data_into_stack(key + '_OUT', self.dt, self.LOOP2PT_OUT[key])
#                 self.LOOP2PT_OUT_buffer[key] = self.LOOP2PT_OUT[key]
#
#             self.commit_bool = True
#             self.para_LOOP2PT = 0
#
#         if self.para_REAL >= self.rate_REAL:
#             for key in self.LEFT_REAL_address:
#                 # print(key, self.LEFT_REAL_dic[key])
#                 self.db.insert_data_into_stack(key, self.dt, self.LEFT_REAL_dic[key])
#                 # print("write pressure transducer")
#                 self.commit_bool = True
#             self.para_REAL = 0
#
#         if self.para_AD >= self.rate_AD:
#             for key in self.AD_address:
#                 # print(key, self.AD_dic[key])
#                 self.db.insert_data_into_stack(key, self.dt, self.AD_dic[key])
#                 # print("write pressure transducer")
#                 self.commit_bool = True
#             self.para_AD = 0
#
#         # #FLAGS
#         for key in self.FLAG_INTLKD:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.FLAG_INTLKD[key] != self.FLAG_INTLKD_buffer[key]:
#                 self.db.insert_data_into_stack(key + '_INTLKD', self.early_dt, self.FLAG_INTLKD_buffer[key])
#                 self.db.insert_data_into_stack(key + '_INTLKD', self.dt, self.FLAG_INTLKD[key])
#                 self.db.insert_data_into_stack(key, self.dt, self.FLAG_DIC[key])
#                 self.FLAG_INTLKD_buffer[key] = self.FLAG_INTLKD[key]
#                 self.commit_bool = True
#             else:
#                 pass
#
#         if self.para_FLAG >= self.rate_FLAG:
#             for key in self.FLAG_INTLKD:
#                 self.db.insert_data_into_stack(key, self.dt, self.FLAG_DIC[key])
#                 self.db.insert_data_into_stack(key + '_INTLKD', self.dt, self.FLAG_INTLKD[key])
#                 self.FLAG_INTLKD_buffer[key] = self.FLAG_INTLKD[key]
#                 self.commit_bool = True
#             self.para_FLAG = 0
#
#         # FF
#         for key in self.FF_DIC:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.FF_DIC[key] != self.FF_buffer[key]:
#                 self.db.insert_data_into_stack(key, self.early_dt, self.FF_buffer[key])
#                 self.db.insert_data_into_stack(key, self.dt, self.FF_DIC[key])
#                 self.FF_buffer[key] = self.FF_DIC[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         if self.para_FF >= self.rate_FF:
#             for key in self.FF_DIC:
#                 self.db.insert_data_into_stack(key, self.dt, self.FF_DIC[key])
#                 self.FF_buffer[key] = self.FF_DIC[key]
#                 self.commit_bool = True
#             self.para_FF = 0
#
#         # PARAM_B
#         for key in self.PARAM_B_DIC:
#             # print(key, self.Valve_OUT[key] != self.Valve_buffer[key])
#             if self.PARAM_B_DIC[key] != self.PARAM_B_buffer[key]:
#                 self.db.insert_data_into_stack(key, self.early_dt, self.PARAM_B_buffer[key])
#                 self.db.insert_data_into_stack(key, self.dt, self.PARAM_B_DIC[key])
#                 self.PARAM_B_buffer[key] = self.PARAM_B_DIC[key]
#                 self.commit_bool = True
#                 # print(self.Valve_OUT[key])
#             else:
#                 pass
#
#         if self.para_PARAM_B >= self.rate_PARAM_B:
#             for key in self.PARAM_B_DIC:
#                 self.db.insert_data_into_stack(key, self.dt, self.PARAM_B_DIC[key])
#                 self.PARAM_B_buffer[key] = self.PARAM_B_DIC[key]
#                 self.commit_bool = True
#             self.para_PARAM_B = 0
#
#         # other parameters I/F/T
#         if self.para_PARAM_F >= self.rate_PARAM_F:
#             for key in self.PARAM_F_DIC:
#                 self.db.insert_data_into_stack(key, self.dt, self.PARAM_F_DIC[key])
#
#                 self.commit_bool = True
#             self.para_PARAM_F = 0
#
#         if self.para_PARAM_I >= self.rate_PARAM_I:
#             for key in self.PARAM_I_DIC:
#                 self.db.insert_data_into_stack(key, self.dt, self.PARAM_I_DIC[key])
#
#                 self.commit_bool = True
#             self.para_PARAM_I = 0
#
#         if self.para_PARAM_T >= self.rate_PARAM_T:
#             for key in self.PARAM_T_DIC:
#                 self.db.insert_data_into_stack(key, self.dt, self.PARAM_T_DIC[key])
#
#                 self.commit_bool = True
#             self.para_PARAM_T = 0
#
#         if self.para_TIME >= self.rate_TIME:
#             for key in self.TIME_DIC:
#                 self.db.insert_data_into_stack(key, self.dt, self.TIME_DIC[key])
#
#                 self.commit_bool = True
#             self.para_TIME = 0
#
#         # print("a",self.para_TT,"b",self.para_PT )
#         # print(8)
#
#         # commit the changes at last step only if it is time to write
#         if self.commit_bool:
#             # put alll commands into stack which is a pandas dataframe, reorder it by timestamp and then transform them into mysql queries
#             self.db.sort_stack()
#             self.db.convert_stack_into_queries()
#             self.db.drop_stack()
#             self.db.db.commit()
#         print("Writing data to database...")
#
#         self.para_TT += 1
#         self.para_PT += 1
#         self.para_Valve += 1
#         self.para_Switch += 1
#         self.para_LOOPPID += 1
#         self.para_LOOP2PT += 1
#         self.para_REAL += 1
#         self.para_AD += 1
#         self.para_Din += 1
#         self.para_FLAG += 1
#         self.para_FF += 1
#         self.para_PARAM_T += 1
#         self.para_PARAM_I += 1
#         self.para_PARAM_B += 1
#         self.para_PARAM_F += 1
#         self.para_TIME += 1
#
#
# class Message_Manager(threading.Thread):
#     # add here the other alarm and database
#     def __init__(self, global_time, timelock, alarm_stack, alarm_lock):
#         super().__init__()
#         self.alarm_init()
#         self.running = True
#         self.global_time = global_time
#         self.clock = self.global_time["clock"]  # hanging when on hold to slack -> internet connection/slack server
#         self.db_time =  self.global_time["dbtime"] # hanging when disconnected from mysql
#         self.slack_time = self.global_time["slacktime"]  # hanging when slack fail
#         self.plc_time = self.global_time["plctime"]  # hanging when Beckhoff/NI/Arduino fail
#         self.socketserver_time = self.global_time["sockettime"]  # hanging when socket to GUI fail
#         self.time_lock = timelock
#
#         self.alarm_stack = alarm_stack
#         self.alarm_lock = alarm_lock
#         self.para_alarm = env.MAINALARM_PARA
#         self.rate_alarm = env.MAINALARM_RATE
#         self.base_period = 1
#
#     def alarm_init(self):
#         # info about tencent mail settings
#         self.host_server = "smtp.qq.com"
#         self.sender_qq = "390282332"
#         self.pwd = "bngozrzmzsbocafa"
#         self.sender_mail = "390282332@qq.com"
#         # self.receiver1_mail = "cdahl@northwestern.edu"
#         self.receiver1_mail = "runzezhang@foxmail.com"
#         self.mail_title = "Alarm from SBC"
#
#         # server to pico watchdog
#
#         # info about slack settings
#         # SLACK_BOT_TOKEN is a linux enviromental variable saved locally on sbcslowcontrol machine
#         # it can be fetched on slack app page in SBCAlarm app: https://api.slack.com/apps/A035X77RW64/general
#         # if not_in_channel error type /invite @SBC_Alarm in channel
#         try:
#             self.slack_init()
#         except (SlackApiError, Exception) as e:
#             with self.alarm_lock:
#                 self.alarm_stack.update({"Slack Exception": "Slack Connection Error"})
#
#
#     def slack_init(self):
#         self.client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
#         self.logger = logging.getLogger(__name__)
#         self.channel_id = "C01A549VDHS"
#
#
#
#     def tencent_alarm(self, message):
#         try:
#             # The body content of the mail
#             mail_content = " Alarm from SBC slowcontrol: " + message
#             # sslLogin
#             smtp = SMTP_SSL(self.host_server)
#             # set_debuglevel() is used for debugging. The parameter value is 1 to enable debug mode and 0 to disable debug mode.
#             smtp.set_debuglevel(1)
#             smtp.ehlo(self.host_server)
#             smtp.login(self.sender_qq, self.pwd)
#             # Define mail content
#             msg = MIMEText(mail_content, "plain", "utf-8")
#             msg["Subject"] = Header(self.mail_title, "utf-8")
#             msg["From"] = self.sender_mail
#             msg["To"] = self.receiver1_mail
#             # send email
#             smtp.sendmail(self.sender_mail, self.receiver1_mail, msg.as_string())
#             smtp.quit()
#             print("mail sent successfully")
#         except Exception as e:
#             print("mail failed to send")
#             print("Error",e)
#
#     def slack_alarm(self, message):
#         # Call the conversations.list method using the WebClient
#         result = self.client.chat_postMessage(
#             channel=self.channel_id,
#             text=str(message)
#             # You could also use a blocks[] array to send richer content
#         )
#         # Print result, which includes information about the message (like TS)
#
#         print("slackalarm",result)
#
#
#     def slack_alarm_fake(self, message):
#         # try:
#         self.client_fake = WebClient(token="feauhieai3289")
#         # Call the conversations.list method using the WebClient
#         result = self.client_fake.chat_postMessage(
#             channel=self.channel_id,
#             text=str(message)
#
#             # You could also use a blocks[] array to send richer content
#         )
#         # Print result, which includes information about the message (like TS)
#
#         print("slackalarm",result)
#
#         # except SlackApiError as e:
#         #     with self.alarm_lock:
#         #         self.alarm_stack.update({"Slack Exception": "Slack Connection Error"})
#         #     print("Slack",f"Error1: {e}", self.alarm_stack)
#
#     def run(self):
#         alarm_received = {}
#         while self.running:
#             try:
#                 with self.alarm_lock:
#                     alarm_received.update(self.alarm_stack)
#                 with self.time_lock:
#                     self.global_time.update({"slacktime": datetime_in_1e5micro()})
#
#
#                 print("slack", alarm_received)
#                 print("Message Manager running ", self.global_time["slacktime"])
#
#                 if self.para_alarm >= self.rate_alarm:
#                     if alarm_received != {}:
#                         self.slack_init()
#                         msg = self.join_stack_into_message(alarm_received)
#                         self.slack_alarm(msg)
#
#                     # and clear the alarm stack
#                     with self.alarm_lock:
#                         self.alarm_stack.clear()
#                         alarm_received.clear()
#                         print("alarm stack cleared", self.alarm_stack, alarm_received)
#                     self.para_alarm = 0
#
#                 self.para_alarm += 1
#                 time.sleep(self.base_period)
#
#
#
#             except (SlackApiError,Exception) as e:
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"Slack Exception": "Slack Connection Error"})
#                 print("Slack exception Error2",e)
#                 # restart itself
#                 time.sleep(self.base_period*60)
#                 break
#         self.run()
#
#
#     def join_stack_into_message(self, dic):
#         message = ""
#         if len(dic) >= 1:
#             for key in dic:
#                 message = message + "\n" + dic[key]
#         return message
#
#
#
# class LocalWatchdog(threading.Thread):
#     def __init__(self, global_time, timelock, alarm_stack, alarm_lock):
#         # alarm msg is different from coupp msg
#         super().__init__()
#         self.global_time = global_time
#         self.timelock = timelock
#         self.alarm_db = COUPP_database()
#         self.alarm_stack = alarm_stack
#         self.alarm_lock = alarm_lock
#         self.running = True
#         # time parameters
#         self.clock = self.global_time["clock"]  # hanging when on hold to slack -> internet connection/slack server
#         self.db_time = self.global_time["dbtime"]  # hanging when disconnected from mysql
#         self.slack_time = self.global_time["slacktime"]  # hanging when ssh fail or coupp mysql fail
#         self.plc_time = self.global_time["plctime"]  # hanging when Beckhoff/NI/Arduino fail
#         self.socketserver_time = self.global_time["sockettime"]  # hanging when socket to GUI fail
#         self.para_alarm = env.MAINALARM_PARA
#         self.rate_alarm = env.MAINALARM_RATE
#         self.para_long_alarm = env.MAINALARM_LONG_PARA
#         self.rate_long_alarm = env.MAINALARM_LONG_RATE
#         self.database_timeout = env.DATABASE_HOLD
#         self.plc_timeout = env.PLC_HOLD
#         self.socket_timeout = env.SOCKET_HOLD
#         self.slack_timeout = env.SLACK_HOLD
#         self.base_period = 1
#
#     def run(self):
#         alarm_received = {}
#         while self.running:
#             try:
#
#                 with self.timelock:
#                     self.global_time.update({"clock":datetime_in_1e5micro()})
#                     # update all times
#                     self.clock = self.global_time[
#                         "clock"]  # hanging when on hold to slack -> internet connection/slack server
#                     self.db_time = self.global_time["dbtime"]  # hanging when disconnected from mysql
#
#                     self.slack_time = self.global_time["slacktime"]  # hanging when ssh fail or coupp mysql fail
#                     self.plc_time = self.global_time["plctime"]  # hanging when Beckhoff/NI/Arduino fail
#                     self.socketserver_time = self.global_time["sockettime"]
#
#                 print("Local watchdog running", self.global_time["clock"], self.global_time["plctime"])
#
#                 # Valid when plc is updating.
#                 # otherwise alarm the plc is disconnected or on hold, add alarm to alarm stack
#                 # We only consider time_out may happen in socket connections here and socket module will restart itself
#                 # because it can detect timeout signal by itself
#                 # Other module, we may just consider that the disconnection can happen and they will restart themselves
#                 # But good to know time_out and manually restart them
#                 if (self.clock - self.plc_time).total_seconds() > self.plc_timeout:
#                     self.alarm_stack.update({"PLC CONNECTION TIMEOUT": "PLC hasn't update long than {time} s".format(
#                         time=self.plc_timeout)})
#                 # In principle, no need to exist bc if it timeout, COUPP txt message will be sent out
#                 if (self.clock - self.slack_time).total_seconds() > self.slack_timeout:
#                     self.alarm_stack.update({"SLACK TIMEOUT": "slack hasn't update long than {time} s".format(
#                         time=self.slack_timeout)})
#                 # because when no client, the server is always on hold
#                 # if (self.clock - self.socketserver_time).total_seconds() > self.socket_timeout:
#                 #     alarm_received.update({"SOCKET TIMEOUT": "SOCKET TO GUI hasn't update long than {time} s".format(time=self.socket_timeout)})
#                 if (self.clock - self.db_time).total_seconds() > self.database_timeout:
#                     self.alarm_stack.update({"DATABASE TIMEOUT": "Database hasn't update long than {time} s".format(
#                         time=self.database_timeout)})
#                 with self.alarm_lock:
#                     alarm_received.update(self.alarm_stack)
#                     alarm_received_txt = self.join_stack_into_message(alarm_received)
#
#                 if self.para_alarm >= self.rate_alarm:
#
#                     # send alarm msg to database, Otherwise, send text message about alarm
#                     if alarm_received_txt == "":
#                         self.alarm_db.ssh_write()
#                     else:
#                         self.alarm_db.ssh_alarm(message=alarm_received_txt)
#                     self.para_alarm = 0
#                     # loop is active in case slack channel isinactive.
#                     # this is 300s loop, if longer than this, the alarms will be cleared out.
#                     if self.para_long_alarm >= self.rate_long_alarm:
#                         with self.alarm_lock:
#                             alarm_received.clear()
#                             self.alarm_stack.clear()
#                         self.para_long_alarm = 0
#                 self.para_alarm += 1
#                 self.para_long_alarm += 1
#                 time.sleep(self.base_period)
#
#             except (sshtunnel.BaseSSHTunnelForwarderError, pymysql.Error,Exception)  as e:
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"COUPP_server_connection_error": "Failed to connected to watchdog machine "
#                                                                               "on COUPP server. Restarting"})
#                 print("watchdog Error",e)
#                 # restart itself
#                 time.sleep(self.base_period * 60)
#                 break
#         self.run()
#
#
#     def join_stack_into_message(self, dic):
#         message = ""
#         if len(dic) >= 1:
#             for key in dic:
#                 message = message + "\n" + dic[key]
#         return message
#
#
# class UpdateServer(threading.Thread):
#     def __init__(self, plc_data, plc_lock, command_data, command_lock, global_time, timelock, alarm_lock, alarm_stack):
#         super().__init__()
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.global_time = global_time
#         self.sockettime = global_time["sockettime"]
#         self.timelock = timelock
#         self.host = '127.0.0.1'
#         self.port = 6666
#         self.server_socket.bind((self.host, self.port))
#         self.server_socket.listen(1)
#         print("Server listening on {host}:{port}".format(host=self.host, port = self.port))
#
#         self.plc_data = plc_data
#         self.plc_lock = plc_lock
#         self.command_data = command_data
#         self.command_lock = command_lock
#         self.alarm_lock = alarm_lock
#         self.alarm_stack = alarm_stack
#         self.period = 1
#
#         self.data_package = pickle.dumps(self.plc_data)
#
#     def run(self):
#         self.Running = True
#
#
#         while self.Running:
#             try:
#                 conn, addr = self.server_socket.accept()
#
#                 print(f"Connection from {addr}")
#
#                 # Set a timeout for socket operations to 10 seconds
#                 conn.settimeout(10)
#                 while True:
#                     with self.timelock:
#                         self.global_time.update({"sockettime":datetime_in_1e5micro()})
#                         print("Socket Server Updating", self.global_time["sockettime"])
#
#                     received_data = pickle.loads(self.receive_data(conn))
#                     self.update_data_signal(received_data)
#                     #pack data and send out
#
#                     self.pack_data(conn)
#
#
#                     time.sleep(self.period)  # Sleep for 1 seconds before sending data again
#
#             except socket.timeout:
#                 print("Connection timed out. Restarting server...")
#                 conn.close()
#             except BrokenPipeError:
#                 print("Client disconnected. Waiting for the next connection...")
#                 conn.close()  # Sleep for 1 second before sending data again
#             except Exception as e:
#                 print(f"Exception: {e}")
#                 conn.close()
#             finally:
#                 with self.alarm_lock:
#                     self.alarm_stack.update({"Socket Server updating Exception":"Socket Server updating loop broke. Restarting..."})
#                 break
#
#         self.run()
#
#     def stop(self):
#         self.server_socket.close()
#         self.Running = False
#
#     def update_data_signal(self, received_dict):
#         with self.command_lock:
#             self.command_data.update(received_dict)
#         # print("command data in server socket", self.command_data)
#     def pack_data(self, conn):
#         data_transfer = pickle.dumps(self.plc_data)
#
#         # Send JSON data to the client
#         conn.sendall(len(data_transfer).to_bytes(4, byteorder='big'))
#
#         # Send the serialized data in chunks
#         for i in range(0, len(data_transfer), 1024):
#             chunk = data_transfer[i:i + 1024]
#             conn.sendall(chunk)
#     def receive_data(self, conn):
#         data_length_bytes = conn.recv(4)
#         data_length = struct.unpack('!I', data_length_bytes)[0]
#
#         # Receive the serialized data in chunks
#         received_data = b''
#         while len(received_data) < data_length:
#             chunk = conn.recv(min(1024, data_length - len(received_data)))
#             if not chunk:
#                 break
#             received_data += chunk
#         return received_data
#
#
# class MainClass():
#     def __init__(self):
#         self.plc_data = copy.deepcopy(env.DIC_PACK)
#         self.global_time={"plctime":datetime_in_1e5micro(),"dbtime":datetime_in_1e5micro(),"slacktime":datetime_in_1e5micro(),"sockettime":datetime_in_1e5micro(),
#                           "clock":datetime_in_1e5micro()}
#         self.plc_lock = threading.Lock()
#         self.command_data = {}
#         self.command_lock = threading.Lock()
#         self.alarm_stack  = {}
#         self.alarm_lock = threading.Lock()
#         self.timelock = threading.Lock()
#         self.StartUpdater()
#
#
#     def StartUpdater(self):
#
#         # Read PLC value on another thread
#         self.threadPLC = UpdatePLC(plc_data=self.plc_data, plc_lock=self.plc_lock, command_data=self.command_data,
#                                    command_lock=self.command_lock, global_time=self.global_time, timelock=self.timelock,
#                                    alarm_stack=self.alarm_stack, alarm_lock=self.alarm_lock)
#
#         self.threadDatabase = UpdateDataBase(plc_data=self.plc_data, plc_lock=self.plc_lock, global_time=self.global_time,
#                                              timelock=self.timelock, alarm_stack=self.alarm_stack, alarm_lock=self.alarm_lock)
#
#         self.threadWatchdog = LocalWatchdog(global_time=self.global_time,
#                                             timelock=self.timelock,
#                                             alarm_stack=self.alarm_stack, alarm_lock=self.alarm_lock)
#
#         self.threadSocket = UpdateServer(plc_data=self.plc_data, plc_lock=self.plc_lock, command_data=self.command_data,
#                                          command_lock=self.command_lock, global_time=self.global_time,
#                                          timelock=self.timelock, alarm_lock=self.alarm_lock, alarm_stack=self.alarm_stack)
#
#         self.threadMessager = Message_Manager(global_time=self.global_time, timelock=self.timelock,
#                                               alarm_stack=self.alarm_stack, alarm_lock=self.alarm_lock)
#
#         # wait for PLC initialization finished
#         self.threadPLC.start()
#         time.sleep(0.5)
#         self.threadDatabase.start()
#         time.sleep(0.1)
#         self.threadWatchdog.start()
#         time.sleep(0.1)
#         self.threadSocket.start()
#         time.sleep(0.1)
#         self.threadMessager.start()
#
#
#     def StopUpdater(self):
#         self.threadPLC.join()
#         time.sleep(1)
#         self.threadDatabase.join()
#         time.sleep(1)
#         self.threadWatchdog.join()
#         time.sleep(1)
#         self.threadSocket.join()
#         time.sleep(1)
#         self.threadMessager.join()
#         time.sleep(1)
#         for i in range(10):
#             print(i)
#             time.sleep(1)
#
#
#

if __name__ == "__main__":
    # MC = MainClass()
    test_crontab("imported")