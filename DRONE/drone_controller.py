import asyncio
from mavsdk import System
import rtsp
import numpy as np
import time
import argparse
import threading

from mavsdk.offboard import OffboardError
from mavsdk.offboard import VelocityBodyYawspeed
import time 
eps = 0.000001
import signal
global command_counter 
command_counter = 0

async def init_drone(port = 14540, baud = 57600, fly_meters = 0, speed = 1, fly_mode = 'global', port_abs_path = False):
    drone = System()
    print(f"Trying to connect to drone on UDP port {port}...")
    await drone.connect(system_address=f"udp://:{port}")
    
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone on port {port}!")
            break

    print("Waiting for drone to have a global/local position estimate...")
    if fly_mode == 'global':
        async for health in drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print("-- Global position state is good enough for flying.")
                break
            
    elif fly_mode == 'local':
        print("checking local")
        async for health in drone.telemetry.health():
            if health.is_local_position_ok:
                print("-- Local position state is good enough for flying.")
                break
    else:
        print("Exisiting. No such a fly_mode {}".format(fly_mode))
        exit(9)
    

    print("-- Arming")
    if fly_meters != 0: #drone is already armed:
        await drone.action.arm()
        await drone.action.set_takeoff_altitude(fly_meters)
        print("-- Taking off")
        await drone.action.takeoff()
        await asyncio.sleep(10)
    ##########################################
    
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
              {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
    
    return drone

async def get_drone_flight_mode(drone):
    if drone is None:
        return "OFFBOARD"
    async for flight_mode in drone.telemetry.flight_mode():
            if  str(flight_mode) != 'OFFBOARD':
                print(f"Exisiting: Flight mode is: {flight_mode}")
            break
    return flight_mode

async def move_drone_by_velocity(drone,forward_speed, right_speed, down_speed, yaw_speed, K, yaw_K):
    global command_counter
    #np.save(f"outputs/velocity/{command_counter}",[forward_speed, right_speed, down_speed, yaw_speed, K, yaw_K])
    command_counter += 1
    if drone is not None:
        # print(forward_speed*K, right_speed*K, down_speed*K, yaw_speed*yaw_K)
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(forward_speed*K, right_speed*K/2, down_speed, yaw_speed*yaw_K))
    else:
        # print(forward_speed*K, right_speed*K, down_speed, yaw_speed*yaw_K)
        pass

async def move_drone_by_meters(drone, y_meters, x_meters, z_meters, speed):
    largest = max(abs(y_meters), abs(x_meters), abs(z_meters))
    if drone is not None:
        #print("in")
        if largest > 0:
            y_speed = (y_meters/largest)*speed
            x_speed = (x_meters/largest)*speed
            z_speed = (z_meters/largest)*speed
            await drone.offboard.set_velocity_body(VelocityBodyYawspeed(y_speed, x_speed, z_speed, 0.0))
            
            await asyncio.sleep(largest/speed - eps) 
            
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    else:
        await asyncio.sleep(largest/speed - eps)

async def print_status_text():
    global drone
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        print("Error")

async def stop_velocity_commands(drone):
    await drone.offboard.stop()


async def land_drone(drone):
    await drone.action.land()

async def get_drone_height(drone,area_covered_by_detected_body):
    print("drone", drone, area_covered_by_detected_body)
    if drone is not None:
        print("Fetching amsl altitude at home location....")
        async for terrain_info in drone.telemetry.home():
            absolute_altitude = terrain_info.absolute_altitude_m
            return absolute_altitude
    else:
        print(area_covered_by_detected_body, 1/area_covered_by_detected_body)
        return 1/area_covered_by_detected_body 

async def get_drone_position(drone):
    try:
        async for position_velocity in drone.telemetry.position_velocity_ned():
            local_position = {
                "north_m": position_velocity.position.north_m,
                "east_m": position_velocity.position.east_m,
                "down_m": position_velocity.position.down_m
            }
            return local_position
    except Exception as e:
        print(f"Error getting drone local position: {e}")
        return None