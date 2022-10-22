#!/bin/bash
# Make sure the script runs with super user priviliges.
[ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"
# Load the kernel module.
modprobe vcan
# Create the virtual CAN interface.
ip link add dev vcan0 type vcan
# Bring the virutal CAN interface online.
ip link set up vcan0

cansend vcan0 302#FFFF
cansend vcan0 584#0000FF
cansend vcan0 610#E
cansend vcan0 483#FFFFFFFF
cansend vcan0 482#FFFFFFFF
cansend vcan0 481#FFFFFFFF
cansend vcan0 480#FFFFFFFF
cansend vcan0 141#FFFFFFFF
cansend vcan0 618#FFFFFFFF
