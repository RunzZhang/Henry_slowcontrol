
import os.path
from sshtunnel import SSHTunnelForwarder
import mysql.connector
import datetime
import time as tm
import paramiko, pymysql
import pandas as pd
import csv, pytz
# get the current time with resolution to seconds
def datetime_in_s():
    d=datetime.datetime.now()
    timeR = int(d.microsecond%1e6)
    delta=datetime.timedelta(microseconds=timeR)
    x=d-delta
    return x
# get the current time with resolution to microseconds
def datetime_in_1e5micro():
    d=datetime.datetime.now()
    timeR = int(d.microsecond%1e5)
    delta=datetime.timedelta(microseconds=timeR)
    x=d-delta
    return x
# get the time in gmt time with resolution to microseconds assuming initially we are in Pacific Time
# this is for Grafana to read the time correctly. Somehow Grafana cannot read the timezone correctly even it has the timezone option.
def datetime_in_1e5micro_gmt():
    la_tz = pytz.timezone('America/Los_Angeles')

    # Get the current time in America/Los_Angeles
    current_time_la = datetime.datetime.now(la_tz)

    # Convert the current time to GMT (UTC)
    current_time_gmt = current_time_la.astimezone(pytz.utc)

    timeR = int(current_time_gmt.microsecond%1e5)
    delta=datetime.timedelta(microseconds=timeR)
    x=current_time_gmt-delta
    return x

# print the current time -0.1s.
# for example, if we are 12:00 then it will print 11:59.90.
# This is for recording the valve status changes
def early_datetime():
    d = datetime.datetime.now()
    timeR = int(d.microsecond % 1e5)
    delta = datetime.timedelta(microseconds=timeR)
    x = d - delta - datetime.timedelta(microseconds=1e5)
    return x
# similar, but current time +0.1s
def later_datetime():
    d = datetime.datetime.now()
    timeR = int(d.microsecond % 1e5)
    delta = datetime.timedelta(microseconds=timeR)
    x = d - delta + datetime.timedelta(microseconds=1e5)
    return x

def UNIX_time(self):
    return int(tm.time())


