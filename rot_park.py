#!/usr/bin/python

# park.py: park the array using the GH RT-21 Az-El rotor controller
# Do not manually run this script. Run park.sh.
# Written for UCLA's ELFIN mission <elfin.igpp.ucla.edu>
# By Micah Cliffe (KK6SLK) <micah.cliffe@ucla.edu>

import socket
from rot_split import client_socket, HOST, azPORT, elPORT

AZ_POS      = "135"
EL_POS      = "90"

###############################################################################
def main():
    try:
        az       = client_socket()
        el       = client_socket()
    except Exception as e:
        print "Could not make sockets. Exiting."
        print e
        sys.exit(1)
    az.connect(HOST, azPORT)
    el.connect(HOST, elPORT)
    print "Connected to rotctld instances."
    # Give commands now
    print("Current Position: " + str(get_position(az, el)))
    print("Setting Position: " + AZ_POS + " " + EL_POS)
    set_position(az, el)
    print("Command sent.")

def get_position(az, el):
    az.send("p")
    az_response = az.get_response().splitlines()[0]
    el.send("p")
    el_response = el.get_response().splitlines()[0]
    response    = az_response + ' ' + el_response + ' '
    return response

def set_position(az, el):
    # cmd = [P, AZIMUTH, ELEVATION]
    azCtrl = "P" + ' ' + AZ_POS + ' 0\n'
    az.send(azCtrl)
    elCtrl = "P" + ' ' + EL_POS + ' 0\n'
    el.send(elCtrl)
    az_resp = az.get_response()
    el_resp = el.get_response()
    if az_resp == el_resp and az_resp == "RPRT 0\n":
        pass
    else:
        print("HAMLIB ERROR.\n", az_resp, el_resp)

###############################################################################
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nExiting.\n"
