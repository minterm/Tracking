#!/usr/bin/python

# rot_split.py: allow gpredict to control GH RT-21 Az-El rotor controller
# Do not manually run this script. Run start_rotor.sh.
# Written for UCLA's ELFIN mission <elfin.igpp.ucla.edu>
# By Micah Cliffe (KK6SLK) <micah.cliffe@ucla.edu>
# Edited by Alexander Gonzalez (KM6ISP) <gonzalezalexander1997@gmail.com>

# Interface with GPredict removed. Azimuth and elevation come from custom tracking script (nostradamus.py) that uses PyEphem.

import socket
import errno
import time
import nostradamus

# Constants
HOST        = 'localhost'
azPORT      = 4535
elPORT      = 4537
REC_SZ      = 1024
RUN_FOREVER = True

###############################################################################
class client_socket:
    def __init__(self, sock=None):
        self.maxRetry  = 5
        self.retryTime = 1
        if sock is None:
            self.sock = socket.socket()
        else:
            self.sock = sock

    def connect(self, host, port):
        for attempt in range(self.maxRetry):
            try:
                self.sock.connect((host,port))
            except EnvironmentError as e:
                if e.errno == errno.ECONNREFUSED:
                    time.sleep(self.retryTime)
                else:
                    raise
            else:
                break
        else:
            raise RuntimeError("Maximum number of unsuccessful attempts reached")

    def send(self, msg):
        self.sock.send(msg)

    def get_response(self):
        return self.sock.recv(REC_SZ)
    
    def __del__(self):
        self.sock.close()

###############################################################################

def main():

#Creates sockets for az and el of rotor controller
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

#initialize nostradamus 
    n = nostradamus.Predictor()
    n.updateTLEs()
    
    while True:
        satellite = raw_input("Which satellite would you like to track? ")
        valid = n.addSatellite(satellite)
        if(valid):
            break
        else:
            #check if spelling is correct or if satellite is in tle.txt
            print "Please enter valid satellite." 
    while True:
        valid_options = ['p', 'P', 'q','Q']
        selection = raw_input("Enter p to get current position, P to track satellite, Q to park, q to quit: ")
        if selection not in valid_options:
            print "Unknown command. Please enter a valid command."
        else:
            break
    print "\nSTATION: " + n.getStation()
    print "SATELLITES: " + str(n.getSatellites())


#NOTE: add frequency track.
#NOTE: add ability to change satellites during script
    while True:
        print "\nListening to Nostradamus...\n"
        
#Begins nostradamus tracker (i.e. gets azimuth and elevation of chosen satellite. For more info see nostradamus.py)
        pos = n.position(satellite)
        n.loadTLE(satellite)
#takes azimuth and elevation from nostradamus and packs it into a command
        pos = str(pos).strip('()')
        rotorcmd = selection + ' , ' + pos
#Just for checking that azimuth and elevation make sense (reference gpredict). Can comment out whenever not needed.         
        tempcmd =  rotorcmd.split(',')
        check_az = '%.2f' % float(tempcmd[1])
        check_el = '%.2f' % float(tempcmd[2])

        
        print "Acquiring Target: %s " % satellite
        print "AZ: " + str(check_az)
        print "EL: " + str(check_el)
#different actions depending on user selection

        #Entering 'q' quits the application
        if selection == 'q':
            print "\nSHUTTING DOWN DEATHSTAR."
            break
        
        #Entering 'p' returns the current position of the array
        elif selection == 'p':
            get_position(az, el, rotorcmd)
            break
        #Entering 'P' begins tracking of the chosen satellite
        #RPRT 0 = successful command, RPRT -1 = failed command
        elif selection == 'P':
            valid_set = set_position(az, el, rotorcmd)
            if not valid_set:
                print "%s out of range. Exiting." % satellite
                break
        #Entering anything else prompts user to make valid selection
        elif selection == 'Q':
            print "Parking the deathstar..."
#NOTE:      ./rot_park.py
        else:
            print "Unknown command: " + selection
            print "I think you broke me. Exit I guess? "
        #~10s gives a tolerance of about 3-4 degrees

        time.sleep(10)


def get_position(az, el, cmd):
    print "\nCurrent superlaser position...\n "
    az.send(cmd)
    az_response = az.get_response().splitlines()[0]
    el.send(cmd)
    el_response = el.get_response().splitlines()[0]
    print "AZ: " + az_response
    print "EL: " + el_response
    response = az_response + '\n' + el_response + '\n'
    print "response: " + response

def set_position(az, el, cmd):
    print "\nAIMING SUPERLASER..."
    cmd  = cmd.split(',')
    # cmd = [P, AZIMUTH, ELEVATION]
    azCtrl = cmd[0] + ' ' + cmd[1] + ' 0\n'
    az.send(azCtrl)
    elCtrl = cmd[0] + ' ' + cmd[2] + ' 0\n'
    el.send(elCtrl)
    print "Commands sent."
    print "AZ: " + azCtrl
    print "EL: " + elCtrl
    az_resp = az.get_response()
    el_resp = el.get_response()
    print "CHECKING SUPERLASER..."
    print "AZ: " + az_resp
    print "EL: " + el_resp
    if az_resp == el_resp and az_resp == "RPRT 0\n":
        pass
    else:
        print "SUPERLASER MALFUNCTION."  
        return 0

###############################################################################
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nExiting.\n"
