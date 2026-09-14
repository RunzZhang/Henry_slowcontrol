"""This is a slowcontrol related document to train how to code the slowcontrol and GUI
Henry_background.py Chapter 3
This chapter is about how to make 2 code communicate with other. i.e send and receive data each other
The application is simple, GUI send command like open/close valve to Background code, and background code send real-time
to GUI to display

3.1 Background side, server:py
I just attached the class here, because you need to fetch data every like 1 second. But this should be much simplified than
actually code
class UpdateServer(threading.Thread):
    def __init__(self):
        super().__init__()

        self.host = '127.0.0.1' # localhost
        self.port = 6666 # any port non-occupied, but need to be same as client's
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print("Server listening on {host}:{port}".format(host=self.host, port = self.port))
        # try to build server
        self.period = 1

        self.data_package = pickle.dumps({data:"background code says hi!"})

    def run(self):
        self.Running = True
        while self.Running:# keep the code running all the time
                conn, addr = self.server_socket.accept()

                print(f"Connection from {addr}")

                while True:

                    received_data = pickle.loads(self.receive_data(conn)) # receive data from client.
                    print(received_data) # print the received data
                    #pack data and send out
                    self.pack_data(conn)
                    time.sleep(self.period)  # Sleep for 1 seconds before sending data again

    def pack_data(self, conn):  # Basically, this function is just chunk the data when the data is too huge for transfer directly
        data_transfer = self.data_package

        # Send JSON data to the client
        conn.sendall(len(data_transfer).to_bytes(4, byteorder='big'))

        # Send the serialized data in chunks
        for i in range(0, len(data_transfer), 1024):
            chunk = data_transfer[i:i + 1024]
            conn.sendall(chunk)



3.2 GUI side: Client.py
class UpdateClient(QtCore.QThread):
    def __init__(self):
        super().__init__()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1' # same address as server
        self.port = 6666 # same port
        self.Running=False
        self.period = 1
        print("client is connecting to the socket server")
        self.receive_dic = copy.deepcopy({data:"This is just a empty directory"}})

    @QtCore.Slot()
    def run(self):
        self.Running = True

        while True:
            try:
                self.client_socket.connect((self.host, self.port))

                while True:
                    # send commands
                    self.send_commands()
                    print("client commands sent")
                    received_data = self.receive_packed_data()

                    # Deserialize pickle data to a dictionary
                    data_dict = pickle.loads(received_data)
                    print(data_dict)


    def receive_packed_data(self): # this is put RECEIVED chunked data (FROM server) back to directory
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

    def pack_data(self, conn): # this is put client data into chunked data so that it can be sent to server
        data_transfer = pickle.dumps(self.commands)

        # Send JSON data to the client
        conn.sendall(len(data_transfer).to_bytes(4, byteorder='big'))

        # Send the serialized data in chunks
        for i in range(0, len(data_transfer), 1024):
            chunk = data_transfer[i:i + 1024]
            conn.sendall(chunk)



PRACTICE: use the above codes, debug to make them run.
Or can you make the data content dynamically? For example, send the current datetime?
        """
