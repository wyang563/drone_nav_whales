from client import DroneClient
from server import DroneServer
import threading
import argparse
import time
import signal

def start_drone(drone_id, server_ip, server_port, other_addresses):
    # Start the server in a separate thread
    drone_server = DroneServer(drone_id, server_ip, server_port)
    signal.signal(signal.SIGINT, drone_server.stop_server)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, drone_server.stop_server) # Handle termination signal
    threading.Thread(target=drone_server.start_server).start()
    # Client instance to send commands to other drones
    drone_client = DroneClient(drone_id, other_addresses)

    return drone_client

parser = argparse.ArgumentParser(description="Drone communication system")
parser.add_argument('--drone_id', type=str, required=True, help="ID of the drone")
parser.add_argument('--server_ip', type=str, required=True, help="IP address of this drone's server")
parser.add_argument('--server_port', type=int, required=True, help="Port of this drone's server")
parser.add_argument('--other_addresses', type=str, required=True, help="Comma-separated list of other drone IP:port pairs (e.g., '192.168.1.11:8002,192.168.1.12:8003')")
args = parser.parse_args()

# Parse other_addresses into a list of tuples
other_addresses = []
for addr in args.other_addresses.split(','):
    ip, port = addr.split(':')
    other_addresses.append((ip, int(port)))

drone_client = start_drone(args.drone_id, args.server_ip, args.server_port, other_addresses)
if drone_client.drone_id == "drone1":
    time.sleep(10)
    location = "0, 0, 0"
    drone_client.send_fly_to_command(f"Location of Drone {location}".format(args.drone_id))
    time.sleep(10)