# Definition of the database
class mydatabase():
    def __init__(self):
        # to log into database, you need the database machine IP, the user name you use to log into database,
        # the username's password and the database name you use
        # The password usually won't show in the python code but in ENV variable instead for cyber security
        self.db = mysql.connector.connect(host="128.111.19.61", user="slowcontrol",
                                          passwd="Th3Slow1!", database="slowcontrol")
        # cursor is always required to execuate commands
        self.mycursor = self.db.cursor()

        # initialzation of a dataframe.
        # the purpose of this is that usually we need to write multiple data into database. For example, we need to write TT1000, TT1001, TT1002 and so on
        # but if we write it one by one, it took great time to finish the commands.
        # i.e connect to mysql-> write TT1000-> finish the command -> disconnected -> connect again-> write TT1001_> finish the command-> disconnected
        # instead, we connect once and write the whole data table into database
        #i.e connect to mysql-> write table containing TT1000, TT1001... into database-> finish the commands -> disconnected
        self.stack_v2 = pd.DataFrame(columns=['Instrument', 'Time', 'Value', 'GMT'])
    # query is to execuate a mysql command, the statement is in mysql query format
    # This is for testing if one can directly execuate mysql query
    def query(self,statement):
        try:
            self.mycursor.execute(statement)
        except:
            print("Statement formal is wrong, please check it")

    # insert data read from PLC into database with the instrument name, timestamp and the instrument value
    def insert_data_into_datastorage(self,instrument, time,value):
        # time must be like '2021-02-17 20:36:26' or datetime.datetime(yy,mm,dd,hh,mm,ss)
        # value is a decimal from -9999.999 to 9999.999
        # name must be consistent with P&ID
        data=(instrument, time,value)
        # this execuate the INSERT query
        # the (%s, %s, %s) content would be replaced by data which is (instrument, time,value)
        self.mycursor.execute(
            "INSERT INTO DataStorage (Instrument, Time, Value) VALUES(%s, %s, %s);", data)
        # commit is required to save the data truly into database. Otherwise, the table won't change either
        self.db.commit()

    # this is similar to the previous function. but instead without commit.
    # this is for writing multiple data into database and commit(save) together to save time
    def insert_data_into_datastorage_wocommit(self,instrument, time,value):
        # time must be like '2021-02-17 20:36:26' or datetime.datetime(yy,mm,dd,hh,mm,ss)
        # value is a decimal from -9999.999 to 9999.999
        # name must be consistent with P&ID
        data=(instrument, time,value)
        self.mycursor.execute(
            "INSERT INTO DataStorage (Instrument, Time, Value) VALUES(%s, %s, %s);", data)
    # This is still similar but save data into stack instead of directly execuating the data
    def insert_data_into_stack_v2(self,instrument, time,value, gmt_time):
        # create a new dataframe with new data
        new_df=pd.DataFrame({'Instrument':instrument,"Time":time,"Value": value,"GMT": gmt_time},index=[len(self.stack_v2)])
        # combine the old stack with new data to generate a new table
        self.stack_v2 = pd.concat((self.stack_v2,new_df), axis=0,ignore_index= True)

    # reorder the table in time order.
    # for example intially the data structure
    # instrument1 | 12:00 | 1
    # instrument1 | 12:01 | 2
    # instrument2 | 12:00 | 3
    # instrument2 | 12:01 | 4
    # but we want bc it is easier for database to deal with data in time increasing order
    # instrument1 | 12:00 | 1
    # instrument2 | 12:00 | 3
    # instrument1 | 12:01 | 2
    # instrument2 | 12:01 | 4

    def sort_stack_v2(self):
        self.stack_v2 = self.stack_v2.sort_values(by=['Time'])
        self.stack_v2 = self.stack_v2.reset_index(drop=True)

    def convert_stack_into_queries_v2(self):
        for idx in self.stack_v2.index:
            newdata = (self.stack_v2['Instrument'][idx], self.stack_v2['Time'][idx], self.stack_v2['Value'][idx], self.stack_v2["GMT"][idx])
            # print(newdata)

            self.mycursor.execute(
                "INSERT INTO DataStorage (Instrument, Time, Value, GMT) VALUES(%s, %s, %s, %s);", newdata)
    # reset the stack
    def drop_stack_v2(self):
        self.stack_v2 = self.stack_v2.iloc[0:0]
        # print(self.stack_v2)
    # print the data and save it into csv file
    def select_export_data_datastorage(self,instrument, start_time, end_time,filename):
        query = "SELECT * FROM DataStorage WHERE Instrument=%s AND Time BETWEEN %s AND %s;"
        data = (instrument,start_time,end_time)
        self.mycursor.execute(query,data)
        rows = self.mycursor.fetchall()
        column_names = [i[0] for i in self.mycursor.description]
        # Define the output CSV file path
        output_file = '/home/hep/Downloads/'+filename

        # Write the data to a CSV file
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the column names as the first row
            writer.writerow(column_names)
            # Write the rows
            writer.writerows(rows)

        self.close_database()
    # print out data between 2 timepoints
    def show_data_datastorage(self,start_time=None, end_time=None):
        # if start_time==None or end_time==None:
        print(start_time,end_time)
        query = "SELECT * FROM DataStorage"
        self.mycursor.execute(query)
        for (ID,Instrument,Time, Value) in self.mycursor:
            print(str("DataStorage"+"| {} | {} | {}".format(Instrument,Time, Value)))
    # safely disconnect from database
    def close_database(self):
        self.mycursor.close()
        self.db.close()


# test sbcslowcontrol database

if __name__ == "__main__":
    # call the class
    db = mydatabase()
    # get the current time
    dt = datetime_in_s()
    # get current time -0.1 s
    early_dt = early_datetime()
    print(dt)


    db.insert_data_into_stack("PV5535", early_dt, 0)
    db.insert_data_into_stack("PV5535", dt, 1)
    db.insert_data_into_stack("PV5485", early_dt, 1)
    db.insert_data_into_stack("PV5485", dt, 0)
    db.insert_data_into_stack("PV5935", early_dt, 0)
    db.insert_data_into_stack("PV5595", dt, 1)
    db.sort_stack()

    db.show_data_datastorage()

    # db.create_table("PV1204")
    # db.insert_data("PV1102", now, random.randrange(100))
    # db.show_data("PV1102")

    db.show_tables()

    db.close_database()

    # test datetime function
    print(datetime_in_1e5micro())
    print(early_datetime())


