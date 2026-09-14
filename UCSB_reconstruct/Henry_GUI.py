"""
This is the main SlowDAQ code used to read/setproperties of the TPLC and PPLC

By: Mathieu Laurin

v0.1.0 Initial code 29/11/19 ML
v0.1.1 Read and write implemented 08/12/19 ML
v0.1.2 Alarm implemented 07/01/20 ML
v0.1.3 PLC online detection, poll PLCs only when values are updated, fix Centos window size bug 04/03/20 ML
"""

import os, sys, time, platform, datetime, random, pickle, cgitb, traceback, signal,copy, json, socket, threading, struct


from PySide2 import QtWidgets, QtCore, QtGui

# from SlowDAQ_SBC_v2 import *

from Henry_GUI_Widgets import *
from Henry_watchdog_database import remaining_T
import zmq
import Henry_env as env

VERSION = "v2.1.3"
# if platform.system() == "Linux":
#     QtGui.QFontDatabase.addApplicationFont("/usr/share/fonts/truetype/vista/calibrib.ttf")
#     SMALL_LABEL_STYLE = "background-color: rgb(204,204,204);  font-family: calibrib;" \
#                         " font-size: 10px;" \
#                         " font-weight: bold;"
#     LABEL_STYLE = "background-color: rgb(204,204,204);  font-family: calibrib; " \
#                   "font-size: 12px; "
#     TITLE_STYLE = "background-color: rgb(204,204,204);  font-family: calibrib;" \
#                   " font-size: 14px; "


# Settings adapted to sbc slowcontrol machine
SMALL_LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Calibri\";" \
                    " font-size: 10px;" \
                    " font-weight: bold;"
LABEL_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Calibri\"; " \
              "font-size: 12px; font-weight: bold;"
TITLE_STYLE = "background-color: rgb(204,204,204); border-radius: 3px; font-family: \"Calibri\";" \
              " font-size: 14px; font-weight: bold;"

BORDER_STYLE = " border-radius: 2px; border-color: black;"





ADMIN_TIMER = 30000
PLOTTING_SCALE = 0.66
ADMIN_PASSWORD = "60b6a2988e4ee1ad831ad567ad938adcc8e294825460bbcab26c1948b935bdf133e9e2c98ad4eafc622f4" \
                 "f5845cf006961abcc0a4007e3ac87d26c8981b792259f3f4db207dc14dbff315071c2f419122f1367668" \
                 "31c12bff0da3a2314ca2266"


R=0.6 # Resolution settings



sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print("ExceptType: ", exctype, "Value: ", value, "Traceback: ", traceback)
    # sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook



def sendKillSignal(etype, value, tb):
    print('KILL ALL')
    traceback.print_exception(etype, value, tb)
    os.kill(os.getpid(), signal.SIGKILL)


original_init = QtCore.QThread.__init__
def patched_init(self, *args, **kwargs):
    print("thread init'ed")
    original_init(self, *args, **kwargs)
    original_run = self.run
    def patched_run(*args, **kwargs):
        try:
            original_run(*args, **kwargs)
        except:
            sys.excepthook(*sys.exc_info())
    self.run = patched_run
QtCore.QThread.__init__ = patched_init

def install():
    sys._excepthook = sys.excepthook
    sys.excepthook = sendKillSignal
    QtCore.QThread.__init__ = patched_init
    

def TwoD_into_OneD(Twod_array):
    Oned_array = []
    i_max = len(Twod_array)
    j_max = len(Twod_array[0])
    i_last = len(Twod_array) - 1
    j_last = len(Twod_array[i_last]) - 1
    for i in range(0, i_max):
        for j in range(0, j_max):
            Oned_array.append(Twod_array[i][j])
            if (i, j) == (i_last, j_last):
                break
        if (i, j) == (i_last, j_last):
            break
    return Oned_array


