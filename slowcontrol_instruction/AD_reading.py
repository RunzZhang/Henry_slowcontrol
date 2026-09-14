"""Function for reading adam module"""

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
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError

# delete random number package when you read real data from PLC
import random
from pymodbus.client.sync import ModbusTcpClient


# Initialization of Address, Value Matrix

logging.basicConfig(filename="/home/hep/sbc_error_log.log")
sys._excepthook = sys.excepthook


# This is a class, a custom package we wrote
class PLC(QtCore.QObject):
    # initilaztion function, this will be called automatically after the package is called
    def __init__(self):
        super().__init__()

        # Adam
        # fill in the Adam IP address here and default Adam port is 502
        # Here we use the modbus protocol so the python package is ModbusTcpClient
        IP_AD1 = "10.111.19.101"
        PORT_AD1 = 502
        # try to connect
        self.Client_AD1 = ModbusTcpClient(IP_AD1, port=PORT_AD1)
        # show connection result
        self.Connected_AD1 = self.Client_AD1.connect()
        print(" AD1 connected: " + str(self.Connected_AD1))

        # initliaztion of RTD address and its reading. trivial readout is 0.
        # the address from channel 1 to 8 is from 0 to 7.
        self.TT_AD1_address = {"RTD7": 0, "RTD8":1, "RTD9": 2, "RTD10": 3}
        self.TT_AD1_dic = {"RTD7": 0, "RTD8":0, "RTD9": 0, "RTD10": 0}

        # run the main function
        self.main_function()


    def Read_AD(self):

        Raw_RTDs_AD1 = {}
        # if the connection is true
        if self.Connected_AD1:
            # loop around the address
            for key in self.TT_AD1_address:
                Raw_RTDs_AD1[key] = self.Client_AD1.read_holding_registers(self.TT_AD1_address[key], count=1, unit=0x01)
                # The readout Raw_RTDs_AD1[key] is digital reading which is scaled from 0 to 2^16 -- Raw_RTDs_AD1[key].getRegister(0)/2**16
                # we need to scale this back to -200 to 200 centigrade first if you set the temperature range is -200 to 200C -- read value = -200+400* input
                read_value = -200+400*Raw_RTDs_AD1[key].getRegister(0)/2**16
                # if the value is valid, if no reading like NA, then directly output result and we know that should be invalid
                # also round number to 2 digits
                if read_value < 201:
                # change C to K
                    self.TT_AD1_dic[key] = round(273.15 + read_value,2)
                else:
                    self.TT_AD1_dic[key] = round(read_value,2)
            # print out result
            print("ADam RTD readings output",self.TT_AD1_dic)

        else:
            print("AD1 lost connection to PLC")


    def main_function(self):
        # main body of the class-- will call the Read_AD function every 1 seconds.
        while True:
            self.Read_AD()
            time.sleep(1)





# then this is the main function for the script. We need to call the class
if __name__ == '__main__':
    # call the class and it will run the init function
    PLC = PLC()


