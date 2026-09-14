"""Function for reading Lakeshore module"""

import struct, time, zmq, sys, pickle, copy, logging
import numpy as np
from PySide2 import QtWidgets, QtCore, QtGui
# import smtplib
# import ssl
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
import socket
import requests
import logging,os

# delete random number package when you read real data from PLC
import random
from pymodbus.client.sync import ModbusTcpClient
from lakeshore import Model336

# Initialization of Address, Value Matrix

logging.basicConfig(filename="/home/hep/sbc_error_log.log")
sys._excepthook = sys.excepthook

# 2 global function to transfer Lakshore direct output(string) to a list
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

# This is a class, a custom package we wrote
class PLC(QtCore.QObject):
    # initilaztion function, this will be called automatically after the package is called
    def __init__(self):
        super().__init__()

        # Lakeshore
        # Lakshore product ID
        # and we use Lakeshore package to connect to client
        self.IP_LS1 = 'LSA2BVC'
        # port is by default 7777
        self.PORT_LS1 = 7777
        self.LS1_con = False
        # test the connection
        try:
            self.Client_LS1 = Model336(serial_number=self.IP_LS1, tcp_port=self.PORT_LS1)
            self.LS1_con = True
            print("LS1 connected: " + str(self.LS1_con))
        except:
            self.LS1_con = False
            print("LS1 connected: " + str(self.LS1_con))

        self.LS1_updatesignal = False

        # initliaztion of heaters address and its reading. trivial readout is 0.
        # 1st digit is the number of Lakeshore, bc we only have 1 for example, it is always 0
        # 2nd digit is the number of Heater
        self.self.LOOPPID_ADR_BASE =  {'HTR1001': (0,0), 'HTR1002': (0,1), 'HTR1003': (0,2)}
        self.self.LOOPPID_OUT =  {'HTR1001': 0, 'HTR1002': 0, 'HTR1003': 0}

        # first digit is the number of Lakeshore, bc now we only have 1 for example, so it is 0
        # second digit is the number of Heater (1 heater can have up to 2 feedback RTDs),
        # the 3rd digit is the number of feedback RTD

        self.HTRTD_address = {"RTD4":(0,0,0),"RTD5":(0,0,1),"RTD6":(0,1,0)}
        self.HTRD_dic = {"RTD4":0,"RTD5":0,"RTD6":0}

        # run the main function
        self.main_function()


    def Read_LS(self):

        Raw_LS_power = {}
        Raw_LS_TT = {}
        self.LS_timeout = 5


        for key in self.LOOPPID_ADR_BASE:
        # part of command to fetch heater power
            command_base = "HTR?"
        # command part to specify which heater
            command_middle = str(self.LOOPPID_ADR_BASE[key][1] + 1)
        # combine the two commands to get the complete final command
            command0 = command_base + command_middle
            # if this is to get heater from 1st lakeshore  and it is connected
            if self.LOOPPID_ADR_BASE[key][0] == 0 and self.LS1_con:
                print("connection success!", key)
                try:
                    Raw_LS_power[key] = float(LS_OUT_translate(self.Client_LS1.query(command0)))
                except:
                    Raw_LS_power[key] = -1

        print("OUTPUT POWER", Raw_LS_power)
        # strip the + symbol from the output and make it to float
        for key in self.LOOPPID_ADR_BASE:
            try:
                stripped = Raw_LS_power[key].strip("+")
            except:
                stripped = Raw_LS_power[key]
            self.LOOPPID_OUT[key] = float(stripped)
        print("HTR OUT", self.LOOPPID_OUT)

        # RTD read is all pulled out once (1,2,3,4), so we can read the tuple first and give it to Raw_dic
        # this reduces the times we communicates with the LS server by a factor of 4
        # too many communications in a short of time can cause LS server to crash
        command_base = "KRDG?"
        # command_middle=str(self.LOOPPID_ADR_BASE[key][1])
        command_middle = "0"
        command0 = command_base + command_middle

        try:
            # KRDG? unlike HTR?, will return all the RTD readings at once as a tuple
            output_tuple = LS_TT_translate(self.Client_LS1.query(command0))

            for key in self.HTRTD_address:
                if self.HTRTD_address[key][0] == 0 and self.LS1_con:
                    # distribute value to corresponding RTD key
                    Raw_LS_TT[key] = output_tuple[
                        2 * self.HTRTD_address[key][1] + self.HTRTD_address[key][2]]
        except:
            for key in self.HTRTD_address:
                if self.HTRTD_address[key][0] == 0:
                    Raw_LS_TT[key] = -1


        for key in self.HTRTD_address:
            self.HTRTD_dic[key] = Raw_LS_TT[key]
        print("HTR RTDs", self.HTRTD_dic)

    def main_function(self):
        # main body of the class-- will call the Read_LS function every 1 seconds.
        while True:
            self.Read_LS()
            time.sleep(1)





# then this is the main function for the script. We need to call the class
if __name__ == '__main__':
    # call the class and it will run the init function
    PLC = PLC()


