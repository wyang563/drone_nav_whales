import socket

class DroneClient:
    def __init__(self, drone_id, other_addresses, drone_ctrl):
        self.drone_id = drone_id
        self.other_addresses = other_addresses  # List of tuples (ip, port)
        self.drone_ctrl = drone_ctrl

    def send_fly_to_command(self, location):
        for ip, port in self.other_addresses:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((ip, port))  # Connect to specific IP and port
                message = f"fly-to|{location}"
                client_socket.send(message.encode())
                client_socket.close()
                print(f"Drone {self.drone_id} sent fly-to command to {ip}:{port}")
            except ConnectionRefusedError:
                print(f"Drone {self.drone_id} could not connect to Drone on {ip}:{port}")
