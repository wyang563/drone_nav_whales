import socket
from DRONE import drone_controller 
import asyncio 

class DroneClient:
    def __init__(self, drone, drone_id, other_addresses, loop):
        self.drone_id = drone_id
        self.other_addresses = other_addresses  # List of tuples (ip, port)
        self.loop = loop
        self.drone = drone

    def send_data(self, encoded_message):
        for ip, port in self.other_addresses:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((ip, port))  # Connect to specific IP and port
                client_socket.send(encoded_message)
                client_socket.close()
                print(f"Drone {self.drone_id} sent data to {ip}:{port}")
            except ConnectionRefusedError:
                print(f"Drone {self.drone_id} could not connect to Drone on {ip}:{port}")

    def send_command(self, command, *args):
        # data passed in as a list of parameters
        if command not in ["fly-to", "set-velocity", "land"]:
            print(f"Invalid command: {command}")
            return
        data_str = ";".join(args)
        message = f"{command}|" + data_str
        self.send_data(message.encode())
