#!/bin/bash

# start_rotor.sh: allow gpredict to control GH RT-21 Az-El rotor controller
# Written for UCLA's ELFIN mission <elfin.igpp.ucla.edu>
# By Micah Cliffe (KK6SLK) <micah.cliffe@ucla.edu>
#
# INSTRUCTIONS: 
# Change device number (number after -r argument of rotctld) to the port 
# numbers of the connect azimuth and elevation controllers.
# Run this as root. You do not manually need to run rotctld or rot_split.py. 
# Under "Antenna Control" in Gpredict engage on a rotator device with 
# the proper az/el settings and port 4533.
# To stop this script, CTRL-C.
# 
# REQUIREMENTS:
# Python 2
# Hamlib
#
# TROUBLESHOOTING:
# Run as root. Make sure rot_split.py and start_rotor.sh have the correct paths 
# at the top, are in the same folder, and have execute permissions. 

# kill rotctld instances when done
trap 'kill $(jobs -p)' EXIT

# spawn az
rotctld -m 405 -s 9600 -C min_az=-5,max_az=360,min_el=0,max_el=0 -t 4535 -r /dev/ttyUSB0 &

# spawn el
rotctld -m 405 -s 9600 -C min_az=0,max_az=0,min_el=-5,max_el=180 -t 4537 -r /dev/ttyUSB1 &

# python script
./rot_split.py
