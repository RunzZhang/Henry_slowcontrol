'''Chapter 6 Alarm system
After the previous 5 chapter reading, most of basic structure of slowcontrol is finished. But I left alarm at last because
it is not a single class or logic as previous ones. It is more integrated -- It is more like a mini - slowcontrol code.
On background side, you need to check if every value is in normal range, otherwise send out alarms. On GUI side, users should be
able to adjust the alarm limits, and those limits need to be transferred to background code side.
Beides, the background need to read a default configuration when rebooted but that configuration can be customized easily i.e not like
Henry_env-- it is hard coded. And it should support multiple alarm configuration storage so user can switch between them.

So I will go through the main parts of alarm design. Most codes are just copied from Henry code without edition.



6.1 Check alarms
From UpdatePLC class:
    This check for every adam module reading, is the reading value out of range
                for keyTT_AD1 in self.TT_AD1_dic:
                    self.check_TT_AD1_alarm(keyTT_AD1)



##############################################################################################
    This function is the check_TT_AD1_alarm(), first it check if lower limit is higher than higher limit, if so, it is invalid
    Then it compares if the value is out of range. If so, then send alarm out.
    similar as database, the alarms won't be sent out immediately because we don't want to frequent alarms it is triggered.
     It will be stored until the the alarm class is ready to send out messages.
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
########################################################################################################



6.2 Alarm Message
The class Message_Manager(threading.Thread) handles the alarm messages. It collects all alarm messages and decide when and
how to send them out.
For now, there are 2 ways, the 1st is by email requiring SMTP protocal and the second is slack requiring the slack robot permission
Here we just focus on the python code side:

6.2.1 Email
This is core part of sending email. You need to initilization though. This cannot be ran alone
So you just have the similar info as you write a email, and put alarm messages (strubg), in to sendmail() function
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

6.2.2 Slack
Similar, but you need get the channel id and set the robot before you can send slack messages.
    def slack_alarm(self, message):
        # Call the conversations.list method using the WebClient
        result = self.client.chat_postMessage(
            channel=self.channel_id,
            text=str(message)
        )
        print("slackalarm",result)

6.3 Alarm GUI
Henry_GUI_Widgets.py/class AlarmWin(QtWidgets.QMainWindow):
It is similar idea of creating a new window.
The main difference is that users can use checkbox to choose whether to trigger a alarm or not.
Previously we had the function that if one alarm is triggered, it will come up to the begining of the alarm list. That is the function
of ReassignRTD1Order(). But it was disabled later.

6.4 Alarm initilization
As I mentioned before, alarm settings should be able to be saved and recalled quickly. And everytime if the background code reset,
it should retrieve a default settings. That is alarm's initilization.
The function of read and write configuration is in class Loadfile(QtWidgets.QWidget)/class CustomSave(QtWidgets.QWidget)
And auto-load function is in alarm_set.py



PRACTICE: Could you create a code: it throws a dice every 5 seconds. If the number is 6, send alarm message via slack saying like "Largest" and if the number is 1, send alarm message like "Smallest" or whatever you like.
And save those results in order into a file like txt or csv. '''