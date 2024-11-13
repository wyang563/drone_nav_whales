#!/bin/bash

# Set IP addresses and ports for each drone instance
DRONE_ID="drone1"
DRONE_IP="10.31.130.102"  # Replace with actual IP address of Drone 1
DRONE_PORT=8000
DRONE_OTHER_ADDRESSES="10.31.130.102:8009"

python3 start_drone.py --drone_id $DRONE_ID --server_ip $DRONE_IP --server_port $DRONE_PORT --other_addresses $DRONE_OTHER_ADDRESSES
