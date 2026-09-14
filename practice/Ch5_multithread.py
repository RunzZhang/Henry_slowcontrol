'''Chapter 5
In this chapter, we will go through multithread and how to pass data to different threads.
Why do we need multi-thread? For example, background code, fetches data from PLC, saves data to mysql, sends data to
GUI and sends out alarms. These activities are almost happen simutaneously. Even not, if one function blocks malfunctions or hangs on,
We need to keep other blocks still keep running. So that requires our code need to operate those functions in parallel.
That is why we need multithread.

5.1 Parallel configuration in Henry_background.py
Although those function blocks run in parallel, but they do share something in common -- data from PLC. So we need to have
a method that those threads can share the data.
You can imagine the code runs like this. Each thread is a kid. And the data pool is a basket. Kids share the same basket, and
whenever they need a new apple from the baskt, they will pick up apples from it.
That is to say, threads share a same data pool and PLC thread will update/read the data pool while other threads can only read from data pool.
Aside from this, threads are basically free to do their own jobs.

5.2 Thread communication
Here I give the simplest example --2 threads.'''

import datetime, threading, time, random
def datetime_in_1e5micro(): # print current time in time resolution of micro seconds
    d=datetime.datetime.now()
    timeR = int(d.microsecond%1e5)
    delta=datetime.timedelta(microseconds=timeR)
    x=d-delta
    return x

class FakePLC(threading.Thread):

    # Here we just generate dummy data with random seed.
    # This is our 1st class to generate data and pass data to the data pool
    # it inherits from package threading, so it has all thread properties

    def __init__(self, plc_data, plc_lock, global_time,timelock, *args, **kwargs):
        # it has 4 parameters, lock is for lock the data so that only 1 class is able to write/read data into datapool
        # to avoid chaos when multi-thread trying to modifying same data pool
        # _data and global_time is the corresponding data pool to be shared

        threading.Thread.__init__(self, *args, **kwargs)
        self.plc_data = plc_data
        self.plc_lock = plc_lock
        self.global_time = global_time
        self.timelock = timelock

    def run(self):

        self.Running = True

        while self.Running:

            with self.timelock: # lock the time data
                self.global_time.update({"plctime" :datetime_in_1e5micro()}) # update the global time
                print("PLC updating", self.global_time["plctime"])

            with self.plc_lock:
                fake_data = random.randint(1,1000) # generate random fake data from 1 to 1k.
                self.plc_data={"data":fake_data} # put the data in to data pool

            time.sleep(1) # sleep for next loop




class Fake_Message(threading.Thread):
    # this is a class to received data and print out it.
    # it inherits from package threading, so it has all thread properties
    def __init__(self, plc_data, plc_lock, global_time,timelock, *args, **kwargs):
        super().__init__()
        threading.Thread.__init__(self, *args, **kwargs)
        self.plc_data = plc_data
        self.plc_lock = plc_lock
        self.global_time = global_time
        self.timelock = timelock

    def run(self):

        self.Running = True

        while self.Running:

            with self.timelock: # read time passed by the data pool
                print("PLC time from Message view", self.global_time["plctime"])

            with self.plc_lock: # read data passed by the data pool
                data_received = dict(self.plc_data)
                print("PLC data from Message view", data_received)

            time.sleep(1)

class MainClass():
    # this class is to recall the previous defined class and build the data pool so that every class can share it.
    def __init__(self):
        # initilization of data and create the data pool to be shared
        self.plc_data = {"data":-1} # initialization of the data
        self.global_time={"plctime":datetime_in_1e5micro()}
        self.plc_lock = threading.Lock()
        self.timelock = threading.Lock()
        self.StartUpdater()


    def StartUpdater(self):

        # Call the previous defined classes, and distribute data pool to those classes
        # also these are the two parallel threads
        self.threadPLC = FakePLC(plc_data=self.plc_data, plc_lock=self.plc_lock, global_time=self.global_time, timelock=self.timelock)


        self.threadMessager = Fake_Message(plc_data=self.plc_data, plc_lock=self.plc_lock, global_time=self.global_time, timelock=self.timelock)

        # starts those threads
        self.threadPLC.start()
        time.sleep(0.1)
        self.threadMessager.start()


if __name__ =="__main__":
    MC = MainClass()



'''PRACTICE: How to create 3 multithread. The first writes random any float from 0-2*Pi to data pool. The second  read the value and print out if it is larger or less than Pi: True/False.
The 3rd read the value, change 0-2*Pi to 0-360 degree and print out. '''