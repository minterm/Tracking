#!/bin/bash

# start_rotor.sh: allow gpredict to control GH RT-21 Az-El rotor controller
# Written for UCLA's ELFIN mission <elfin.igpp.ucla.edu>
# By Micah Cliffe (KK6SLK) <micah.cliffe@ucla.edu>

# kill rotctld instances when done
trap 'kill $(jobs -p)' EXIT

# spawn az
rotctld -m 405 -s 4800 -C min_az=-5,max_az=360,min_el=0,max_el=0,timeout=5000,retry=2 -t 4539 -r /dev/ttyUSB2 &

# spawn el
rotctld -m 405 -s 4800 -C min_az=-5,max_az=185,min_el=0,max_el=0,timeout=5000,retry=2 -t 4537 -r /dev/ttyUSB0 &

# python script
./rot_split.py
