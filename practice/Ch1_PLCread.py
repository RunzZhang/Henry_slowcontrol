"""This is a slowcontrol related document to train how to code the slowcontrol and GUI
--Ryan Zhang
Henry_background.py Chapter 1
1.1 PLC read
The first part is about data fetch from PLC. relating code is class PLC.ReadAll()
In ReadAll() you also have sub functions like: Read_BO()/Read_AD()/Read_LL()
Their have similar functions: read from related devices but can have different code structure which is caused from protocal.
For example, Beckhoff/Adam use modbus -> read_holding_registers();
 Lakeshore 's protocol is based on tcp socket but they provides their own package Model336;
 Liquid Leveler is just based on raw code of tcp sockets;
 One need to refer to one device's manual to get what protocol you need to use.
 Starting with Beckhoff, the basic part is :

 ###################################################################################
Raw_BO_PT = {}
for key in PT_address: ## loop around the Beckhoff devices addresses
    Raw_BO_PT[key] = Client_BO.read_holding_registers(PT_address[key], count=2, unit=0x01)
    ##read 2 words(count=2) from the begining of address of PT_address[key]

#######################################################################################
This is a scheme
address 0 1 2 3 4 5
data    2 3 7 9 3 8
then read_holding _register(2, count=2, unit=0x01) will return (7,9)

##########################################################################################
    Now one need to compose (7,9) to another number, ususally floating number.
    But the order matters, so you put two words in the order of >HH to have a new hex number and then use >f rule to transfer the hex number into
     floating number.
     Finally, you round it to 3 digits.

    PT_dic[key] = round(
        struct.unpack(">f", struct.pack(">HH", Raw_BO_PT[key].getRegister(0 + 1),
                                        Raw_BO_PT[key].getRegister(0)))[0], 3)

    Notice: in Beckhofff
#######################################################################################

"""
# example for Read one PT on pion
import struct
from pymodbus.client.sync import ModbusTcpClient

# In most recent pymodubus, unit -> slave and getRegister method -> registers
def read_BO():
    IP_BO = "10.111.19.106"

    PORT_BO = 502

    Client_BO = ModbusTcpClient(IP_BO, port=PORT_BO)
    Raw_BO_PT = {}
    PT_dic = {}
    for key in {"PT001": 12796}:
        Raw_BO_PT[key] = Client_BO.read_holding_registers({"PT001": 12796}[key], count=2, unit=0x01)
        PT_dic[key] = round(
            struct.unpack(">f", struct.pack(">HH", Raw_BO_PT[key].getRegister(0 + 1),
                                            Raw_BO_PT[key].getRegister(0)))[0], 3)

    print(PT_dic)

"""PRACTICE: How to read RTD value from Adam Module?"""


"""1.2 Write Value
Write value to PLC is similar. Generally you just using write_register(address, value, unit=0x01) 

#########################################################################################
    def Write_BO_2( address, value):
        word1, word2 = float_to_2words(value) # change a float number into 2 words
        print('words', word1, word2)
        # pay attention to endian relationship
        Raw1 = Client_BO.write_register(address, value=word1, unit=0x01) # put 1st word into 1st register
        Raw2 = Client_BO.write_register(address + 1, value=word2, unit=0x01) # and 2nd word into 2nd register

        print("write result = ", Raw1, Raw2)
#######################################
But writing can be more complicated. Since usually you need to first read status before deciding where and what value you want 
to write. Or I just want to write particular digit. 
#############################################################################################
    def WriteBase2(address): # this fetches data from a address and then change one digit to True. and write back the whole binary value
        output_BO = Read_BO_1(address)  
        input_BO = struct.unpack("H", output_BO)[0] | 0x0002 
        Raw = Client_BO.write_register(address, value=input_BO, unit=0x01)
        print("write base2 result=", Raw)
##################################################################################
PRACTICE: how to do this: if last digit is 0, write it to 1, if it is 1, write it to 0. For example, 0001 to 0000/ 0000 to 0001 """