#!/bin/bash

# Set IP addresses and ports for each drone instance
DRONE_ID="drone2"
DRONE_IP="127.0.0.1"  # Replace with actual IP address of Drone 1
DRONE_SERVER_PORT=8009
DRONE_PORT=14542
DRONE_OTHER_ADDRESSES="127.0.0.1:8000"

python3 run.py --drone_port $DRONE_PORT --drone_id $DRONE_ID --server_ip $DRONE_IP --server_port $DRONE_SERVER_PORT --other_addresses $DRONE_OTHER_ADDRESSES
