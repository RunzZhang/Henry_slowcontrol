import threading, struct
import time
from pymodbus.client.sync import ModbusTcpClient

class ThreadA(threading.Thread):
    def __init__(self, shared_data, lock):
        super().__init__()
        self.shared_data = shared_data
        self.lock = lock
        self.PT_address = {"PT1325": 12794, "PT2121": 12796, "PT2316": 12798, "PT2330": 12800, "PT2335": 12802,
              "PT3308": 12804, "PT3309": 12806, "PT3311": 12808, "PT3314": 12810, "PT3320": 12812,
              "PT3332": 12814, "PT3333": 12816, "PT4306": 12818, "PT4315": 12820, "PT4319": 12822,
              "PT4322": 12824, "PT4325": 12826, "PT6302": 12828, 'PT1101': 12830, 'PT5304': 12834,
              "PT2343":12836}
        self.PT_dic = {"PT1325": 0, "PT2121": 0, "PT2316": 0, "PT2330": 0, "PT2335": 0,
          "PT3308": 0, "PT3309": 0, "PT3311": 0, "PT3314": 0, "PT3320": 0,
          "PT3332": 0, "PT3333": 0, "PT4306": 0, "PT4315": 0, "PT4319": 0,
          "PT4322": 0, "PT4325": 0, "PT6302": 0, "PT1101": 0, "PT5304": 0,
          "PT2343": 0}
        IP_BO = "192.168.137.11"
        PORT_BO = 502
        self.Client_BO = ModbusTcpClient(IP_BO, port=PORT_BO)

        self.Connected_BO = self.Client_BO.connect()
        print(" Beckoff connected: " + str(self.Connected_BO))

    def run(self):
        for i in range(5):
            Raw_BO_PT = {}
            for key in self.PT_address:
                Raw_BO_PT[key] = self.Client_BO.read_holding_registers(self.PT_address[key], count=2, unit=0x01)
                self.PT_dic[key] = round(
                    struct.unpack(">f", struct.pack(">HH", Raw_BO_PT[key].getRegister(0 + 1),
                                                    Raw_BO_PT[key].getRegister(0)))[0], 3)
            data_to_send = self.PT_dic
            with self.lock:
                self.shared_data.update(data_to_send)
                print(f'ThreadA sending: {data_to_send}')
            time.sleep(2)

class ThreadB(threading.Thread):
    def __init__(self, shared_data, lock):
        super().__init__()
        self.shared_data = shared_data
        self.lock = lock

    def run(self):
        for i in range(5):
            with self.lock:
                data_received = dict(self.shared_data)
                print(f'ThreadB received: {data_received}')
            time.sleep(1)

if __name__ == "__main__":
    # Create a shared dictionary and a lock
    shared_data = {}
    shared_data_lock = threading.Lock()

    # Create instances of ThreadA and ThreadB, passing the shared data and lock
    thread_a = ThreadA(shared_data, shared_data_lock)
    thread_b = ThreadB(shared_data, shared_data_lock)

    # Start both threads
    thread_a.start()
    thread_b.start()

    # Wait for both threads to finish
    thread_a.join()
    thread_b.join()
