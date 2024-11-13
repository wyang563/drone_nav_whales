from client import DroneClient
from server import DroneServer
import threading


def start_drone(drone_id, server_ip, server_port, other_addresses):
    # Start the server in a separate thread
    drone_server = DroneServer(drone_id, server_ip, server_port)
    threading.Thread(target=drone_server.start_server).start()

    # Client instance to send commands to other drones
    drone_client = DroneClient(drone_id, other_addresses)

    return drone_client

other_addresses = []
server_port = ""
server_ip = "172.31.130.226 18.13.47.13 172.22.254.13"
drone_id = "drone1"
start_drone(drone_id, server_ip, server_port, other_addresses)