# Main class
# This is designed for linux system
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.GUI_design()
        self.Alarm_system()

        App.aboutToQuit.connect(self.StopUpdater)
        # Start display updater; comment out to show GUI only
        print("start updater...")
        self.StartUpdater()
        self.signal_connection()

    def GUI_design(self):
        # Get background image path
        # Get background image path
        if '__file__' in globals():
            self.Path = os.path.dirname(os.path.realpath(__file__))
        else:
            self.Path = os.getcwd()
        self.ImagePath = os.path.join(self.Path, "image")
        # print(self.ImagePath)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.resize(2400 * R, 1400 * R)  # Open at center using resized
        self.setMinimumSize(2400 * R, 1400 * R)
        self.setWindowTitle("SlowDAQ " + VERSION)
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.ImagePath, "ucsb_phy.jpg")))

        # Tabs, backgrounds & labels

        self.Tab = QtWidgets.QTabWidget(self)
        self.Tab.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Tab.setStyleSheet("font-weight: bold; font-size: 20px; font-family: Times;")
        self.Tab.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.Tab.setGeometry(QtCore.QRect(0 * R, 0 * R, 2400 * R, 1400 * R))

        self.ThermosyphonTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.ThermosyphonTab, "Thermosyphon Main Panel")

        self.ThermosyphonTab.Background = QtWidgets.QLabel(self.ThermosyphonTab)
        self.ThermosyphonTab.Background.setScaledContents(True)
        self.ThermosyphonTab.Background.setStyleSheet('background-color:black;')
        pixmap_thermalsyphon = QtGui.QPixmap(os.path.join(self.ImagePath, "henry_ts_panel_Jul28.png"))
        pixmap_thermalsyphon = pixmap_thermalsyphon.scaledToWidth(2400 * R)
        self.ThermosyphonTab.Background.setPixmap(QtGui.QPixmap(pixmap_thermalsyphon))
        self.ThermosyphonTab.Background.move(0 * R, 0 * R)
        self.ThermosyphonTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.GasTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.GasTab, "Gas Panel")

        self.GasTab.Background = QtWidgets.QLabel(self.GasTab)
        self.GasTab.Background.setScaledContents(True)
        self.GasTab.Background.setStyleSheet('background-color:black;')
        pixmap_gas = QtGui.QPixmap(os.path.join(self.ImagePath, "henry_gas_panel.png"))
        pixmap_gas = pixmap_gas.scaledToWidth(2400 * R)
        self.GasTab.Background.setPixmap(QtGui.QPixmap(pixmap_gas))
        self.GasTab.Background.move(0 * R, 0 * R)
        self.GasTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.TubeTab = QtWidgets.QTabWidget(self.Tab)
        self.Tab.addTab(self.TubeTab, "Inner Tube")

        self.TubeTab.Background = QtWidgets.QLabel(self.TubeTab)
        self.TubeTab.Background.setScaledContents(True)
        self.TubeTab.Background.setStyleSheet('background-color:black;')
        pixmap_tube = QtGui.QPixmap(os.path.join(self.ImagePath, "henry_tube_Jun2.png"))
        pixmap_tube = pixmap_tube.scaledToWidth(2400 * R)
        self.TubeTab.Background.setPixmap(QtGui.QPixmap(pixmap_tube))
        self.TubeTab.Background.move(0 * R, 0 * R)
        self.TubeTab.Background.setAlignment(QtCore.Qt.AlignCenter)

        self.Xe_RecTab = QtWidgets.QWidget(self.Tab)
        self.Tab.addTab(self.Xe_RecTab, "Xe Rec")

        self.Xe_RecTab.Background = QtWidgets.QLabel(self.Xe_RecTab)
        self.Xe_RecTab.Background.setScaledContents(True)
        self.Xe_RecTab.Background.setStyleSheet('background-color:black;')
        pixmap_DatanSignal = QtGui.QPixmap(os.path.join(self.ImagePath, "Xenon_Rec.png"))
        pixmap_DatanSignal = pixmap_DatanSignal.scaledToWidth(2400 * R)
        self.Xe_RecTab.Background.setPixmap(QtGui.QPixmap(pixmap_DatanSignal))
        self.Xe_RecTab.Background.move(0 * R, 0 * R)
        self.Xe_RecTab.Background.setAlignment(QtCore.Qt.AlignCenter)
        self.Xe_RecTab.Background.setObjectName("DatanSignalBkg")

        self.DatanSignalTab = QtWidgets.QWidget(self.Tab)
        self.Tab.addTab(self.DatanSignalTab, "Data and Signal Panel")

        self.DatanSignalTab.Background = QtWidgets.QLabel(self.DatanSignalTab)
        self.DatanSignalTab.Background.setScaledContents(True)
        self.DatanSignalTab.Background.setStyleSheet('background-color:black;')
        pixmap_DatanSignal = QtGui.QPixmap(os.path.join(self.ImagePath, "Default_Background"))
        pixmap_DatanSignal = pixmap_DatanSignal.scaledToWidth(2400 * R)
        self.DatanSignalTab.Background.setPixmap(QtGui.QPixmap(pixmap_DatanSignal))
        self.DatanSignalTab.Background.move(0 * R, 0 * R)
        self.DatanSignalTab.Background.setAlignment(QtCore.Qt.AlignCenter)
        self.DatanSignalTab.Background.setObjectName("DatanSignalBkg")

        # Data saving and recovery
        # Data setting form is ended with .ini and directory is https://doc.qt.io/archives/qtforpython-5.12/PySide2/QtCore/QSettings.html depending on the System
        self.settings = QtCore.QSettings("$HOME/.config//SBC/SlowControl.ini", QtCore.QSettings.IniFormat)

        # Temperature tab buttons

        # Data and Signal Tab
        self.ReadSettings = Loadfile(self.DatanSignalTab)
        self.ReadSettings.move(50 * R, 50 * R)

        self.SaveSettings = CustomSave(self.DatanSignalTab)
        self.SaveSettings.move(700 * R, 50 * R)
        # self.SaveSettings.SaveFileButton.clicked.connect(
        #     lambda x: self.Save(directory=self.SaveSettings.Head, project=self.SaveSettings.Tail))


        # Thermosyphon Widgets
        self.PV1001 = Valve_v2(self.ThermosyphonTab)
        self.PV1001.Label.setText("PV1001")
        self.PV1001.move(1035 * R, 165 * R)

        self.PV1002 = Valve_v2(self.ThermosyphonTab)
        self.PV1002.Label.setText("PV1002")
        self.PV1002.move(1950 * R, 940 * R)

        self.PV1003 = Valve_v2(self.ThermosyphonTab)
        self.PV1003.Label.setText("PV1003")
        self.PV1003.move(1950 * R, 1150 * R)

        self.PV1004 = Valve_v2(self.ThermosyphonTab)
        self.PV1004.Label.setText("PV1004")
        self.PV1004.move(1700 * R, 1100 * R)

        # self.PV1005 = Valve_v2(self.ThermosyphonTab)
        # self.PV1005.Label.setText("PV1005")
        # self.PV1005.move(1450 * R, 585 * R)

        self.PV1006 = Valve_v2(self.ThermosyphonTab)
        self.PV1006.Label.setText("PV1006")
        self.PV1006.move(1065 * R, 940 * R)

        # self.PV1007 = Valve_v2(self.ThermosyphonTab)
        # self.PV1007.Label.setText("PV1007")
        # self.PV1007.move(1065 * R, 1150 * R)

        self.MFC1008 = LOOPPID_v2(self.ThermosyphonTab)
        self.MFC1008.move(1795 * R, 700 * R)
        self.MFC1008.Label.setText("MFC1008")
        self.MFC1008.LOOPPIDWindow.setWindowTitle("MFC1008")
        self.MFC1008.LOOPPIDWindow.Label.setText("MFC1008")

        self.PT1000 = PressureIndicator(self.ThermosyphonTab)
        self.PT1000.Label.setText("PT1000")
        self.PT1000.move(145 * R, 30 * R)
        self.PT1000.SetUnit(" psia")

        self.PT1001 = PressureIndicator(self.ThermosyphonTab)
        self.PT1001.Label.setText("PT1001")
        self.PT1001.move(155 * R, 975 * R)
        self.PT1001.SetUnit(" psia")

        self.PT1002 = PressureIndicator(self.ThermosyphonTab)
        self.PT1002.Label.setText("PT1002")
        self.PT1002.move(160 * R, 1160 * R)
        self.PT1002.SetUnit(" psia")



        # Gas Panel Widgets

        # self.PNV001 = Valve(self.GasTab)
        # self.PNV001.Label.setText("PNV001")
        # self.PNV001.move(470 * R, 750 * R)

        self.BGA01 = PressureIndicator(self.GasTab)
        self.BGA01.Label.setText("BGA_BI01")
        self.BGA01.move(1233 * R, 325 * R)
        self.BGA01.SetUnit(" %")

        self.BGA02 = PressureIndicator(self.GasTab)
        self.BGA02.Label.setText("BGA_BI02")
        self.BGA02.move(1642 * R, 325 * R)
        self.BGA02.SetUnit(" %")

        self.BGAP01 = PressureIndicator(self.GasTab)
        self.BGAP01.Label.setText("BGA_PU01")
        self.BGAP01.move(1410 * R, 325 * R)
        self.BGAP01.SetUnit(" %")

        self.BGAP02 = PressureIndicator(self.GasTab)
        self.BGAP02.Label.setText("BGA_PU02")
        self.BGAP02.move(1820 * R, 325 * R)
        self.BGAP02.SetUnit(" %")

        self.PT001 = PressureIndicator(self.GasTab)
        self.PT001.Label.setText("PT001")
        self.PT001.move(187 * R, 560 * R)
        self.PT001.SetUnit(" psia")

        self.PT002 = PressureIndicator(self.GasTab)
        self.PT002.Label.setText("PT002")
        self.PT002.move(1070 * R, 440 * R)
        self.PT002.SetUnit(" psia")

        self.PT003 = PressureIndicator(self.GasTab)
        self.PT003.Label.setText("PT003")
        self.PT003.move(992 * R, 740 * R)
        self.PT003.SetUnit(" psia")

        self.PT004 = PressureIndicator(self.GasTab)
        self.PT004.Label.setText("PT004")
        self.PT004.move(1452 * R, 440 * R)
        self.PT004.SetUnit(" psia")

        self.PT0 = PressureIndicator(self.TubeTab)
        self.PT0.Label.setText("PT0")
        self.PT0.move(669 * R, 590 * R)
        self.PT0.SetUnit(" psia")

        self.PV12 = Valve_v2(self.GasTab)
        self.PV12.Label.setText("PV12")
        self.PV12.move(1840 * R, 1185 * R)

        self.PV11 = Valve_v2(self.GasTab)
        self.PV11.Label.setText("PV11")
        self.PV11.move(2200 * R, 1108 * R)        

        self.PV10 = Valve_v2(self.GasTab)
        self.PV10.Label.setText("PV10")
        self.PV10.move(1840 * R, 1031 * R)

        self.PV9 = Valve_v2(self.GasTab)
        self.PV9.Label.setText("PV9")
        self.PV9.move(2200 * R, 954 * R)

        self.PV8 = Valve_v2(self.GasTab)
        self.PV8.Label.setText("PV8")
        self.PV8.move(1840 * R, 877 * R)

        self.PV7 = Valve_v2(self.GasTab)
        self.PV7.Label.setText("PV7")
        self.PV7.move(2200 * R, 800 * R)

        self.PV6 = Valve_v2(self.GasTab)
        self.PV6.Label.setText("PV6")
        self.PV6.move(1840 * R, 723 * R)

        self.PV5 = Valve_v2(self.GasTab)
        self.PV5.Label.setText("PV5")
        self.PV5.move(2200 * R, 646 * R)

        self.PV4 = Valve_v2(self.GasTab)
        self.PV4.Label.setText("PV4")
        self.PV4.move(1840 * R, 569 * R)

        self.PV3 = Valve_v2(self.GasTab)
        self.PV3.Label.setText("PV3")
        self.PV3.move(2200 * R, 492 * R)

        self.PV2 = Valve_v2(self.GasTab)
        self.PV2.Label.setText("PV2")
        self.PV2.move(1840 * R, 415 * R)

        self.PV1 = Valve_v2(self.GasTab)
        self.PV1.Label.setText("PV1")
        self.PV1.move(895 * R, 960 * R)








        self.MFC1 = LOOPPID_v2(self.GasTab)
        self.MFC1.move(1110 * R, 540 * R)
        self.MFC1.Label.setText("MFC1_cc")
        self.MFC1.Power.Label.setText("Output")
        self.MFC1.LOOPPIDWindow.setWindowTitle("MFC1")
        self.MFC1.LOOPPIDWindow.Label.setText("MFC1")

        self.MFC2 = LOOPPID_v2(self.GasTab)
        self.MFC2.move(1475 * R, 540 * R)
        self.MFC2.Label.setText("MFC2_cc")
        self.MFC2.Power.Label.setText("Output")
        self.MFC2.LOOPPIDWindow.setWindowTitle("MFC2")
        self.MFC2.LOOPPIDWindow.Label.setText("MFC2")

        # inner tube widgets
        self.RTD1 = Indicator(self.TubeTab)
        self.RTD1.Label.setText("RTD1")
        self.RTD1.move(560 * R, 280 * R)

        self.RTD2 = Indicator(self.TubeTab)
        self.RTD2.Label.setText("RTD2")
        self.RTD2.move(560 * R, 370 * R)
        
        self.RTD3 = Indicator(self.TubeTab)
        self.RTD3.Label.setText("RTD3")
        self.RTD3.move(465 * R, 1110 * R)

        self.RTD4 = Indicator(self.TubeTab)
        self.RTD4.Label.setText("RTD4")
        self.RTD4.move(394 * R, 875 * R)

        self.RTD5 = Indicator(self.TubeTab)
        self.RTD5.Label.setText("RTD5")
        self.RTD5.move(995 * R, 695 * R)

        self.RTD6 = Indicator(self.TubeTab)
        self.RTD6.Label.setText("RTD6")
        self.RTD6.move(720 * R, 1111 * R)

        self.RTD7 = Indicator(self.TubeTab)
        self.RTD7.Label.setText("RTD7")
        self.RTD7.move(529 * R, 849 * R)

        self.RTD8 = Indicator(self.TubeTab)
        self.RTD8.Label.setText("RTD8")
        self.RTD8.move(394 * R, 990 * R)

        self.RTD9 = Indicator(self.TubeTab)
        self.RTD9.Label.setText("RTD9")
        self.RTD9.move(394 * R, 590 * R)

        self.RTD10 = Indicator(self.TubeTab)
        self.RTD10.Label.setText("RTD10")
        self.RTD10.move(529 * R, 650 * R)

        self.RTD11 = Indicator(self.TubeTab)
        self.RTD11.Label.setText("RTD11")
        self.RTD11.move(394 * R, 695 * R)

        self.RTD12 = Indicator(self.TubeTab)
        self.RTD12.Label.setText("RTD12")
        self.RTD12.move(529 * R, 755 * R)

        self.RTD13 = Indicator(self.TubeTab)
        self.RTD13.Label.setText("RTD13")
        self.RTD13.move(394 * R, 795 * R)

        self.RTD14 = Indicator(self.TubeTab)
        self.RTD14.Label.setText("RTD14")
        self.RTD14.move(995 * R, 775 * R)

        # Removing LiqLev indicator for now
        # self.LiqLev = Indicator(self.TubeTab)
        # self.LiqLev.Label.setText("Liq Lev")
        # self.LiqLev.move(50 * R, 300 * R)
        # self.LiqLev.SetUnit(' "')

        self.HTR1001 = LOOPPID_v2(self.TubeTab)
        self.HTR1001.move(1440 * R, 30 * R)
        self.HTR1001.Label.setText("Heater1")
        self.HTR1001.LOOPPIDWindow.setWindowTitle("Heater1")
        self.HTR1001.LOOPPIDWindow.Label.setText("Heater1")

        self.HTR1002 = LOOPPID_v2(self.TubeTab)
        self.HTR1002.move(1440 * R, 130 * R)
        self.HTR1002.Label.setText("Heater2")
        self.HTR1002.LOOPPIDWindow.setWindowTitle("Heater2")
        self.HTR1002.LOOPPIDWindow.Label.setText("Heater2")

        self.HTR1003 = LOOPPID_v2(self.TubeTab)
        self.HTR1003.move(1440 * R, 230 * R)
        self.HTR1003.Label.setText("Heater3")
        self.HTR1003.LOOPPIDWindow.setWindowTitle("Heater3")
        self.HTR1003.LOOPPIDWindow.Label.setText("Heater3")

        self.HTR1004 = LOOPPID_v2(self.TubeTab)
        self.HTR1004.move(1440 * R, 330 * R)
        self.HTR1004.Label.setText("Heater4")
        self.HTR1004.LOOPPIDWindow.setWindowTitle("Heater4")
        self.HTR1004.LOOPPIDWindow.Label.setText("Heater4")

        self.HTR1005 = LOOPPID_v2(self.TubeTab)
        self.HTR1005.move(1440 * R, 410 * R)
        self.HTR1005.Label.setText("Heater5")
        self.HTR1005.LOOPPIDWindow.setWindowTitle("Heater5")
        self.HTR1005.LOOPPIDWindow.Label.setText("Heater5")

        self.IDHTR1001 = PnID_Alone(self.TubeTab)
        self.IDHTR1001.Label.setText("Heater 1")
        self.IDHTR1001.move(449 * R, 294 * R)

        self.IDHTR1002 = PnID_Alone(self.TubeTab)
        self.IDHTR1002.Label.setText("Heater 2")
        self.IDHTR1002.move(449 * R, 387 * R)

        self.IDHTR1003 = PnID_Alone(self.TubeTab)
        self.IDHTR1003.Label.setText("Heater 3")
        self.IDHTR1003.move(895 * R, 778 * R)

        self.IDHTR1004 = PnID_Alone(self.TubeTab)
        self.IDHTR1004.Label.setText("Heater 4")
        self.IDHTR1004.move(614 * R, 1122 * R)

        self.IDHTR1005 = PnID_Alone(self.TubeTab)
        self.IDHTR1005.Label.setText("Heater 5")
        self.IDHTR1005.move(1440 * R, 700 * R)

        self.PV1_XR = Valve_v2(self.Xe_RecTab)
        self.PV1_XR.Label.setText("PV1")
        self.PV1_XR.move(1750 * R, 500 * R)

        self.PV1_RST = RST_button(self.Xe_RecTab)
        self.PV1_RST.button.setText("PV1_RST")
        self.PV1_RST.move(1920 * R, 500 * R)

        self.PT_SET = IndicatorSetWidget(self.Xe_RecTab)
        self.PT_SET.move(1880 * R, 100 * R)
        self.PT_SET.Label.setText("PT003")
        self.PT_SET.Read.SetUnit(" psia")
        self.PT_SET.Stpoint.SetUnit(" psia")

        self.SV0001 = Valve_v2(self.Xe_RecTab)
        self.SV0001.Label.setText("SV0001")
        self.SV0001.move(760 * R, 450 * R)

        self.PT003_XR = PressureIndicator(self.Xe_RecTab)
        self.PT003_XR.Label.setText("PT003")
        self.PT003_XR.move(1900 * R, 400 * R)
        self.PT003_XR.SetUnit(" psia")

        self.TT0001 = Indicator(self.Xe_RecTab)
        self.TT0001.Label.setText("TT0001")
        self.TT0001.move(900 * R, 900 * R)

        self.TT0002 = Indicator(self.Xe_RecTab)
        self.TT0002.Label.setText("TT0002")
        self.TT0002.move(900 * R, 700 * R)

        self.SV_MAN = SV_CTRL(self.Xe_RecTab)
        self.SV_MAN.move(700*R, 180*R )

    def Alarm_system(self):
        # Alarm button
        self.AlarmWindow = AlarmWin()
        self.AlarmButton = AlarmButton(self.AlarmWindow, self)
        self.AlarmButton.SubWindow.resize(1000*R, 500*R)

        # self.AlarmButton.StatusWindow.AlarmWindow()

        self.AlarmButton.move(2300*R, 100*R)
        # self.AlarmButton.move(10 * R, 1200 * R)
        # self.AlarmButton.Button.setText("Alarm Button")


        #commands stack
        self.address =env.merge_dic(sec.TT_AD1_ADDRESS, sec.TT_AD2_ADDRESS, sec.PT_ADDRESS, sec.LEFT_REAL_ADDRESS,
                                     sec.VALVE_ADDRESS, sec.LOOPPID_ADR_BASE, sec.PROCEDURE_ADDRESS,
                                     sec.INTLK_A_ADDRESS,sec.LL_ADDRESS, sec.HTRTD_ADDRESS, sec.DIN_ADDRESS)
        self.commands = {}
        self.command_buffer_waiting= 1
        # self.statustransition={}

        self.Valve_buffer = copy.copy(env.VALVE_OUT)
        self.CHECKED = False

        self.LOOPPID_EN_buffer = copy.copy(sec.LOOPPID_EN)

        self.RTDAlarmMatrix = [self.AlarmButton.SubWindow.RTD9, self.AlarmButton.SubWindow.RTD10,
                               self.AlarmButton.SubWindow.RTD11, self.AlarmButton.SubWindow.RTD12,
                               self.AlarmButton.SubWindow.RTD13,self.AlarmButton.SubWindow.RTD14]
        #
        self.HTROUTAlarmMatrix = [self.AlarmButton.SubWindow.HTR1001, self.AlarmButton.SubWindow.HTR1002,
                                  self.AlarmButton.SubWindow.HTR1003,
                                  self.AlarmButton.SubWindow.HTR1004, self.AlarmButton.SubWindow.HTR1005]

        self.HTRRTDAlarmMatrix = [self.AlarmButton.SubWindow.RTD1, self.AlarmButton.SubWindow.RTD2,
                                  self.AlarmButton.SubWindow.RTD3, self.AlarmButton.SubWindow.RTD4,
                                  self.AlarmButton.SubWindow.RTD5, self.AlarmButton.SubWindow.RTD6,
                                  self.AlarmButton.SubWindow.RTD7, self.AlarmButton.SubWindow.RTD8, 
                                  ]

        self.PTAlarmMatrix = [self.AlarmButton.SubWindow.PT1000, self.AlarmButton.SubWindow.PT1001,
                               self.AlarmButton.SubWindow.PT1002,
                              self.AlarmButton.SubWindow.PT001,
                              self.AlarmButton.SubWindow.PT002,
                              self.AlarmButton.SubWindow.PT003, self.AlarmButton.SubWindow.PT004,self.AlarmButton.SubWindow.PT0]

        self.LEFTVariableMatrix = [self.AlarmButton.SubWindow.LL]



        self.AlarmMatrix = self.RTDAlarmMatrix + self.HTROUTAlarmMatrix + self.HTRRTDAlarmMatrix  + self.PTAlarmMatrix + self.LEFTVariableMatrix



    def StartUpdater(self):
        self.command_lock = threading.Lock()
        # install()
        self.clientthread = UpdateClient(commands=self.commands, command_lock=self.command_lock)
        # when new data comes, update the display
        self.clientthread.client_data_transport.connect(self.updatedisplay)
        self.clientthread.start()

   # Stop all updater threads
    @QtCore.Slot()
    def StopUpdater(self):
        self.clientthread.join()


    # signal connections to write settings to PLC codes

    def signal_connection(self):

        # Data signal saving and writing
        self.SaveSettings.SaveFileButton.clicked.connect(
            lambda: self.SaveSettings.SavecsvConfig(self.UpClient.receive_dic))
        # self.ReadSettings.LoadFileButton.clicked.connect(lambda : self.updatedisplay(self.ReadSettings.loaded_dict))
        self.ReadSettings.LoadFileButton.clicked.connect(lambda: self.man_set(self.ReadSettings.default_dict))
        self.ReadSettings.LoadFileButton.clicked.connect(lambda: self.man_activated(self.ReadSettings.default_dict))

        self.PV1001.Set.LButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1001.Label.text()))
        self.PV1001.Set.RButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1001.Label.text()))
        self.PV1002.Set.LButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1002.Label.text()))
        self.PV1002.Set.RButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1002.Label.text()))
        self.PV1003.Set.LButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1003.Label.text()))
        self.PV1003.Set.RButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1003.Label.text()))
        self.PV1004.Set.LButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1004.Label.text()))
        self.PV1004.Set.RButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1004.Label.text()))
        # self.PV1005.Set.LButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1005.Label.text()))
        # self.PV1005.Set.RButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1005.Label.text()))
        self.PV1006.Set.LButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1006.Label.text()))
        self.PV1006.Set.RButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1006.Label.text()))
        # self.PV1007.Set.LButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1007.Label.text()))
        # self.PV1007.Set.RButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1007.Label.text()))

        #PV1 is NO so the logic can be different
        self.PV1.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1.Label.text()))
        self.PV1.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1.Label.text()))
        self.PV1_XR.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV1.Label.text()))
        self.PV1_XR.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV1.Label.text()))

        self.PV2.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV2.Label.text()))
        self.PV2.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV2.Label.text()))
        self.PV3.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV3.Label.text()))
        self.PV3.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV3.Label.text()))
        self.PV4.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV4.Label.text()))
        self.PV4.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV4.Label.text()))
        self.PV5.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV5.Label.text()))
        self.PV5.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV5.Label.text()))
        self.PV6.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV6.Label.text()))
        self.PV6.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV6.Label.text()))
        self.PV7.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV7.Label.text()))
        self.PV7.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV7.Label.text()))
        self.PV8.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV8.Label.text()))
        self.PV8.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV8.Label.text()))
        self.PV9.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV9.Label.text()))
        self.PV9.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV9.Label.text()))
        self.PV10.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV10.Label.text()))
        self.PV10.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV10.Label.text()))
        self.PV11.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV11.Label.text()))
        self.PV11.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV11.Label.text()))
        self.PV12.Set.LButton.clicked.connect(lambda x: self.LButtonClicked(self.PV12.Label.text()))
        self.PV12.Set.RButton.clicked.connect(lambda x: self.RButtonClicked(self.PV12.Label.text()))
        # SV is inversed logic
        # SV0001 the state in the background reading out is right somehow but the input command i.e. OPEN and CLOSE
        # are reversed
        self.SV0001.Set.LButton.clicked.connect(lambda x: self.RButtonClicked(self.SV0001.Label.text()))
        self.SV0001.Set.RButton.clicked.connect(lambda x: self.LButtonClicked(self.SV0001.Label.text()))

        self.SV_MAN.MAN.clicked.connect(lambda: self.TRIGUpdate(pid="SV0001_TRIG", Act="MAN"))
        self.SV_MAN.RST.clicked.connect(lambda: self.TRIGUpdate(pid="SV0001_RESET", Act="RESET"))
        self.PV1_RST.emitter.confirmed.connect(lambda: self.TRIGUpdate(pid="PV1_RESET", Act="RESET"))

        self.AlarmButton.SubWindow.PT1000.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1000.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT1000.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT1000.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT1000.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT1001.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1001.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT1001.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT1001.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT1001.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT1002.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1002.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT1002.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT1002.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT1002.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT0.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT0.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT0.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT0.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT0.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT001.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT001.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT001.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT001.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT001.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT002.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT002.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT002.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT002.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT002.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT003.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT003.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT003.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT003.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT003.High_Set.Field.text()))

        self.AlarmButton.SubWindow.PT004.updatebutton.clicked.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT004.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT004.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT004.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT004.High_Set.Field.text()))


        self.AlarmButton.SubWindow.RTD9.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD9.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD9.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD9.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD9.High_Set.Field.text()))

        self.AlarmButton.SubWindow.RTD10.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD10.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD10.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD10.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD10.High_Set.Field.text()))
        
        self.AlarmButton.SubWindow.RTD11.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD11.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD11.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD11.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD11.High_Set.Field.text()))
        
        self.AlarmButton.SubWindow.RTD12.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD12.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD12.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD12.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD12.High_Set.Field.text()))
        
        self.AlarmButton.SubWindow.RTD13.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD13.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD13.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD13.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD13.High_Set.Field.text()))
        
        self.AlarmButton.SubWindow.RTD14.updatebutton.clicked.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD14.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD14.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD14.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD14.High_Set.Field.text()))

        self.AlarmButton.SubWindow.HTR1001.updatebutton.clicked.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1001.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1001.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1001.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1001.High_Set.Field.text()))

        self.AlarmButton.SubWindow.HTR1002.updatebutton.clicked.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1002.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1002.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1002.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1002.High_Set.Field.text()))
        self.AlarmButton.SubWindow.HTR1003.updatebutton.clicked.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1003.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1003.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1003.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1003.High_Set.Field.text()))
        self.AlarmButton.SubWindow.HTR1005.updatebutton.clicked.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1005.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1005.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1005.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1005.High_Set.Field.text()))

        self.AlarmButton.SubWindow.HTR1004.updatebutton.clicked.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1004.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1004.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1004.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1004.High_Set.Field.text()))

        self.AlarmButton.SubWindow.RTD1.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD1.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD1.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD1.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD1.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD2.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD2.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD2.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD2.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD2.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD3.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD3.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD3.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD3.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD3.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD4.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD4.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD4.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD4.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD4.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD5.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD5.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD5.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD5.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD5.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD6.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD6.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD6.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD6.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD6.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD7.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD7.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD7.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD7.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD7.High_Set.Field.text()))
        self.AlarmButton.SubWindow.RTD8.updatebutton.clicked.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD8.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD8.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD8.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD8.High_Set.Field.text()))
        

        self.AlarmButton.SubWindow.LL.updatebutton.clicked.connect(
            lambda: self.LLBoxUpdate(pid=self.AlarmButton.SubWindow.LL.Label.text(),
                                     Act=self.AlarmButton.SubWindow.LL.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.LL.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.LL.High_Set.Field.text()))

        self.PT_SET.updatebutton.clicked.connect(
            lambda: self.PTSETUpdate(pid="PT003ST",
                                     Act="SET_THRESHOLD",
                                     LowLimit=0,
                                     HighLimit=self.PT_SET.Set.Field.text()))

        # check box state change
        self.AlarmButton.SubWindow.PT1000.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1000.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT1000.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT1000.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT1000.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.PT1001.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1001.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT1001.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT1001.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT1001.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.PT1002.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT1002.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT1002.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT1002.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT1002.High_Set.Field.text(), update=False))
        self.AlarmButton.SubWindow.PT0.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT0.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT0.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT0.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT0.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.PT001.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT001.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT001.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT001.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT001.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.PT002.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT002.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT002.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT002.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT002.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.PT003.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT003.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT003.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT003.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT003.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.PT004.AlarmMode.stateChanged.connect(
            lambda: self.PTBoxUpdate(pid=self.AlarmButton.SubWindow.PT004.Label.text(),
                                     Act=self.AlarmButton.SubWindow.PT004.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.PT004.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.PT004.High_Set.Field.text(), update=False))

        
        self.AlarmButton.SubWindow.RTD9.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD9.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD9.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD9.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD9.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.RTD10.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD10.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD10.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD10.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD10.High_Set.Field.text(), update=False))
        
        self.AlarmButton.SubWindow.RTD11.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD11.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD11.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD11.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD11.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.RTD12.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD12.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD12.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD12.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD12.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.RTD13.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD13.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD13.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD13.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD13.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.RTD14.AlarmMode.stateChanged.connect(
            lambda: self.AD1TTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD14.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD14.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD14.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD14.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.HTR1001.AlarmMode.stateChanged.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1001.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1001.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1001.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1001.High_Set.Field.text(),
                                          update=False))

        self.AlarmButton.SubWindow.HTR1002.AlarmMode.stateChanged.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1002.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1002.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1002.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1002.High_Set.Field.text(),
                                          update=False))
        self.AlarmButton.SubWindow.HTR1003.AlarmMode.stateChanged.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1003.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1003.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1003.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1003.High_Set.Field.text(),
                                          update=False))
        self.AlarmButton.SubWindow.HTR1005.AlarmMode.stateChanged.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1005.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1005.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1005.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1005.High_Set.Field.text(),
                                          update=False))

        self.AlarmButton.SubWindow.HTR1004.AlarmMode.stateChanged.connect(
            lambda: self.LOOPPIDBoxUpdate(pid=self.AlarmButton.SubWindow.HTR1004.Label.text(),
                                          Act=self.AlarmButton.SubWindow.HTR1004.AlarmMode.isChecked(),
                                          LowLimit=self.AlarmButton.SubWindow.HTR1004.Low_Set.Field.text(),
                                          HighLimit=self.AlarmButton.SubWindow.HTR1004.High_Set.Field.text(),
                                          update=False))

        self.AlarmButton.SubWindow.RTD1.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD1.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD1.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD1.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD1.High_Set.Field.text(), update=False))
        self.AlarmButton.SubWindow.RTD2.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD2.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD2.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD2.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD2.High_Set.Field.text(), update=False))
        self.AlarmButton.SubWindow.RTD3.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD3.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD3.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD3.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD3.High_Set.Field.text(), update=False))
        self.AlarmButton.SubWindow.RTD4.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD4.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD4.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD4.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD4.High_Set.Field.text(), update=False))
        self.AlarmButton.SubWindow.RTD5.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD5.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD5.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD5.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD5.High_Set.Field.text(), update=False))
        self.AlarmButton.SubWindow.RTD6.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD6.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD6.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD6.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD6.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.RTD7.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD7.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD7.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD7.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD7.High_Set.Field.text(), update=False))
        
        self.AlarmButton.SubWindow.RTD8.AlarmMode.stateChanged.connect(
            lambda: self.HTRTTBoxUpdate(pid=self.AlarmButton.SubWindow.RTD8.Label.text(),
                                        Act=self.AlarmButton.SubWindow.RTD8.AlarmMode.isChecked(),
                                        LowLimit=self.AlarmButton.SubWindow.RTD8.Low_Set.Field.text(),
                                        HighLimit=self.AlarmButton.SubWindow.RTD8.High_Set.Field.text(), update=False))

        self.AlarmButton.SubWindow.LL.AlarmMode.stateChanged.connect(
            lambda: self.LLBoxUpdate(pid=self.AlarmButton.SubWindow.LL.Label.text(),
                                     Act=self.AlarmButton.SubWindow.LL.AlarmMode.isChecked(),
                                     LowLimit=self.AlarmButton.SubWindow.LL.Low_Set.Field.text(),
                                     HighLimit=self.AlarmButton.SubWindow.LL.High_Set.Field.text(), update=False))

    @QtCore.Slot()
    def LButtonClicked(self, pid):
        try:
            # if there is alread a command to send to tcp server, wait the new command until last one has been sent
            # if not self.commands[pid]:
            #     time.sleep(self.command_buffer_waiting)
            # in case cannot find the pid's address
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def RButtonClicked(self, pid):

        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "CLOSE",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked", datetime.datetime.now())
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def FLAGLButtonClicked(self, pid):
        try:
            # if there is alread a command to send to tcp server, wait the new command until last one has been sent
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            # in case cannot find the pid's address
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "FLAG", "operation": "OPEN", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def FLAGRButtonClicked(self, pid):

        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "FLAG", "operation": "CLOSE",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def SwitchLButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "switch", "operation": "ON", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def SwitchRButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "switch", "operation": "OFF",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_A_LButtonClicked(self, pid):
        try:

            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_A", "operation": "ON", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_A_RButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_A", "operation": "OFF",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_A_RESET(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_A", "operation": "RESET",
                                  "value": 1}
            print(self.commands)
            print(pid, "RESET")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_A_update(self, pid, value):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_A", "operation": "update",
                                  "value": float(value)}
            print(self.commands)
            print(pid, "update")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_D_LButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_D", "operation": "ON", "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_D_RButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_D", "operation": "OFF",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def INTLK_D_RESET(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "INTLK_D", "operation": "RESET",
                                  "value": 1}
            print(self.commands)
            print(pid, "RESET")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTLButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_power", "operation": "OPEN",
                                  "value": 1}
            # self.statustransition[pid] = {"server": "BO", "address": address, "type": "valve", "operation": "OPEN", "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTRButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_power", "operation": "CLOSE",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTSet(self, pid, value):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if value in [0, 1, 2, 3]:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT", "operation": "SETMODE",
                                      "value": value}
            else:
                print("value should be 0, 1, 2, 3")
            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTSETPOINTSet(self, pid, value1, value2):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if value1 == 1:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT",
                                      "operation": "SET1", "value": value2}
            elif value1 == 2:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT",
                                      "operation": "SET2", "value": value2}
            elif value1 == 3:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT",
                                      "operation": "SET3", "value": value2}
            else:
                print("MODE number should be in 1-3")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTGroupButtonClicked(self, pid, setN):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if setN == 0:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_setmode",
                                      "operation": "SET0", "value": True}
            elif setN == 1:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_setmode",
                                      "operation": "SET1", "value": True}
            elif setN == 2:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_setmode",
                                      "operation": "SET2", "value": True}
            elif setN == 3:
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_setmode",
                                      "operation": "SET3", "value": True}
            else:
                print("not a valid address")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOP2PTupdate(self, pid, modeN, setpoint):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if modeN == 'MODE0':
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_para",
                                      "operation": "SET0", "value": {"SETPOINT": setpoint}}
            elif modeN == 'MODE1':
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_para",
                                      "operation": "SET1", "value": {"SETPOINT": setpoint}}
            elif modeN == 'MODE2':
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_para",
                                      "operation": "SET2", "value": {"SETPOINT": setpoint}}
            elif modeN == 'MODE3':
                self.commands[pid] = {"server": "BO", "address": address, "type": "LOOP2PT_para",
                                      "operation": "SET3", "value": {"SETPOINT": setpoint}}
            else:
                print("MODE number should be in MODE0-3 and is a string")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTLButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "heater_power", "operation": "EN",
                                  "value": 1}
            print(self.commands)
            print(pid, "LButton is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTRButtonClicked(self, pid):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "heater_power", "operation": "DISEN",
                                  "value": 1}
            print(self.commands)
            print(pid, "R Button is clicked")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTSwitchSet(self, pid, value):
        try:

            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if value in [0, 1, 2, 3]:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater", "operation": "SETMODE",
                                      "value": value}
            else:
                print("value should be 0, 1, 2, 3")
            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTHISet(self, pid, value):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                  "operation": "HI_LIM", "value": value}

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTLOSet(self, pid, value):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                  "operation": "LO_LIM", "value": value}

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTSETPOINTSet(self, pid, value1, value2):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if value1 == 0:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                      "operation": "SET0", "value": value2}
            elif value1 == 1:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                      "operation": "SET1", "value": value2}
            elif value1 == 2:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                      "operation": "SET2", "value": value2}
            elif value1 == 3:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater",
                                      "operation": "SET3", "value": value2}
            else:
                print("MODE number should be in 0-3")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTRGroupButtonClicked(self, pid, setN):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if setN == 0:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_setmode",
                                      "operation": "SET0", "value": True}
            elif setN == 1:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_setmode",
                                      "operation": "SET1", "value": True}
            elif setN == 2:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_setmode",
                                      "operation": "SET2", "value": True}
            elif setN == 3:
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_setmode",
                                      "operation": "SET3", "value": True}
            else:
                print("not a valid address")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTRupdate(self, pid, modeN, setpoint, HI, LO):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            if modeN == 'MODE0':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET0", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            elif modeN == 'MODE1':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET1", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            elif modeN == 'MODE2':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET2", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            elif modeN == 'MODE3':
                self.commands[pid] = {"server": "BO", "address": address, "type": "heater_para",
                                      "operation": "SET3", "value": {"SETPOINT": setpoint, "HI_LIM": HI, "LO_LIM": LO}}
            else:
                print("MODE number should be in MODE0-3 and is a string")

            print(self.commands)
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def BOTTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def AD1TTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "AD1", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                   "LowLimit": float(
                                                                                                       LowLimit),
                                                                                                   "HighLimit": float(
                                                                                                       HighLimit),
                                                                                                   "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def AD2TTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "AD2", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                   "LowLimit": float(
                                                                                                       LowLimit),
                                                                                                   "HighLimit": float(
                                                                                                       HighLimit),
                                                                                                   "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def HTRTTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "LS", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def FPTTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "FP", "address": address, "type": "TT", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def PTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "PT", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def PTSETUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "PTSET", "operation": {"Act": Act,
                                                                                                     "LowLimit": float(
                                                                                                         LowLimit),
                                                                                                     "HighLimit": float(
                                                                                                         HighLimit),
                                                                                                     "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LEFTBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "LEFT", "operation": {"Act": Act,
                                                                                                    "LowLimit": float(
                                                                                                        LowLimit),
                                                                                                    "HighLimit": float(
                                                                                                        HighLimit),
                                                                                                    "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LLBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "LL", "address": address, "type": "LL", "operation": {"Act": Act,
                                                                                                  "LowLimit": float(
                                                                                                      LowLimit),
                                                                                                  "HighLimit": float(
                                                                                                      HighLimit),
                                                                                                  "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def DinBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "Din", "operation": {"Act": Act,
                                                                                                   "LowLimit": float(
                                                                                                       LowLimit),
                                                                                                   "HighLimit": float(
                                                                                                       HighLimit),
                                                                                                   "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def LOOPPIDBoxUpdate(self, pid, Act, LowLimit, HighLimit, update=True):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "LS", "address": address, "type": "LOOPPID_alarm", "operation": {"Act": Act,
                                                                                                             "LowLimit": float(
                                                                                                                 LowLimit),
                                                                                                             "HighLimit": float(
                                                                                                                 HighLimit),
                                                                                                             "Update": update}}
            print(pid, Act, LowLimit, HighLimit, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def ProcedureClick(self, pid, start, stop, abort):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "Procedure",
                                  "operation": {"Start": start, "Stop": stop, "Abort": abort}}
            print(pid, start, stop, abort, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def Procedure_TS_update(self, pid, RST, SEL, ADDREM_MASS, MAXTIME, update):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "Procedure_TS",
                                  "operation": {"RST_FF": RST, "SEL": SEL, "ADDREM_MASS": ADDREM_MASS,
                                                "MAXTIME": MAXTIME, "update": update}}
            print(pid, RST, SEL, ADDREM_MASS, MAXTIME, update, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def Procedure_PC_update(self, pid, start, stop, abort, ABORT_FF, FASTCOMP_FF, PCYCLE_SLOWCOMP_FF, PCYCLE_CYLEQ_FF,
                            PCYCLE_ACCHARGE_FF, PCYCLE_CYLBLEED_FF, PSET, MAXEXPTIME, MAXEQTIME, MAXEQPDIFF, MAXACCTIME,
                            MAXACCDPDT, MAXBLEEDTIME, MAXBLEEDDPDT, update):
        try:
            # if self.commands[pid] is not None:
            #     time.sleep(self.command_buffer_waiting)
            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "Procedure_PC",
                                  "operation": {"ABORT_FF": ABORT_FF, "FASTCOMP_FF": FASTCOMP_FF,
                                                "PCYCLE_SLOWCOMP_FF": PCYCLE_SLOWCOMP_FF,
                                                "PCYCLE_CYLEQ_FF": PCYCLE_CYLEQ_FF,
                                                "PCYCLE_ACCHARGE_FF": PCYCLE_ACCHARGE_FF,
                                                "PCYCLE_CYLBLEED_FF": PCYCLE_CYLBLEED_FF,
                                                "PSET": PSET, "MAXEXPTIME": MAXEXPTIME, "MAXEQTIME": MAXEQTIME,
                                                "MAXEQPDIFF": MAXEQPDIFF,
                                                "MAXACCTIME": MAXACCTIME, "MAXACCDPDT": MAXACCDPDT,
                                                "MAXBLEEDTIME": MAXBLEEDTIME, "MAXBLEEDDPDT": MAXBLEEDDPDT,
                                                "update": update}}
            print(pid, start, stop, abort, "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def TRIGUpdate(self, pid, Act):
        try:

            address = self.address[pid]
            self.commands[pid] = {"server": "BO", "address": address, "type": "TRIG", "operation": Act}
            print(pid, Act,  "ARE OK?")
        except Exception as e:
            print(e)

    @QtCore.Slot()
    def sendcommands(self):
        self.send_command_signal_MW.emit()
        print(self.commands)
        # print("signal received")

    
    def FindDistinctTrue(self, v0, v1, v2, v3):
        if v0 == True:
            if True in [v1, v2, v3]:
                print("Multiple True values")
                return "False"
            else:
                return "MODE0"
        elif v1 == True:
            if True in [v2, v3]:
                print("Multiple True values")
                return "False"
            else:
                return "MODE1"
        elif v2 == True:
            if True in [v3]:
                print("Multiple True values")
                return "False"
            else:
                return "MODE2"
        else:
            if v3:
                return "MODE3"
            else:
                print("No True Value")
                return "False"

    def FetchSetPoint(self, v0, v1, v2, v3, w0, w1, w2, w3):
        # v0-3 must corresponds to w0-3 in order
        if v0 == True:
            if True in [v1, v2, v3]:
                print("Multiple True values")
                return "False"
            else:
                return w0
        elif v1 == True:
            if True in [v2, v3]:
                print("Multiple True values")
                return "False"
            else:
                return w1
        elif v2 == True:
            if True in [v3]:
                print("Multiple True values")
                return "False"
            else:
                return w2
        else:
            if v3:
                return w3
            else:
                print("No True Value")
                return "False"

    @QtCore.Slot(object)
    def man_set(self, dic_c):
        self.commands['MAN_SET'] = dic_c
        # check the checkboxes

    @QtCore.Slot(object)
    def man_activated(self, dic_c):
        print("Acitve",dic_c["Active"])
        for element in self.RTDAlarmMatrix:
            # print(element.Label.text())
            if element.Label.text() in dic_c["Active"]["TT"]["AD1"]:
                element.AlarmMode.setChecked(bool(dic_c["Active"]["TT"]["AD1"][element.Label.text()]))
            elif element.Label.text() in dic_c["Active"]["TT"]["AD2"]:
                element.AlarmMode.setChecked(bool(dic_c["Active"]["TT"]["AD2"][element.Label.text()]))
        for element in self.HTROUTAlarmMatrix:
            # print(element.Label.text())

            element.AlarmMode.setChecked(bool(dic_c["Active"]["LOOPPID"][element.Label.text()]))
        for element in self.HTRRTDAlarmMatrix:
            element.AlarmMode.setChecked(bool(dic_c["Active"]["TT"]["LS"][element.Label.text()]))

        # for element in self.HTROUTAlarmMatrix:
        #     element.AlarmMode.setChecked(bool(dic_c["Active"]["LOOPPID"][element.Label.text()]))

        for element in self.PTAlarmMatrix:
            element.AlarmMode.setChecked(bool(dic_c["Active"]["PT"][element.Label.text()]))

        for element in self.LEFTVariableMatrix:
            element.AlarmMode.setChecked(bool(dic_c["Active"]["LL"][element.Label.text()]))


    @QtCore.Slot(object)
    def updatedisplay(self, received_dic_c):
        print("Display updating", datetime.datetime.now())
        # update the check states in initilazation
        if received_dic_c["Active"]["INI_CHECK"]==True and self.CHECKED == False:
            self.man_activated(received_dic_c)
            self.CHECKED = True

        # initialization for all check box
        self.AlarmButton.SubWindow.PT1000.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT1000"])
        self.AlarmButton.SubWindow.PT1000.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT1000"])

        self.AlarmButton.SubWindow.PT1001.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT1001"])
        self.AlarmButton.SubWindow.PT1001.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT1001"])

        self.AlarmButton.SubWindow.PT1002.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT1002"])
        self.AlarmButton.SubWindow.PT1002.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT1002"])

        self.AlarmButton.SubWindow.PT0.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT0"])
        self.AlarmButton.SubWindow.PT0.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT0"])

        self.AlarmButton.SubWindow.PT001.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT001"])
        self.AlarmButton.SubWindow.PT001.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT001"])

        self.AlarmButton.SubWindow.PT002.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT002"])
        self.AlarmButton.SubWindow.PT002.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT002"])

        self.AlarmButton.SubWindow.PT003.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT003"])
        self.AlarmButton.SubWindow.PT003.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT003"])

        self.AlarmButton.SubWindow.PT004.UpdateAlarm(received_dic_c["Alarm"]["PT"]["PT004"])
        self.AlarmButton.SubWindow.PT004.Indicator.SetValue(
            received_dic_c["data"]["PT"]["value"]["PT004"])
    
        self.AlarmButton.SubWindow.RTD9.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD9"])
        self.AlarmButton.SubWindow.RTD9.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD9"])

        self.AlarmButton.SubWindow.RTD10.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD10"])
        self.AlarmButton.SubWindow.RTD10.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD10"])
        
        self.AlarmButton.SubWindow.RTD11.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD11"])
        self.AlarmButton.SubWindow.RTD11.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD11"])

        self.AlarmButton.SubWindow.RTD12.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD12"])
        self.AlarmButton.SubWindow.RTD12.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD12"])
        
        self.AlarmButton.SubWindow.RTD13.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD13"])
        self.AlarmButton.SubWindow.RTD13.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD13"])

        self.AlarmButton.SubWindow.RTD14.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["RTD14"])
        self.AlarmButton.SubWindow.RTD14.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD14"])





        # self.AlarmButton.SubWindow.TT1007.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["TT1007"])
        # self.AlarmButton.SubWindow.TT1007.Indicator.SetValue(
        #     received_dic_c["data"]["TT"]["AD1"]["value"]["TT1007"])
        #
        # self.AlarmButton.SubWindow.TT1008.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD1"]["TT1008"])
        # self.AlarmButton.SubWindow.TT1008.Indicator.SetValue(
        #     received_dic_c["data"]["TT"]["AD1"]["value"]["TT1008"])
        #
        # self.AlarmButton.SubWindow.TT1009.UpdateAlarm(received_dic_c["Alarm"]["TT"]["AD2"]["TT1009"])
        # self.AlarmButton.SubWindow.TT1009.Indicator.SetValue(
        #     received_dic_c["data"]["TT"]["AD2"]["value"]["TT1009"])

        self.AlarmButton.SubWindow.HTR1001.UpdateAlarm(received_dic_c["Alarm"]["LOOPPID"]["HTR1001"])
        self.AlarmButton.SubWindow.HTR1001.Indicator.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1001"])

        self.AlarmButton.SubWindow.HTR1002.UpdateAlarm(received_dic_c["Alarm"]["LOOPPID"]["HTR1002"])
        self.AlarmButton.SubWindow.HTR1002.Indicator.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1002"])

        self.AlarmButton.SubWindow.HTR1003.UpdateAlarm(received_dic_c["Alarm"]["LOOPPID"]["HTR1003"])
        self.AlarmButton.SubWindow.HTR1003.Indicator.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1003"])

        self.AlarmButton.SubWindow.HTR1005.UpdateAlarm(received_dic_c["Alarm"]["LOOPPID"]["HTR1005"])
        self.AlarmButton.SubWindow.HTR1005.Indicator.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1005"])

        self.AlarmButton.SubWindow.HTR1004.UpdateAlarm(received_dic_c["Alarm"]["LOOPPID"]["HTR1004"])
        self.AlarmButton.SubWindow.HTR1004.Indicator.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1004"])

        self.AlarmButton.SubWindow.RTD1.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD1"])
        self.AlarmButton.SubWindow.RTD1.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD1"])

        self.AlarmButton.SubWindow.RTD2.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD2"])
        self.AlarmButton.SubWindow.RTD2.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD2"])

        self.AlarmButton.SubWindow.RTD3.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD3"])
        self.AlarmButton.SubWindow.RTD3.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD3"])

        self.AlarmButton.SubWindow.RTD4.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD4"])
        self.AlarmButton.SubWindow.RTD4.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD4"])

        self.AlarmButton.SubWindow.RTD5.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD5"])
        self.AlarmButton.SubWindow.RTD5.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD5"])

        self.AlarmButton.SubWindow.RTD6.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD6"])
        self.AlarmButton.SubWindow.RTD6.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD6"])

        self.AlarmButton.SubWindow.RTD7.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD7"])
        self.AlarmButton.SubWindow.RTD7.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD7"])
        
        self.AlarmButton.SubWindow.RTD8.UpdateAlarm(received_dic_c["Alarm"]["TT"]["LS"]["RTD8"])
        self.AlarmButton.SubWindow.RTD8.Indicator.SetValue(
            received_dic_c["data"]["TT"]["LS"]["value"]["RTD8"])


        self.AlarmButton.SubWindow.LL.UpdateAlarm(received_dic_c["Alarm"]["LL"]["LL"])
        self.AlarmButton.SubWindow.LL.Indicator.SetValue(
            received_dic_c["data"]["LL"]["value"]["LL"])

        self.PT1000.SetValue(received_dic_c["data"]["PT"]["value"]["PT1000"])
        self.PT1001.SetValue(received_dic_c["data"]["PT"]["value"]["PT1001"])
        self.PT1002.SetValue(received_dic_c["data"]["PT"]["value"]["PT1002"])
        self.PT0.SetValue(received_dic_c["data"]["PT"]["value"]["PT0"])

        self.PT001.SetValue(received_dic_c["data"]["PT"]["value"]["PT001"])

        self.PT002.SetValue(received_dic_c["data"]["PT"]["value"]["PT002"])

        self.PT003.SetValue(received_dic_c["data"]["PT"]["value"]["PT003"])
        self.PT003_XR.SetValue(received_dic_c["data"]["PT"]["value"]["PT003"])
        self.PT_SET.Read.SetValue(received_dic_c["data"]["PT"]["value"]["PT003"])
        self.PT_SET.Stpoint.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["PT003ST"])
        self.PT004.SetValue(received_dic_c["data"]["PT"]["value"]["PT004"])
        self.RTD1.SetValue(received_dic_c["data"]["TT"]["LS"]["value"]["RTD1"])
        self.RTD2.SetValue(received_dic_c["data"]["TT"]["LS"]["value"]["RTD2"])
        self.RTD3.SetValue(received_dic_c["data"]["TT"]["LS"]["value"]["RTD3"])
        self.RTD4.SetValue(received_dic_c["data"]["TT"]["LS"]["value"]["RTD4"])
        self.RTD5.SetValue(received_dic_c["data"]["TT"]["LS"]["value"]["RTD5"])
        self.RTD6.SetValue(received_dic_c["data"]["TT"]["LS"]["value"]["RTD6"])
        self.RTD7.SetValue(received_dic_c["data"]["TT"]["LS"]["value"]["RTD7"])
        self.RTD8.SetValue(received_dic_c["data"]["TT"]["LS"]["value"]["RTD8"])
        self.RTD9.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD9"])
        self.RTD10.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD10"])
        self.RTD11.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD11"])
        self.RTD12.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD12"])
        self.RTD13.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD13"])
        self.RTD14.SetValue(received_dic_c["data"]["TT"]["AD1"]["value"]["RTD14"])
        self.TT0001.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["TT0001"])
        self.TT0002.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["TT0002"])

        self.BGA01.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["BGAAH01"])
        self.BGAP01.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["BGAP01"])
        self.BGA02.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["BGAAH02"])
        self.BGAP02.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["BGAP02"])
        # self.LiqLev.SetValue(received_dic_c["data"]["LL"]["value"]["LL"])  <- This is not used in the GUI, so commented out
        print("Time",received_dic_c["data"]["LEFT_REAL"]["value"]["SV0001_TIME"])
        self.SV_MAN.Time.SetRawValue(remaining_T(passed=received_dic_c["data"]["LEFT_REAL"]["value"]["SV0001_TIME"]))

        #Update alarmwindow's widgets' value

        for element in self.PTAlarmMatrix:
            # print(element.Label.text())
            element.UpdateAlarm(
                received_dic_c["Alarm"]["PT"][element.Label.text()])
            element.Indicator.SetValue(
                received_dic_c["data"]["PT"]["value"][element.Label.text()])
            element.Low_Read.SetValue(
                received_dic_c["data"]["PT"]["low"][element.Label.text()])
            element.High_Read.SetValue(
                received_dic_c["data"]["PT"]["high"][element.Label.text()])

        for element in self.RTDAlarmMatrix:
            if element.Label.text() in received_dic_c["Active"]["TT"]["AD1"]:
                element.UpdateAlarm(
                    received_dic_c["Alarm"]["TT"]["AD1"][element.Label.text()])
                element.Indicator.SetValue(
                    received_dic_c["data"]["TT"]["AD1"]["value"][element.Label.text()])
                element.Low_Read.SetValue(
                    received_dic_c["data"]["TT"]["AD1"]["low"][element.Label.text()])
                element.High_Read.SetValue(
                    received_dic_c["data"]["TT"]["AD1"]["high"][element.Label.text()])
            elif element.Label.text() in received_dic_c["Active"]["TT"]["AD2"]:
                element.UpdateAlarm(
                    received_dic_c["Alarm"]["TT"]["AD2"][element.Label.text()])
                element.Indicator.SetValue(
                    received_dic_c["data"]["TT"]["AD2"]["value"][element.Label.text()])
                element.Low_Read.SetValue(
                    received_dic_c["data"]["TT"]["AD2"]["low"][element.Label.text()])
                element.High_Read.SetValue(
                    received_dic_c["data"]["TT"]["AD2"]["high"][element.Label.text()])
            # print(element.Label.text())

        for element in self.HTRRTDAlarmMatrix:
            # print(element.Label.text())
            element.UpdateAlarm(
                received_dic_c["Alarm"]["TT"]["LS"][element.Label.text()])
            element.Indicator.SetValue(
                received_dic_c["data"]["TT"]["LS"]["value"][element.Label.text()])
            element.Low_Read.SetValue(
                received_dic_c["data"]["TT"]["LS"]["low"][element.Label.text()])
            element.High_Read.SetValue(
                received_dic_c["data"]["TT"]["LS"]["high"][element.Label.text()])

        for element in self.HTROUTAlarmMatrix:
            # print(element.Label.text())
            element.UpdateAlarm(
                received_dic_c["Alarm"]["LOOPPID"][element.Label.text()])
            element.Indicator.SetValue(
                received_dic_c["data"]["LOOPPID"]["OUT"][element.Label.text()])
            element.Low_Read.SetValue(
                received_dic_c["data"]["LOOPPID"]["Alarm_LowLimit"][element.Label.text()])
            element.High_Read.SetValue(
                received_dic_c["data"]["LOOPPID"]["Alarm_HighLimit"][element.Label.text()])

        for element in self.LEFTVariableMatrix:
            # print(element.Label.text())
            element.UpdateAlarm(
                received_dic_c["Alarm"]["LL"][element.Label.text()])
            element.Indicator.SetValue(
                received_dic_c["data"]["LL"]["value"][element.Label.text()])
            element.Low_Read.SetValue(
                received_dic_c["data"]["LL"]["low"][element.Label.text()])
            element.High_Read.SetValue(
                received_dic_c["data"]["LL"]["high"][element.Label.text()])

        AlarmMatrix = []
        for element in self.AlarmMatrix:
            AlarmMatrix.append(element.Alarm)
        self.update_alarmwindow(AlarmMatrix)

        self.PV1001.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1001"])
        self.PV1002.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1002"])
        self.PV1003.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1003"])
        self.PV1004.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1004"])
        # self.PV1005.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1005"])
        self.PV1006.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1006"])
        # self.PV1007.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1007"])
        self.PV1.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1"])
        self.PV1_XR.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV1"])
        self.PV2.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV2"])
        self.PV3.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV3"])
        self.PV4.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV4"])
        self.PV5.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV5"])
        self.PV6.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV6"])
        self.PV7.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV7"])
        self.PV8.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV8"])
        self.PV9.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV9"])
        self.PV10.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV10"])
        self.PV11.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV11"])
        self.PV12.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["PV12"])
        self.SV0001.ColorLabel(received_dic_c["data"]["Valve"]["OUT"]["SV0001"])
        # show whether the widgets status are normal: manully controlled and no error signal

        if received_dic_c["data"]["Valve"]["MAN"]["PV1001"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1001"]:

            self.PV1001.ActiveState.UpdateColor(True)
        else:
            self.PV1001.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1002"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1002"]:

            self.PV1002.ActiveState.UpdateColor(True)
        else:
            self.PV1002.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1003"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1003"]:

            self.PV1003.ActiveState.UpdateColor(True)
        else:
            self.PV1003.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1004"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1004"]:

            self.PV1004.ActiveState.UpdateColor(True)
        else:
            self.PV1004.ActiveState.UpdateColor(False)

        # if received_dic_c["data"]["Valve"]["MAN"]["PV1005"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1005"]:

        #     self.PV1005.ActiveState.UpdateColor(True)
        # else:
        #     self.PV1005.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1006"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1006"]:

            self.PV1006.ActiveState.UpdateColor(True)
        else:
            self.PV1006.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1006"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1006"]:

            self.PV1006.ActiveState.UpdateColor(True)
        else:
            self.PV1006.ActiveState.UpdateColor(False)

        # if received_dic_c["data"]["Valve"]["MAN"]["PV1007"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1007"]:

        #     self.PV1007.ActiveState.UpdateColor(True)
        # else:
        #     self.PV1007.ActiveState.UpdateColor(False)

        # For PV1, the INTLCK is data/Din/PV1_LCK
        if received_dic_c["data"]["Valve"]["MAN"]["PV1"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1"] and not received_dic_c["data"]["Din"]["value"]["PV1_LCK"]:

            self.PV1.ActiveState.UpdateColor(True)
        else:
            self.PV1.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV1"] and not received_dic_c["data"]["Valve"]["ERR"]["PV1"] and not received_dic_c["data"]["Din"]["value"]["PV1_LCK"]:

            self.PV1_XR.ActiveState.UpdateColor(True)
        else:
            self.PV1_XR.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV2"] and not received_dic_c["data"]["Valve"]["ERR"]["PV2"]:

            self.PV2.ActiveState.UpdateColor(True)
        else:
            self.PV2.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV3"] and not received_dic_c["data"]["Valve"]["ERR"]["PV3"]:

            self.PV3.ActiveState.UpdateColor(True)
        else:
            self.PV3.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV4"] and not received_dic_c["data"]["Valve"]["ERR"]["PV4"]:

            self.PV4.ActiveState.UpdateColor(True)
        else:
            self.PV4.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV5"] and not received_dic_c["data"]["Valve"]["ERR"]["PV5"]:

            self.PV5.ActiveState.UpdateColor(True)
        else:
            self.PV5.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV6"] and not received_dic_c["data"]["Valve"]["ERR"]["PV6"]:

            self.PV6.ActiveState.UpdateColor(True)
        else:
            self.PV6.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV7"] and not received_dic_c["data"]["Valve"]["ERR"]["PV7"]:

            self.PV7.ActiveState.UpdateColor(True)
        else:
            self.PV7.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV8"] and not received_dic_c["data"]["Valve"]["ERR"]["PV8"]:

            self.PV8.ActiveState.UpdateColor(True)
        else:
            self.PV8.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV9"] and not received_dic_c["data"]["Valve"]["ERR"]["PV9"]:

            self.PV9.ActiveState.UpdateColor(True)
        else:
            self.PV9.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV10"] and not received_dic_c["data"]["Valve"]["ERR"]["PV10"]:

            self.PV10.ActiveState.UpdateColor(True)
        else:
            self.PV10.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV11"] and not received_dic_c["data"]["Valve"]["ERR"]["PV11"]:

            self.PV11.ActiveState.UpdateColor(True)
        else:
            self.PV11.ActiveState.UpdateColor(False)

        if received_dic_c["data"]["Valve"]["MAN"]["PV12"] and not received_dic_c["data"]["Valve"]["ERR"]["PV12"]:

            self.PV12.ActiveState.UpdateColor(True)
        else:
            self.PV12.ActiveState.UpdateColor(False)

        if (received_dic_c["data"]["Valve"]["MAN"]["SV0001"]) and (not received_dic_c["data"]["Valve"]["ERR"]["SV0001"]) and (received_dic_c["data"]["Din"]["value"]["SV0001_MAN"]):

            self.SV0001.ActiveState.UpdateColor(True)
        else:
            self.SV0001.ActiveState.UpdateColor(False)

        # print("PV1001 busy", received_dic_c["data"]["Valve"]["Busy"]["PV1001"])
        if received_dic_c["data"]["Valve"]["Busy"]["PV1001"] == True:
            self.PV1001.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1001.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1002"] == True:
            self.PV1002.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1002.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1003"] == True:
            self.PV1003.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1003.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1004"] == True:
            self.PV1004.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1004.ButtonTransitionState(False)

        # if received_dic_c["data"]["Valve"]["Busy"]["PV1005"] == True:
        #     self.PV1005.ButtonTransitionState(True)
        #     # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        # else:
        #     # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
        #     self.PV1005.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1006"] == True:
            self.PV1006.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1006.ButtonTransitionState(False)

        # if received_dic_c["data"]["Valve"]["Busy"]["PV1007"] == True:
        #     self.PV1007.ButtonTransitionState(True)
        #     # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        # else:
        #     # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
        #     self.PV1007.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1"] == True:
            self.PV1.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV1"] == True:
            self.PV1_XR.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV1_XR.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV2"] == True:
            self.PV2.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV2.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV3"] == True:
            self.PV3.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV3.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV4"] == True:
            self.PV4.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV4.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV5"] == True:
            self.PV5.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV5.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV6"] == True:
            self.PV6.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV6.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV7"] == True:
            self.PV7.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV7.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV8"] == True:
            self.PV8.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV8.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV9"] == True:
            self.PV9.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV9.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV10"] == True:
            self.PV10.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV10.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV11"] == True:
            self.PV11.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV11.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["PV12"] == True:
            self.PV12.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.PV12.ButtonTransitionState(False)

        if received_dic_c["data"]["Valve"]["Busy"]["SV0001"] == True:
            self.SV0001.ButtonTransitionState(True)
            # self.Valve_buffer["PV1344"] = received_dic_c["data"]["Valve"]["OUT"]["PV1344"]

        else:
            # if not rejected, and new value is different from the previous one(the valve status changed), then set busy back
            self.SV0001.ButtonTransitionState(False)

        if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1001"]:
            self.HTR1001.ButtonTransitionState(True)
            self.HTR1001.LOOPPIDWindow.ButtonTransitionState(True)
        elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1001"]:
            self.HTR1001.ButtonTransitionState(False)
            self.HTR1001.LOOPPIDWindow.ButtonTransitionState(False)
        else:
            pass

        if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1002"]:
            self.HTR1002.ButtonTransitionState(True)
            self.HTR1002.LOOPPIDWindow.ButtonTransitionState(True)
        elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1002"]:
            self.HTR1002.ButtonTransitionState(False)
            self.HTR1002.LOOPPIDWindow.ButtonTransitionState(False)
        else:
            pass

        if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1003"]:
            self.HTR1003.ButtonTransitionState(True)
            self.HTR1003.LOOPPIDWindow.ButtonTransitionState(True)
        elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1003"]:
            self.HTR1003.ButtonTransitionState(False)
            self.HTR1003.LOOPPIDWindow.ButtonTransitionState(False)
        else:
            pass

        if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1005"]:
            self.HTR1005.ButtonTransitionState(True)
            self.HTR1005.LOOPPIDWindow.ButtonTransitionState(True)
        elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1005"]:
            self.HTR1005.ButtonTransitionState(False)
            self.HTR1005.LOOPPIDWindow.ButtonTransitionState(False)
        else:
            pass

        if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1004"]:
            self.HTR1004.ButtonTransitionState(True)
            self.HTR1004.LOOPPIDWindow.ButtonTransitionState(True)
        elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1004"]:
            self.HTR1004.ButtonTransitionState(False)
            self.HTR1004.LOOPPIDWindow.ButtonTransitionState(False)
        else:
            pass

            # timeline
            # 1.click button and button locked -> 2.same status signal sent(try to set button status back)-> 3.PLC received the command and change the status
            # -> 4.changed status signal sent, the status is unlocked
            # how to distinguish 2 and 4 in different senarios: state change
            # busy -> whether it is locked

        if not received_dic_c["data"]["Valve"]["MAN"]["PV1"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV1"]:
                self.PV1.Set.ButtonLClicked()
                self.PV1_XR.Set.ButtonLClicked()
            else:
                self.PV1.Set.ButtonRClicked()
                self.PV1_XR.Set.ButtonRClicked()
            self.Valve_buffer["PV1"] = received_dic_c["data"]["Valve"]["OUT"]["PV1"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV1"]:
            # if manually, we need to know whether the button is locked
            # if locked (grey), then only update value after the buffer != current value
            if received_dic_c["data"]["Valve"]["Busy"]["PV1"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1"]:
                    self.PV1.Set.ButtonLClicked()
                    self.PV1_XR.Set.ButtonLClicked()
                else:
                    self.PV1.Set.ButtonRClicked()
                    self.PV1_XR.Set.ButtonRClicked()
                self.Valve_buffer["PV1"] = received_dic_c["data"]["Valve"]["OUT"]["PV1"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV1"]:

                if received_dic_c["data"]["Valve"]["OUT"]["PV1"] != self.Valve_buffer["PV1"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1"]:
                        self.PV1.Set.ButtonLClicked()
                        self.PV1_XR.Set.ButtonLClicked()
                    else:
                        self.PV1.Set.ButtonRClicked()
                        self.PV1_XR.Set.ButtonRClicked()
                    self.Valve_buffer["PV1"] = received_dic_c["data"]["Valve"]["OUT"]["PV1"]
                else:
                    pass


        if not received_dic_c["data"]["Valve"]["MAN"]["PV2"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV2"]:
                self.PV2.Set.ButtonLClicked()
            else:
                self.PV2.Set.ButtonRClicked()
            self.Valve_buffer["PV2"] = received_dic_c["data"]["Valve"]["OUT"]["PV2"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV2"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV2"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV2"]:
                    self.PV2.Set.ButtonLClicked()
                else:
                    self.PV2.Set.ButtonRClicked()
                self.Valve_buffer["PV2"] = received_dic_c["data"]["Valve"]["OUT"]["PV2"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV2"]:
                #     print("PV2", received_dic_c["data"]["Valve"]["OUT"]["PV2"] != self.Valve_buffer["PV2"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV2"])
                #     print("Buffer", self.Valve_buffer["PV2"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV2"] != self.Valve_buffer["PV2"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV2"]:
                        self.PV2.Set.ButtonLClicked()
                    else:
                        self.PV2.Set.ButtonRClicked()
                    self.Valve_buffer["PV2"] = received_dic_c["data"]["Valve"]["OUT"]["PV2"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV3"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV3"]:
                self.PV3.Set.ButtonLClicked()
            else:
                self.PV3.Set.ButtonRClicked()
            self.Valve_buffer["PV3"] = received_dic_c["data"]["Valve"]["OUT"]["PV3"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV3"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV3"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV3"]:
                    self.PV3.Set.ButtonLClicked()
                else:
                    self.PV3.Set.ButtonRClicked()
                self.Valve_buffer["PV3"] = received_dic_c["data"]["Valve"]["OUT"]["PV3"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV3"]:
                #     print("PV3", received_dic_c["data"]["Valve"]["OUT"]["PV3"] != self.Valve_buffer["PV3"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV3"])
                #     print("Buffer", self.Valve_buffer["PV3"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV3"] != self.Valve_buffer["PV3"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV3"]:
                        self.PV3.Set.ButtonLClicked()
                    else:
                        self.PV3.Set.ButtonRClicked()
                    self.Valve_buffer["PV3"] = received_dic_c["data"]["Valve"]["OUT"]["PV3"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV4"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV4"]:
                self.PV4.Set.ButtonLClicked()
            else:
                self.PV4.Set.ButtonRClicked()
            self.Valve_buffer["PV4"] = received_dic_c["data"]["Valve"]["OUT"]["PV4"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV4"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV4"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV4"]:
                    self.PV4.Set.ButtonLClicked()
                else:
                    self.PV4.Set.ButtonRClicked()
                self.Valve_buffer["PV4"] = received_dic_c["data"]["Valve"]["OUT"]["PV4"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV4"]:
                #     print("PV4", received_dic_c["data"]["Valve"]["OUT"]["PV4"] != self.Valve_buffer["PV4"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV4"])
                #     print("Buffer", self.Valve_buffer["PV4"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV4"] != self.Valve_buffer["PV4"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV4"]:
                        self.PV4.Set.ButtonLClicked()
                    else:
                        self.PV4.Set.ButtonRClicked()
                    self.Valve_buffer["PV4"] = received_dic_c["data"]["Valve"]["OUT"]["PV4"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV5"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV5"]:
                self.PV5.Set.ButtonLClicked()
            else:
                self.PV5.Set.ButtonRClicked()
            self.Valve_buffer["PV5"] = received_dic_c["data"]["Valve"]["OUT"]["PV5"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV5"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV5"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV5"]:
                    self.PV5.Set.ButtonLClicked()
                else:
                    self.PV5.Set.ButtonRClicked()
                self.Valve_buffer["PV5"] = received_dic_c["data"]["Valve"]["OUT"]["PV5"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV5"]:
                #     print("PV5", received_dic_c["data"]["Valve"]["OUT"]["PV5"] != self.Valve_buffer["PV5"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV5"])
                #     print("Buffer", self.Valve_buffer["PV5"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV5"] != self.Valve_buffer["PV5"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV5"]:
                        self.PV5.Set.ButtonLClicked()
                    else:
                        self.PV5.Set.ButtonRClicked()
                    self.Valve_buffer["PV5"] = received_dic_c["data"]["Valve"]["OUT"]["PV5"]
                else:
                    pass
        if not received_dic_c["data"]["Valve"]["MAN"]["PV6"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV6"]:
                self.PV6.Set.ButtonLClicked()
            else:
                self.PV6.Set.ButtonRClicked()
            self.Valve_buffer["PV6"] = received_dic_c["data"]["Valve"]["OUT"]["PV6"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV6"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV6"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV6"]:
                    self.PV6.Set.ButtonLClicked()
                else:
                    self.PV6.Set.ButtonRClicked()
                self.Valve_buffer["PV6"] = received_dic_c["data"]["Valve"]["OUT"]["PV6"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV6"]:
                #     print("PV6", received_dic_c["data"]["Valve"]["OUT"]["PV6"] != self.Valve_buffer["PV6"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV6"])
                #     print("Buffer", self.Valve_buffer["PV6"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV6"] != self.Valve_buffer["PV6"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV6"]:
                        self.PV6.Set.ButtonLClicked()
                    else:
                        self.PV6.Set.ButtonRClicked()
                    self.Valve_buffer["PV6"] = received_dic_c["data"]["Valve"]["OUT"]["PV6"]
                else:
                    pass
        if not received_dic_c["data"]["Valve"]["MAN"]["PV7"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV7"]:
                self.PV7.Set.ButtonLClicked()
            else:
                self.PV7.Set.ButtonRClicked()
            self.Valve_buffer["PV7"] = received_dic_c["data"]["Valve"]["OUT"]["PV7"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV7"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV7"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV7"]:
                    self.PV7.Set.ButtonLClicked()
                else:
                    self.PV7.Set.ButtonRClicked()
                self.Valve_buffer["PV7"] = received_dic_c["data"]["Valve"]["OUT"]["PV7"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV7"]:
                #     print("PV7", received_dic_c["data"]["Valve"]["OUT"]["PV7"] != self.Valve_buffer["PV7"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV7"])
                #     print("Buffer", self.Valve_buffer["PV7"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV7"] != self.Valve_buffer["PV7"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV7"]:
                        self.PV7.Set.ButtonLClicked()
                    else:
                        self.PV7.Set.ButtonRClicked()
                    self.Valve_buffer["PV7"] = received_dic_c["data"]["Valve"]["OUT"]["PV7"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV8"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV8"]:
                self.PV8.Set.ButtonLClicked()
            else:
                self.PV8.Set.ButtonRClicked()
            self.Valve_buffer["PV8"] = received_dic_c["data"]["Valve"]["OUT"]["PV8"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV8"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV8"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV8"]:
                    self.PV8.Set.ButtonLClicked()
                else:
                    self.PV8.Set.ButtonRClicked()
                self.Valve_buffer["PV8"] = received_dic_c["data"]["Valve"]["OUT"]["PV8"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV8"]:
                #     print("PV8", received_dic_c["data"]["Valve"]["OUT"]["PV8"] != self.Valve_buffer["PV8"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV8"])
                #     print("Buffer", self.Valve_buffer["PV8"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV8"] != self.Valve_buffer["PV8"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV8"]:
                        self.PV8.Set.ButtonLClicked()
                    else:
                        self.PV8.Set.ButtonRClicked()
                    self.Valve_buffer["PV8"] = received_dic_c["data"]["Valve"]["OUT"]["PV8"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV9"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV9"]:
                self.PV9.Set.ButtonLClicked()
            else:
                self.PV9.Set.ButtonRClicked()
            self.Valve_buffer["PV9"] = received_dic_c["data"]["Valve"]["OUT"]["PV9"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV9"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV9"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV9"]:
                    self.PV9.Set.ButtonLClicked()
                else:
                    self.PV9.Set.ButtonRClicked()
                self.Valve_buffer["PV9"] = received_dic_c["data"]["Valve"]["OUT"]["PV9"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV9"]:
                #     print("PV9", received_dic_c["data"]["Valve"]["OUT"]["PV9"] != self.Valve_buffer["PV9"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV9"])
                #     print("Buffer", self.Valve_buffer["PV9"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV9"] != self.Valve_buffer["PV9"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV9"]:
                        self.PV9.Set.ButtonLClicked()
                    else:
                        self.PV9.Set.ButtonRClicked()
                    self.Valve_buffer["PV9"] = received_dic_c["data"]["Valve"]["OUT"]["PV9"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV10"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV10"]:
                self.PV10.Set.ButtonLClicked()
            else:
                self.PV10.Set.ButtonRClicked()
            self.Valve_buffer["PV10"] = received_dic_c["data"]["Valve"]["OUT"]["PV10"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV10"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV10"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV10"]:
                    self.PV10.Set.ButtonLClicked()
                else:
                    self.PV10.Set.ButtonRClicked()
                self.Valve_buffer["PV10"] = received_dic_c["data"]["Valve"]["OUT"]["PV10"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV10"]:
                #     print("PV10", received_dic_c["data"]["Valve"]["OUT"]["PV10"] != self.Valve_buffer["PV10"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV10"])
                #     print("Buffer", self.Valve_buffer["PV10"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV10"] != self.Valve_buffer["PV10"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV10"]:
                        self.PV10.Set.ButtonLClicked()
                    else:
                        self.PV10.Set.ButtonRClicked()
                    self.Valve_buffer["PV10"] = received_dic_c["data"]["Valve"]["OUT"]["PV10"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV11"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV11"]:
                self.PV11.Set.ButtonLClicked()
            else:
                self.PV11.Set.ButtonRClicked()
            self.Valve_buffer["PV11"] = received_dic_c["data"]["Valve"]["OUT"]["PV11"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV11"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV11"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV11"]:
                    self.PV11.Set.ButtonLClicked()
                else:
                    self.PV11.Set.ButtonRClicked()
                self.Valve_buffer["PV11"] = received_dic_c["data"]["Valve"]["OUT"]["PV11"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV11"]:
                #     print("PV11", received_dic_c["data"]["Valve"]["OUT"]["PV11"] != self.Valve_buffer["PV11"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV11"])
                #     print("Buffer", self.Valve_buffer["PV11"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV11"] != self.Valve_buffer["PV11"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV11"]:
                        self.PV11.Set.ButtonLClicked()
                    else:
                        self.PV11.Set.ButtonRClicked()
                    self.Valve_buffer["PV11"] = received_dic_c["data"]["Valve"]["OUT"]["PV11"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV12"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV12"]:
                self.PV12.Set.ButtonLClicked()
            else:
                self.PV12.Set.ButtonRClicked()
            self.Valve_buffer["PV12"] = received_dic_c["data"]["Valve"]["OUT"]["PV12"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV12"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV12"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV12"]:
                    self.PV12.Set.ButtonLClicked()
                else:
                    self.PV12.Set.ButtonRClicked()
                self.Valve_buffer["PV12"] = received_dic_c["data"]["Valve"]["OUT"]["PV12"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV12"]:
                #     print("PV12", received_dic_c["data"]["Valve"]["OUT"]["PV12"] != self.Valve_buffer["PV12"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV12"])
                #     print("Buffer", self.Valve_buffer["PV12"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV12"] != self.Valve_buffer["PV12"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV12"]:
                        self.PV12.Set.ButtonLClicked()
                    else:
                        self.PV12.Set.ButtonRClicked()
                    self.Valve_buffer["PV12"] = received_dic_c["data"]["Valve"]["OUT"]["PV12"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["SV0001"]:
            if received_dic_c["data"]["Valve"]["OUT"]["SV0001"]:
                self.SV0001.Set.ButtonLClicked()
            else:
                self.SV0001.Set.ButtonRClicked()
            self.Valve_buffer["SV0001"] = received_dic_c["data"]["Valve"]["OUT"]["SV0001"]
        elif received_dic_c["data"]["Valve"]["MAN"]["SV0001"]:
            if received_dic_c["data"]["Valve"]["Busy"]["SV0001"]:
                if received_dic_c["data"]["Valve"]["OUT"]["SV0001"]:
                    self.SV0001.Set.ButtonLClicked()
                else:
                    self.SV0001.Set.ButtonRClicked()
                self.Valve_buffer["SV0001"] = received_dic_c["data"]["Valve"]["OUT"]["SV0001"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["SV0001"]:
                #     print("SV0001", received_dic_c["data"]["Valve"]["OUT"]["SV0001"] != self.Valve_buffer["SV0001"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["SV0001"])
                #     print("Buffer", self.Valve_buffer["SV0001"])
                if received_dic_c["data"]["Valve"]["OUT"]["SV0001"] != self.Valve_buffer["SV0001"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["SV0001"]:
                        self.SV0001.Set.ButtonLClicked()
                    else:
                        self.SV0001.Set.ButtonRClicked()
                    self.Valve_buffer["SV0001"] = received_dic_c["data"]["Valve"]["OUT"]["SV0001"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV1001"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV1001"]:
                self.PV1001.Set.ButtonLClicked()
            else:
                self.PV1001.Set.ButtonRClicked()
            self.Valve_buffer["PV1001"] = received_dic_c["data"]["Valve"]["OUT"]["PV1001"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV1001"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV1001"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1001"]:
                    self.PV1001.Set.ButtonLClicked()
                else:
                    self.PV1001.Set.ButtonRClicked()
                self.Valve_buffer["PV1001"] = received_dic_c["data"]["Valve"]["OUT"]["PV1001"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV1001"]:
                #     print("PV1001", received_dic_c["data"]["Valve"]["OUT"]["PV1001"] != self.Valve_buffer["PV1001"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1001"])
                #     print("Buffer", self.Valve_buffer["PV1001"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV1001"] != self.Valve_buffer["PV1001"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1001"]:
                        self.PV1001.Set.ButtonLClicked()
                    else:
                        self.PV1001.Set.ButtonRClicked()
                    self.Valve_buffer["PV1001"] = received_dic_c["data"]["Valve"]["OUT"]["PV1001"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV1002"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV1002"]:
                self.PV1002.Set.ButtonLClicked()
            else:
                self.PV1002.Set.ButtonRClicked()
            self.Valve_buffer["PV1002"] = received_dic_c["data"]["Valve"]["OUT"]["PV1002"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV1002"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV1002"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1002"]:
                    self.PV1002.Set.ButtonLClicked()
                else:
                    self.PV1002.Set.ButtonRClicked()
                self.Valve_buffer["PV1002"] = received_dic_c["data"]["Valve"]["OUT"]["PV1002"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV1002"]:
                #     print("PV1002", received_dic_c["data"]["Valve"]["OUT"]["PV1002"] != self.Valve_buffer["PV1002"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1002"])
                #     print("Buffer", self.Valve_buffer["PV1002"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV1002"] != self.Valve_buffer["PV1002"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1002"]:
                        self.PV1002.Set.ButtonLClicked()
                    else:
                        self.PV1002.Set.ButtonRClicked()
                    self.Valve_buffer["PV1002"] = received_dic_c["data"]["Valve"]["OUT"]["PV1002"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV1003"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV1003"]:
                self.PV1003.Set.ButtonLClicked()
            else:
                self.PV1003.Set.ButtonRClicked()
            self.Valve_buffer["PV1003"] = received_dic_c["data"]["Valve"]["OUT"]["PV1003"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV1003"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV1003"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1003"]:
                    self.PV1003.Set.ButtonLClicked()
                else:
                    self.PV1003.Set.ButtonRClicked()
                self.Valve_buffer["PV1003"] = received_dic_c["data"]["Valve"]["OUT"]["PV1003"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV1003"]:
                #     print("PV1003", received_dic_c["data"]["Valve"]["OUT"]["PV1003"] != self.Valve_buffer["PV1003"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1003"])
                #     print("Buffer", self.Valve_buffer["PV1003"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV1003"] != self.Valve_buffer["PV1003"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1003"]:
                        self.PV1003.Set.ButtonLClicked()
                    else:
                        self.PV1003.Set.ButtonRClicked()
                    self.Valve_buffer["PV1003"] = received_dic_c["data"]["Valve"]["OUT"]["PV1003"]
                else:
                    pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV1004"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV1004"]:
                self.PV1004.Set.ButtonLClicked()
            else:
                self.PV1004.Set.ButtonRClicked()
            self.Valve_buffer["PV1004"] = received_dic_c["data"]["Valve"]["OUT"]["PV1004"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV1004"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV1004"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1004"]:
                    self.PV1004.Set.ButtonLClicked()
                else:
                    self.PV1004.Set.ButtonRClicked()
                self.Valve_buffer["PV1004"] = received_dic_c["data"]["Valve"]["OUT"]["PV1004"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV1004"]:
                #     print("PV1004", received_dic_c["data"]["Valve"]["OUT"]["PV1004"] != self.Valve_buffer["PV1004"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1004"])
                #     print("Buffer", self.Valve_buffer["PV1004"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV1004"] != self.Valve_buffer["PV1004"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1004"]:
                        self.PV1004.Set.ButtonLClicked()
                    else:
                        self.PV1004.Set.ButtonRClicked()
                    self.Valve_buffer["PV1004"] = received_dic_c["data"]["Valve"]["OUT"]["PV1004"]
                else:
                    pass

        # if not received_dic_c["data"]["Valve"]["MAN"]["PV1005"]:
        #     if received_dic_c["data"]["Valve"]["OUT"]["PV1005"]:
        #         self.PV1005.Set.ButtonLClicked()
        #     else:
        #         self.PV1005.Set.ButtonRClicked()
        #     self.Valve_buffer["PV1005"] = received_dic_c["data"]["Valve"]["OUT"]["PV1005"]
        # elif received_dic_c["data"]["Valve"]["MAN"]["PV1005"]:
        #     if received_dic_c["data"]["Valve"]["Busy"]["PV1005"]:
        #         if received_dic_c["data"]["Valve"]["OUT"]["PV1005"]:
        #             self.PV1005.Set.ButtonLClicked()
        #         else:
        #             self.PV1005.Set.ButtonRClicked()
        #         self.Valve_buffer["PV1005"] = received_dic_c["data"]["Valve"]["OUT"]["PV1005"]
        #     elif not received_dic_c["data"]["Valve"]["Busy"]["PV1005"]:
        #         #     print("PV1005", received_dic_c["data"]["Valve"]["OUT"]["PV1005"] != self.Valve_buffer["PV1005"])
        #         #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1005"])
        #         #     print("Buffer", self.Valve_buffer["PV1005"])
        #         if received_dic_c["data"]["Valve"]["OUT"]["PV1005"] != self.Valve_buffer["PV1005"]:
        #             if received_dic_c["data"]["Valve"]["OUT"]["PV1005"]:
        #                 self.PV1005.Set.ButtonLClicked()
        #             else:
        #                 self.PV1005.Set.ButtonRClicked()
        #             self.Valve_buffer["PV1005"] = received_dic_c["data"]["Valve"]["OUT"]["PV1005"]
        #         else:
        #             pass

        if not received_dic_c["data"]["Valve"]["MAN"]["PV1006"]:
            if received_dic_c["data"]["Valve"]["OUT"]["PV1006"]:
                self.PV1006.Set.ButtonLClicked()
            else:
                self.PV1006.Set.ButtonRClicked()
            self.Valve_buffer["PV1006"] = received_dic_c["data"]["Valve"]["OUT"]["PV1006"]
        elif received_dic_c["data"]["Valve"]["MAN"]["PV1006"]:
            if received_dic_c["data"]["Valve"]["Busy"]["PV1006"]:
                if received_dic_c["data"]["Valve"]["OUT"]["PV1006"]:
                    self.PV1006.Set.ButtonLClicked()
                else:
                    self.PV1006.Set.ButtonRClicked()
                self.Valve_buffer["PV1006"] = received_dic_c["data"]["Valve"]["OUT"]["PV1006"]
            elif not received_dic_c["data"]["Valve"]["Busy"]["PV1006"]:
                #     print("PV1006", received_dic_c["data"]["Valve"]["OUT"]["PV1006"] != self.Valve_buffer["PV1006"])
                #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1006"])
                #     print("Buffer", self.Valve_buffer["PV1006"])
                if received_dic_c["data"]["Valve"]["OUT"]["PV1006"] != self.Valve_buffer["PV1006"]:
                    if received_dic_c["data"]["Valve"]["OUT"]["PV1006"]:
                        self.PV1006.Set.ButtonLClicked()
                    else:
                        self.PV1006.Set.ButtonRClicked()
                    self.Valve_buffer["PV1006"] = received_dic_c["data"]["Valve"]["OUT"]["PV1006"]
                else:
                    pass

        # if not received_dic_c["data"]["Valve"]["MAN"]["PV1007"]:
        #     if received_dic_c["data"]["Valve"]["OUT"]["PV1007"]:
        #         self.PV1007.Set.ButtonLClicked()
        #     else:
        #         self.PV1007.Set.ButtonRClicked()
        #     self.Valve_buffer["PV1007"] = received_dic_c["data"]["Valve"]["OUT"]["PV1007"]
        # elif received_dic_c["data"]["Valve"]["MAN"]["PV1007"]:
        #     if received_dic_c["data"]["Valve"]["Busy"]["PV1007"]:
        #         if received_dic_c["data"]["Valve"]["OUT"]["PV1007"]:
        #             self.PV1007.Set.ButtonLClicked()
        #         else:
        #             self.PV1007.Set.ButtonRClicked()
        #         self.Valve_buffer["PV1007"] = received_dic_c["data"]["Valve"]["OUT"]["PV1007"]
        #     elif not received_dic_c["data"]["Valve"]["Busy"]["PV1007"]:
        #         #     print("PV1007", received_dic_c["data"]["Valve"]["OUT"]["PV1007"] != self.Valve_buffer["PV1007"])
        #         #     print("OUT", received_dic_c["data"]["Valve"]["OUT"]["PV1007"])
        #         #     print("Buffer", self.Valve_buffer["PV1007"])
        #         if received_dic_c["data"]["Valve"]["OUT"]["PV1007"] != self.Valve_buffer["PV1007"]:
        #             if received_dic_c["data"]["Valve"]["OUT"]["PV1007"]:
        #                 self.PV1007.Set.ButtonLClicked()
        #             else:
        #                 self.PV1007.Set.ButtonRClicked()
        #             self.Valve_buffer["PV1007"] = received_dic_c["data"]["Valve"]["OUT"]["PV1007"]
        #         else:
        #             pass

        # set LOOPPID double button status ON/OFF also the status in the subwindow

        if not received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1001"]:
            if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]:
                self.HTR1001.LOOPPIDWindow.Mode.ButtonLClicked()
                self.HTR1001.State.ButtonLClicked()
            else:
                self.HTR1001.LOOPPIDWindow.Mode.ButtonRClicked()
                self.HTR1001.State.ButtonRClicked()
            self.LOOPPID_EN_buffer["HTR1001"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]
        elif received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1001"]:
            if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1001"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]:
                    self.HTR1001.LOOPPIDWindow.Mode.ButtonLClicked()
                    self.HTR1001.State.ButtonLClicked()
                else:
                    self.HTR1001.LOOPPIDWindow.Mode.ButtonRClicked()
                    self.HTR1001.State.ButtonRClicked()
                self.LOOPPID_EN_buffer["HTR1001"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]
            elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1001"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"] != self.LOOPPID_EN_buffer["HTR1001"]:
                    if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]:
                        self.HTR1001.LOOPPIDWindow.Mode.ButtonLClicked()
                        self.HTR1001.State.ButtonLClicked()
                    else:
                        self.HTR1001.LOOPPIDWindow.Mode.ButtonRClicked()
                        self.HTR1001.State.ButtonRClicked()
                    self.LOOPPID_EN_buffer["HTR1001"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"]
                else:
                    pass

        self.HTR1001.ColorLabel(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"])
        self.HTR1001.Power.ColorButton(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.RTD1.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1001"][0])
        self.HTR1001.LOOPPIDWindow.RTD2.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1001"][1])

        if not received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1002"]:
            if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]:
                self.HTR1002.LOOPPIDWindow.Mode.ButtonLClicked()
                self.HTR1002.State.ButtonLClicked()
            else:
                self.HTR1002.LOOPPIDWindow.Mode.ButtonRClicked()
                self.HTR1002.State.ButtonRClicked()
            self.LOOPPID_EN_buffer["HTR1002"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]
        elif received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1002"]:
            if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1002"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]:
                    self.HTR1002.LOOPPIDWindow.Mode.ButtonLClicked()
                    self.HTR1002.State.ButtonLClicked()
                else:
                    self.HTR1002.LOOPPIDWindow.Mode.ButtonRClicked()
                    self.HTR1002.State.ButtonRClicked()
                self.LOOPPID_EN_buffer["HTR1002"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]
            elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1002"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"] != self.LOOPPID_EN_buffer["HTR1002"]:
                    if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]:
                        self.HTR1002.LOOPPIDWindow.Mode.ButtonLClicked()
                        self.HTR1002.State.ButtonLClicked()
                    else:
                        self.HTR1002.LOOPPIDWindow.Mode.ButtonRClicked()
                        self.HTR1002.State.ButtonRClicked()
                    self.LOOPPID_EN_buffer["HTR1002"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"]
                else:
                    pass

        self.HTR1002.ColorLabel(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"])
        self.HTR1002.Power.ColorButton(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.RTD1.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1002"][0])
        self.HTR1002.LOOPPIDWindow.RTD2.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1002"][1])

        if not received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1003"]:
            if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]:
                self.HTR1003.LOOPPIDWindow.Mode.ButtonLClicked()
                self.HTR1003.State.ButtonLClicked()
            else:
                self.HTR1003.LOOPPIDWindow.Mode.ButtonRClicked()
                self.HTR1003.State.ButtonRClicked()
            self.LOOPPID_EN_buffer["HTR1003"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]
        elif received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1003"]:
            if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1003"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]:
                    self.HTR1003.LOOPPIDWindow.Mode.ButtonLClicked()
                    self.HTR1003.State.ButtonLClicked()
                else:
                    self.HTR1003.LOOPPIDWindow.Mode.ButtonRClicked()
                    self.HTR1003.State.ButtonRClicked()
                self.LOOPPID_EN_buffer["HTR1003"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]
            elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1003"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"] != self.LOOPPID_EN_buffer["HTR1003"]:
                    if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]:
                        self.HTR1003.LOOPPIDWindow.Mode.ButtonLClicked()
                        self.HTR1003.State.ButtonLClicked()
                    else:
                        self.HTR1003.LOOPPIDWindow.Mode.ButtonRClicked()
                        self.HTR1003.State.ButtonRClicked()
                    self.LOOPPID_EN_buffer["HTR1003"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"]
                else:
                    pass

        self.HTR1003.ColorLabel(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"])
        self.HTR1003.Power.ColorButton(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.RTD1.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1003"][0])
        self.HTR1003.LOOPPIDWindow.RTD2.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1003"][1])

        if not received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1005"]:
            if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"]:
                self.HTR1005.LOOPPIDWindow.Mode.ButtonLClicked()
                self.HTR1005.State.ButtonLClicked()
            else:
                self.HTR1005.LOOPPIDWindow.Mode.ButtonRClicked()
                self.HTR1005.State.ButtonRClicked()
            self.LOOPPID_EN_buffer["HTR1005"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"]
        elif received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1005"]:
            if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1005"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"]:
                    self.HTR1005.LOOPPIDWindow.Mode.ButtonLClicked()
                    self.HTR1005.State.ButtonLClicked()
                else:
                    self.HTR1005.LOOPPIDWindow.Mode.ButtonRClicked()
                    self.HTR1005.State.ButtonRClicked()
                self.LOOPPID_EN_buffer["HTR1005"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"]
            elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1005"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"] != self.LOOPPID_EN_buffer["HTR1005"]:
                    if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"]:
                        self.HTR1005.LOOPPIDWindow.Mode.ButtonLClicked()
                        self.HTR1005.State.ButtonLClicked()
                    else:
                        self.HTR1005.LOOPPIDWindow.Mode.ButtonRClicked()
                        self.HTR1005.State.ButtonRClicked()
                    self.LOOPPID_EN_buffer["HTR1005"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"]
                else:
                    pass

        self.HTR1005.ColorLabel(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"])
        self.HTR1005.Power.ColorButton(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"])
        self.HTR1005.LOOPPIDWindow.RTD1.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1005"][0])
        self.HTR1005.LOOPPIDWindow.RTD2.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1005"][1])



        if not received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1004"]:
            if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]:
                self.HTR1004.LOOPPIDWindow.Mode.ButtonLClicked()
                self.HTR1004.State.ButtonLClicked()
            else:
                self.HTR1004.LOOPPIDWindow.Mode.ButtonRClicked()
                self.HTR1004.State.ButtonRClicked()
            self.LOOPPID_EN_buffer["HTR1004"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]
        elif received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1004"]:
            if received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1004"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]:
                    self.HTR1004.LOOPPIDWindow.Mode.ButtonLClicked()
                    self.HTR1004.State.ButtonLClicked()
                else:
                    self.HTR1004.LOOPPIDWindow.Mode.ButtonRClicked()
                    self.HTR1004.State.ButtonRClicked()
                self.LOOPPID_EN_buffer["HTR1004"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]
            elif not received_dic_c["data"]["LOOPPID"]["Busy"]["HTR1004"]:
                if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"] != self.LOOPPID_EN_buffer["HTR1004"]:
                    if received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]:
                        self.HTR1004.LOOPPIDWindow.Mode.ButtonLClicked()
                        self.HTR1004.State.ButtonLClicked()
                    else:
                        self.HTR1004.LOOPPIDWindow.Mode.ButtonRClicked()
                        self.HTR1004.State.ButtonRClicked()
                    self.LOOPPID_EN_buffer["HTR1004"] = received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"]
                else:
                    pass

        self.HTR1004.ColorLabel(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"])
        self.HTR1004.Power.ColorButton(received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.RTD1.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1004"][0])
        self.HTR1004.LOOPPIDWindow.RTD2.SetValue(received_dic_c["data"]["LOOPPID"]["TT"]["HTR1004"][1])



        self.HTR1001.LOOPPIDWindow.Interlock.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["INTLKD"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.Error.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["ERR"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.MANSP.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1001"])
        if True in [received_dic_c["data"]["LOOPPID"]["SATHI"]["HTR1001"],
                    received_dic_c["data"]["LOOPPID"]["SATLO"]["HTR1001"]]:

            self.HTR1001.LOOPPIDWindow.SAT.UpdateColor(True)
        else:
            self.HTR1001.LOOPPIDWindow.SAT.UpdateColor(False)
        self.HTR1001.LOOPPIDWindow.ModeREAD.Field.setText(

            self.FindDistinctTrue(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1001"],
                                  received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1001"],
                                  received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1001"],
                                  received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1001"]))
        self.HTR1001.LOOPPIDWindow.EN.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["EN"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.HIGH.SetValue(
            received_dic_c["data"]["LOOPPID"]["HI_LIM"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.LOW.SetValue(
            received_dic_c["data"]["LOOPPID"]["LO_LIM"]["HTR1001"])
        self.HTR1001.LOOPPIDWindow.SETSP.SetValue(
            self.FetchSetPoint(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["SET0"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["SET1"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["SET2"]["HTR1001"],
                               received_dic_c["data"]["LOOPPID"]["SET3"]["HTR1001"]))
        self.HTR1001.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1001"])

        self.HTR1002.LOOPPIDWindow.Interlock.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["INTLKD"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.Error.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["ERR"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.MANSP.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1002"])
        if True in [received_dic_c["data"]["LOOPPID"]["SATHI"]["HTR1002"],
                    received_dic_c["data"]["LOOPPID"]["SATLO"]["HTR1002"]]:

            self.HTR1002.LOOPPIDWindow.SAT.UpdateColor(True)
        else:
            self.HTR1002.LOOPPIDWindow.SAT.UpdateColor(False)
        self.HTR1002.LOOPPIDWindow.ModeREAD.Field.setText(

            self.FindDistinctTrue(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1002"],
                                  received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1002"],
                                  received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1002"],
                                  received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1002"]))
        self.HTR1002.LOOPPIDWindow.EN.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["EN"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.HIGH.SetValue(
            received_dic_c["data"]["LOOPPID"]["HI_LIM"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.LOW.SetValue(
            received_dic_c["data"]["LOOPPID"]["LO_LIM"]["HTR1002"])
        self.HTR1002.LOOPPIDWindow.SETSP.SetValue(
            self.FetchSetPoint(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["SET0"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["SET1"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["SET2"]["HTR1002"],
                               received_dic_c["data"]["LOOPPID"]["SET3"]["HTR1002"]))
        self.HTR1002.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1002"])

        #
        self.HTR1003.LOOPPIDWindow.Interlock.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["INTLKD"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.Error.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["ERR"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.MANSP.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1003"])
        if True in [received_dic_c["data"]["LOOPPID"]["SATHI"]["HTR1003"],
                    received_dic_c["data"]["LOOPPID"]["SATLO"]["HTR1003"]]:

            self.HTR1003.LOOPPIDWindow.SAT.UpdateColor(True)
        else:
            self.HTR1003.LOOPPIDWindow.SAT.UpdateColor(False)
        self.HTR1003.LOOPPIDWindow.ModeREAD.Field.setText(

            self.FindDistinctTrue(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1003"],
                                  received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1003"],
                                  received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1003"],
                                  received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1003"]))
        self.HTR1003.LOOPPIDWindow.EN.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["EN"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.HIGH.SetValue(
            received_dic_c["data"]["LOOPPID"]["HI_LIM"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.LOW.SetValue(
            received_dic_c["data"]["LOOPPID"]["LO_LIM"]["HTR1003"])
        self.HTR1003.LOOPPIDWindow.SETSP.SetValue(
            self.FetchSetPoint(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["SET0"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["SET1"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["SET2"]["HTR1003"],
                               received_dic_c["data"]["LOOPPID"]["SET3"]["HTR1003"]))
        self.HTR1003.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1003"])

        self.HTR1005.LOOPPIDWindow.Interlock.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["INTLKD"]["HTR1005"])
        self.HTR1005.LOOPPIDWindow.Error.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["ERR"]["HTR1005"])
        self.HTR1005.LOOPPIDWindow.MANSP.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1005"])
        if True in [received_dic_c["data"]["LOOPPID"]["SATHI"]["HTR1005"],
                    received_dic_c["data"]["LOOPPID"]["SATLO"]["HTR1005"]]:

            self.HTR1005.LOOPPIDWindow.SAT.UpdateColor(True)
        else:
            self.HTR1005.LOOPPIDWindow.SAT.UpdateColor(False)
        self.HTR1005.LOOPPIDWindow.ModeREAD.Field.setText(

            self.FindDistinctTrue(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1005"],
                                  received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1005"],
                                  received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1005"],
                                  received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1005"]))
        self.HTR1005.LOOPPIDWindow.EN.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["EN"]["HTR1005"])
        self.HTR1005.LOOPPIDWindow.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1005"])
        self.HTR1005.LOOPPIDWindow.HIGH.SetValue(
            received_dic_c["data"]["LOOPPID"]["HI_LIM"]["HTR1005"])
        self.HTR1005.LOOPPIDWindow.LOW.SetValue(
            received_dic_c["data"]["LOOPPID"]["LO_LIM"]["HTR1005"])
        self.HTR1005.LOOPPIDWindow.SETSP.SetValue(
            self.FetchSetPoint(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1005"],
                               received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1005"],
                               received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1005"],
                               received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1005"],
                               received_dic_c["data"]["LOOPPID"]["SET0"]["HTR1005"],
                               received_dic_c["data"]["LOOPPID"]["SET1"]["HTR1005"],
                               received_dic_c["data"]["LOOPPID"]["SET2"]["HTR1005"],
                               received_dic_c["data"]["LOOPPID"]["SET3"]["HTR1005"]))
        self.HTR1005.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1005"])

        self.HTR1004.LOOPPIDWindow.Interlock.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["INTLKD"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.Error.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["ERR"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.MANSP.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["MAN"]["HTR1004"])
        if True in [received_dic_c["data"]["LOOPPID"]["SATHI"]["HTR1004"],
                    received_dic_c["data"]["LOOPPID"]["SATLO"]["HTR1004"]]:

            self.HTR1004.LOOPPIDWindow.SAT.UpdateColor(True)
        else:
            self.HTR1004.LOOPPIDWindow.SAT.UpdateColor(False)
        self.HTR1004.LOOPPIDWindow.ModeREAD.Field.setText(

            self.FindDistinctTrue(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1004"],
                                  received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1004"],
                                  received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1004"],
                                  received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1004"]))
        self.HTR1004.LOOPPIDWindow.EN.UpdateColor(
            received_dic_c["data"]["LOOPPID"]["EN"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.HIGH.SetValue(
            received_dic_c["data"]["LOOPPID"]["HI_LIM"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.LOW.SetValue(
            received_dic_c["data"]["LOOPPID"]["LO_LIM"]["HTR1004"])
        self.HTR1004.LOOPPIDWindow.SETSP.SetValue(
            self.FetchSetPoint(received_dic_c["data"]["LOOPPID"]["MODE0"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["MODE1"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["MODE2"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["MODE3"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["SET0"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["SET1"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["SET2"]["HTR1004"],
                               received_dic_c["data"]["LOOPPID"]["SET3"]["HTR1004"]))
        self.HTR1004.Power.SetValue(
            received_dic_c["data"]["LOOPPID"]["OUT"]["HTR1004"])

        self.MFC1.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["FCV1001"])
        self.MFC1.LOOPPIDWindow.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["FCV1001"])

        self.MFC2.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["FCV1002"])
        self.MFC2.LOOPPIDWindow.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["FCV1002"])

        self.MFC1008.Power.SetValue(received_dic_c["data"]["LEFT_REAL"]["value"]["MFC1008"])
        # self.MFC1008.LOOPPIDWindow.OUT.SetValue(received_dic_c["data"]["LEFT_REAL"]["FCV1001"])


    @QtCore.Slot(object)
    def update_alarmwindow(self,list):
        # if len(dic)>0:
        #     print(dic)
        print(list[0])
        if True in list:
            print('alarm list',True)
        else:
            print(' alarm list',False)

        self.AlarmButton.CollectAlarm(list)
        # print("Alarm Status=", self.AlarmButton.Button.Alarm)
        if self.AlarmButton.Button.Alarm:
            self.AlarmButton.ButtonAlarmSetSignal()
        else:
            self.AlarmButton.ButtonAlarmResetSignal()
            self.AlarmButton.SubWindow.ResetOrder()



class UpdateClient(QtCore.QThread):
    client_data_transport = QtCore.Signal(object)
    def __init__(self, commands, command_lock):
        super().__init__()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'
        self.port = 6666
        self.Running=False
        self.period = 1
        self.commands = commands
        self.command_lock = command_lock

        print("client is connecting to the socket server")

        self.receive_dic = copy.deepcopy(env.DIC_PACK)
        self.commands_package = pickle.dumps({})

    @QtCore.Slot()
    def run(self):
        self.Running = True

        while True:
            try:
                self.client_socket.connect((self.host, self.port))

                # Set a timeout for socket operations to 10 seconds
                self.client_socket.settimeout(10)
                while True:
                    # send commands
                    self.send_commands()
                    print("client commands sent")
                    received_data = self.receive_packed_data()

                    # Deserialize pickle data to a dictionary
                    data_dict = pickle.loads(received_data)
                    self.update_data(data_dict)


            except socket.timeout:
                print("Connection timed out. Restarting client...")
                self.client_socket.close()
                break
        self.run()

    @QtCore.Slot()
    def stop(self):
        self.Running = False
        self.client_socket.close()



    def update_data(self,message):
        
        #message mush be a dictionary
        self.receive_dic = message
        self.client_data_transport.emit(self.receive_dic)
    def receive_packed_data(self):
        data_length_bytes = self.client_socket.recv(4)
        data_length = struct.unpack('!I', data_length_bytes)[0]

        # Receive the serialized data in chunks
        received_data = b''
        while len(received_data) < data_length:
            chunk = self.client_socket.recv(min(1024, data_length - len(received_data)))
            if not chunk:
                break
            received_data += chunk
        return received_data

    def pack_data(self, conn):
        data_transfer = pickle.dumps(self.commands)

        # Send JSON data to the client
        conn.sendall(len(data_transfer).to_bytes(4, byteorder='big'))

        # Send the serialized data in chunks
        for i in range(0, len(data_transfer), 1024):
            chunk = data_transfer[i:i + 1024]
            conn.sendall(chunk)


    def send_commands(self):
        # claim that whether MAN_SET is True or false
        print("Commands are here", self.commands,datetime.datetime.now())
        self.pack_data(self.client_socket)
        with self.command_lock:
            self.commands.clear()
        print("finished sending commands")






# Code entry point

if __name__ == "__main__":



    App = QtWidgets.QApplication(sys.argv)

    MW = MainWindow()

    # MW = HeaterSubWindow()
    # recover data
    # MW.Recover()
    if platform.system() == "Linux":
        MW.show()
        MW.showMinimized()
    else:
        MW.show()
    MW.activateWindow()
    # save data

    sys.exit(App.exec_())

    # AW = AlarmWin()
    # if platform.system() == "Linux":
    #     AW.show()
    #     AW.showMinimized()
    # else:
    #     AW.show()
    # AW.activateWindow()
    # sys.exit(App.exec_())



"""
Note to run on VS on my computer...

import os
os.chdir("D:\\Pico\\SlowDAQ\\Qt\\SlowDAQ")
exec(open("SlowDAQ.py").read())
"""