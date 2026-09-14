"""This is a slowcontrol related document to train how to code the slowcontrol and GUI
Henry_background.py Chapter 2
This chapter focuses on the the datastorage after you fetch data from PLC
The related code is Henry_watchdog_database.py/mydatabase and Henry_background.py/UpdateDatabase
mydatabase is the class definition and UpdateDatabase recalls the mydatabase class to match the slowcontrol data flow.
So we mainly focus on the mydatabase()
This parts assuming you have already correctly configured mysql on your machine. like downloading Mysql Community
2.1 mysql connection

 self.db = mysql.connector.connect(host="128.111.19.61", user="slowcontrol",
                                          passwd=os.environ.get("SLOWCONTROL_LOCAL_TOKEN"), database="slowcontrol")
 host is the host ip your database is at,
 user is the mysql user name,
 password is the user's password, saved as linux enviromental variable for cyber security
 database is the database name in mysql you will use
 if this runs correctly, there should be no error

 2.2 mysql read
after you get the db. You can call many different function to execuate queries, which is same as Mysql way. But first thing
to notice is that you need cursor.:
For example:
    def show_data_datastorage(): # this shows all data in DataStorage and print out the Instrument, Time, Value column

        query = "SELECT * FROM DataStorage"
        self.mycursor.execute(query)
        for (ID,Instrument,Time, Value) in self.mycursor:
            print(str("DataStorage"+"| {} | {} | {}".format(Instrument,Time, Value)))

2.3 write
similar idea, but you need to commit it before the mysql actually write data to database
    def insert_data_into_datastorage(instrument, time,value):
        # time must be like '2021-02-17 20:36:26' or datetime.datetime(yy,mm,dd,hh,mm,ss)
        # value is a decimal from -9999.999 to 9999.999
        # name must be consistent with P&ID
        data=(instrument, time,value)
        self.mycursor.execute(
            "INSERT INTO DataStorage (Instrument, Time, Value) VALUES(%s, %s, %s);", data)
        self.db.commit()

2.4 write multi-rows
However, in database writing, we usually need to write a lot of rows at one time. If we follows write data1, commit1, write data2, commit2
This will make mysql execuation time extreme long. Instead, we put data into one long query and then execuate it. But to notice, we need
to order it in time order to fit in the database time column configuration.


#########################################################################################################################
    def insert_data_into_stack(self,instrument, time,value, gmt_time): # Put data all into stack
        # time must be like '2021-02-17 20:36:26' or datetime.datetime(yy,mm,dd,hh,mm,ss)
        # value is a decimal from -9999.999 to 9999.999
        # name must be consistent with P&ID
        new_df = pd.DataFrame({'Instrument': instrument, "Time": time, "Value": value, "GMT": gmt_time},
                              index=[len(self.stack)])
        self.stack = pd.concat((self.stack, new_df), axis=0, ignore_index=True)

    def sort_stack(self):  # order the stack in time order
        self.stack = self.stack.sort_values(by=['Time'])
        self.stack = self.stack.reset_index(drop=True)

    def convert_stack_into_queries(self): # transfer stack into a  long query and execute it. Don't forget to commit it afterwards!
        for idx in self.stack.index:
            newdata = (self.stack['Instrument'][idx], self.stack['Time'][idx], self.stack['Value'][idx],
                       self.stack["GMT"][idx])
            # print(newdata)

            self.mycursor.execute(
                "INSERT INTO DataStorage (Instrument, Time, Value, GMT) VALUES(%s, %s, %s, %s);", newdata)
##############################################################################################################################

PRACTICE:
try to show all the tables under one database, for example, named as "slowcontrol"
"""