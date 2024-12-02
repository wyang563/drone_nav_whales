from client import DroneClient
from server import DroneServer
import threading
import argparse
import time
import signal
import asyncio
from DRONE import drone_controller
import sys

def start_drone(drone_port, drone_id, server_ip, server_port, other_addresses, loop):
    # Start the server in a separate thread
    global drone_server
    global drone
    # setup server and drone
    print("Starting drone in run...")
    drone_server = False
    drone = None
    drone = loop.run_until_complete(drone_controller.init_drone(port=drone_port))
    drone_server = DroneServer(drone, drone_id, server_ip, server_port, loop)
    # signal.signal(signal.SIGINT, drone_server.stop_server)  # Handle Ctrl+C
    # signal.signal(signal.SIGTERM, drone_server.stop_server) # Handle termination signal
    threading.Thread(target=drone_server.start_server).start()
    # Client instance to send commands to other drones
    drone_client = DroneClient(drone, drone_id, other_addresses, loop)

    return drone_client, drone_server

def shutdown_server(signum, frame):
    global drone_server
    if drone_server:
        drone_server.stop_server(signum, frame)
    else:
        print("Server instance not found")
    if drone is not None:
        drone._stop_mavsdk_server()
    asyncio.get_event_loop().stop()  # Stop the event loop
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Drone communication system")
    parser.add_argument('--drone_port', type=int, required=True, help="port drone sim is running on")
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
    drone_client, drone_server = start_drone(args.drone_port, args.drone_id, args.server_ip, args.server_port, other_addresses, loop)
    position = loop.run_until_complete(drone_controller.get_drone_position(drone_client.drone))
    print(args.drone_id + " starting position " + str(position))
    if drone_client.drone_id == "drone1":
        time.sleep(3)
        location = "10, 10, 10"
        speed = "14"
        drone_client.send_command("fly-to", location, speed)
    time.sleep(10)
    position = loop.run_until_complete(drone_controller.get_drone_position(drone_client.drone))
    print(args.drone_id + " starting position " + str(position))

if __name__ == "__main__":
    try:
        # Get the current event loop
        loop = asyncio.get_event_loop()
        signal.signal(signal.SIGINT, shutdown_server)
        signal.signal(signal.SIGTERM, shutdown_server)
        main()

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down gracefully...")
        if not loop.is_closed():
            loop.close()        