import socket, time
import pickle

def run_client():
    # Client configuration
    HOST = '127.0.0.1'
    PORT = 12345

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            # Connect to the server
            client_socket.connect((HOST, PORT))

            while True:
                # Receive serialized data from the server
                received_data = client_socket.recv(4096)

                # Break the loop if no more data is received
                if not received_data:
                    break

                # Deserialize the data using pickle
                deserialized_data = pickle.loads(received_data)

                # Print the received dictionary
                print("Received data from server:", deserialized_data)

                # Sleep for 1 second before receiving data again
                # time.sleep(1)

        except ConnectionRefusedError:
            print("Server not available. Retrying...")
            time.sleep(1)

        except ConnectionResetError:
            print("Server disconnected.")
            client_socket.close()
            break

if __name__ == "__main__":
    run_client()
