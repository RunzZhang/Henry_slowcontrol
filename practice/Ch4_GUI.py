"""Chapter 4
GUI design
This parts is hard to show sample code because GUI design really depends on user's demands. So instead, I will just give you
an idea what is the GUI structured.
1.Imagining that you have a big canvas, then this is your Henry_GUI.py/ GUI main window, which is inherted from QtWidgets.QMainWindow
Then next step is to pain on the canvas

2. You can put tab in the canvas first
self.Tab = QtWidgets.QTabWidget(self)
        self.Tab.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Tab.setStyleSheet("font-weight: bold; font-size: 20px; font-family: Times;")
        self.Tab.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.Tab.setGeometry(QtCore.QRect(0 * R, 0 * R, 2400 * R, 1400 * R))

so that you can switch between tabs


3. Now you need to put different your own design on to the tabs. This is more like put a stiker to the canvas. You first
need to desgin the sticker(widget), and then recall it to the tab.

3.1 All designs are in Henry_GUI_Widgets.py To design a widget, the idea is still similar. create a small canvas, which is
QtWidgets.QWidget now. And add details to the small canvas like Qbutton, QCheckbox, etc.

3.2 to use the widgets, you just call it in the mainwindows, for example:
self.PV1001 = Valve_v2(self.ThermosyphonTab) # call the widget class Valve_v2 and put it onto Thermosyphon tab
        self.PV1001.Label.setText("PV1001") # Set the text of the Valve_v2 to PV1001
        self.PV1001.move(1035 * R, 165 * R)  # move it to assigned position


3.3 How to design a good widgets? Good question! You can either refer to mycodes or go to online to search for some
sample code. Sorry, as I said before, it really depends on your demands


4. Update value of GUI dynamically
You need to define a function to update value of your widgets. For example, This update the RTD10 text box value from received data
, which is what you fetched from Chapter 3.
        self.AlarmButton.SubWindow.RTD10.Indicator.SetValue(
            received_dic_c["data"]["TT"]["AD1"]["value"]["RTD10"])

PRACTICE: I probably shouldn't ask you to do this since I didn't give enough example.
a.Find a class in the Henry_GUI_Widgets.py which can control and print out the solenoid valve status. (obvious right?)
b. Then what is the difference between different versions?
"""
