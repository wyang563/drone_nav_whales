import socket
import threading
import sys
from DRONE import drone_controller

class DroneServer:
    def __init__(self, drone, drone_id, ip, port, loop):
        self.drone = drone
        self.drone_id = drone_id
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))  # Bind to specific IP and port
        self.server_socket.listen(5)
        self.loop = loop
        self.threads = []

    def handle_connection(self, client_socket):
        data = client_socket.recv(1024).decode()
        command, data = data.split('|')
        
        if command == "fly-to":
            displacement, speed = data.split(';')
            print(f"Drone {self.drone_id} flying to displacement: {displacement} at speed: {speed}")
            dx, dy, dz = displacement.split(',')
            # convert values
            dx, dy, dz = float(dx), float(dy), float(dz)
            speed = float(speed)
            self.loop.run_until_complete(drone_controller.move_drone_by_meters(self.drone, dx, dy, dz, speed))
            print("Drone finished fly-to operation")
        
        elif command == "set-velocity":
            forward_speed, right_speed, down_speed, yaw_speed, K, yaw_K = data.split(';')
            print(f"Drone {self.drone_id} setting velocity to: {forward_speed}, {right_speed}, {down_speed}, {yaw_speed}")
            forward_speed, right_speed, down_speed, yaw_speed, K, yaw_K = float(forward_speed), float(right_speed), float(down_speed), float(yaw_speed), float(K), float(yaw_K)
            self.loop.run_until_complete(drone_controller.move_drone_by_velocity(self.drone, forward_speed, right_speed, down_speed, yaw_speed, K, yaw_K))
            print("Drone finished set-velocity operation")
            
        client_socket.close()

    def start_server(self):
        try:
            self.running = True
            print(f"Drone {self.drone_id} server started on {self.ip}:{self.port}")
            while self.running:
                try:
                    client_socket, _ = self.server_socket.accept()
                    thread = threading.Thread(target=self.handle_connection, args=(client_socket,), daemon=True)
                    self.threads.append(thread)
                    thread.start()
                except OSError:
                    break
        except Exception as e:
            print(f"server error: {e}")
        finally:
            self.server_socket.close()

    def stop_server(self, signum=0, frame=0):
        print("Shutting down server...")
        self.running = False
        self.server_socket.close()
        for thread in self.threads:
            if thread.is_alive():
                thread.join()

