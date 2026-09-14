import socket
import pickle
import time

def run_server():
    # Server configuration
    HOST = '127.0.0.1'
    PORT = 12345

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen()

    print(f"Server listening on {HOST}:{PORT}")

    while True:
        try:
            # Accept a connection from a client
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")

            # Set a timeout for socket operations to 10 seconds
            conn.settimeout(10)

            while True:
                # Create a sample dictionary to send
                data_to_send = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

                # Serialize the dictionary using pickle
                serialized_data = pickle.dumps(data_to_send)

                # Send serialized data to the client
                try:
                    conn.sendall(serialized_data)
                    print("Data sent to client. Original size:", len(data_to_send))
                except BrokenPipeError:
                    print("Client disconnected. Waiting for the next connection...")
                    conn.close()  # Sleep for 1 second before sending data again
                    break
                time.sleep(1)


        except socket.timeout:
            print("Connection timed out. Waiting for the next connection...")

        except ConnectionResetError:
            print("Client disconnected.")
            conn.close()

if __name__ == "__main__":
    run_server()
