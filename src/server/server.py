import socket

from proto import message_pb2


def start_server(host='0.0.0.0', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")
    
    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection established with {address}")
        
        try:
            data = client_socket.recv(1024)  # Adjust buffer size as needed
            if not data:
                break
            
            # Decode the received protobuf message
            sensor_data = message_pb2.SensorData()
            sensor_data.ParseFromString(data)
            
            print("Received data:")
            print(f"ID: {sensor_data.id}")
            print(f"Name: {sensor_data.name}")
            print(f"Value: {sensor_data.value}")
        
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
