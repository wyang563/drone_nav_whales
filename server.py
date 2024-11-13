import socket
import threading

class DroneServer:
    def __init__(self, drone_id, ip, port):
        self.drone_id = drone_id
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))  # Bind to specific IP and port
        self.server_socket.listen(5)

    def handle_connection(self, client_socket):
        data = client_socket.recv(1024).decode()
        command, location = data.split('|')
        
        if command == "fly-to":
            print(f"Drone {self.drone_id} flying to location: {location}")
            # Placeholder for flight logic

        client_socket.close()

    def start_server(self):
        print(f"Drone {self.drone_id} server started on {self.ip}:{self.port}")
        while True:
            client_socket, _ = self.server_socket.accept()
            threading.Thread(target=self.handle_connection, args=(client_socket,)).start()


