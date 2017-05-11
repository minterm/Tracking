#!/usr/bin/python

# rot_split.py: allow gpredict to control GH RT-21 Az-El rotor controller
# Do not manually run this script. Run start_rotor.sh.
# Written for UCLA's ELFIN mission <elfin.igpp.ucla.edu>
# By Micah Cliffe (KK6SLK) <micah.cliffe@ucla.edu>

import socket
import errno
import time

# Constants
HOST        = 'localhost'
GPORT       = 4533
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
            print "Attempt: ", attempt
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
class server_socket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket()
        else:
            self.sock = sock
        self.connected = None
        self.address   = None
    
    def setup(self, host, port, listeners=1):
        try:
            self.sock.bind((host,port))
            self.sock.listen(listeners)
            self.connected, self.address = self.sock.accept()
        except Exception as e:
            print "Error setting up server and connection."
            print e

    def acceptNew(self):
        if self.connected:
            try:
                self.connected.close()
            except Exception as e:
                print e
        try:
            self.connected, self.address = self.sock.accept()
        except Exception as e:
            print "Error accepting new connection."
            print e
    
    def receive(self):
        return str(self.connected.recv(REC_SZ))

    def respond(self, response):
        self.connected.send(response)

    def __del__(self):
        if self.connected:
            try:
                self.connected.close()
            except Exception as e:
                print e
        self.sock.close()

###############################################################################

def main():
    try:
        az       = client_socket()
        el       = client_socket()
        gpredict = server_socket()
    except Exception as e:
        print "Could not make sockets. Exiting."
        print e
        sys.exit(1)
    az.connect(HOST, azPORT)
    el.connect(HOST, elPORT)
    print "Connected to rotctld instances."
    print "Waiting to engage with Gpredict."
    gpredict.setup(HOST, GPORT)
    print "Engaged."

    while True:
        print "____Listen to Gpredict____"
        heard = gpredict.receive()
        if heard == "":
            print "Waiting to engage with Gpredict."
            gpredict.acceptNew()
            print "Engaged."
            continue
        else:
            print "Command: " + heard
        
        if heard[0] == 'p':
            get_position(gpredict, az, el, heard)
        elif heard[0] == 'P':
            set_position(gpredict, az, el, heard)
        elif heard[0] == 'q':
            print "Disengaged."
            if not RUN_FOREVER:
                break
        else:
            print "Unknown command: " + str(heard)
    print "Exiting."

def get_position(gpredict, az, el, cmd):
    print "____Get Position____"
    az.send(cmd)
    az_response = az.get_response().splitlines()[0]
    el.send(cmd)
    el_response = el.get_response().splitlines()[0]
    print "AZ: " + az_response
    print "EL: " + el_response
    response = az_response + '\n' + el_response + '\n'
    print "response: " + response
    gpredict.respond(response)

def set_position(gpredict, az, el, cmd):
    print "____Set Position____"
    cmd  = cmd.split()
    # cmd = [P, AZIMUTH, ELEVATION]
    azCtrl = cmd[0] + ' ' + cmd[1] + ' 0\n'
    az.send(azCtrl)
    elCtrl = cmd[0] + ' ' + cmd[2] + ' 0\n'
    el.send(elCtrl)
    print "Commands sent:"
    print "AZ:\n" + azCtrl
    print "EL:\n" + elCtrl
    az_resp = az.get_response()
    el_resp = el.get_response()
    print "Responses:"
    print "AZ: " + az_resp
    print "EL: " + el_resp
    if az_resp == el_resp and az_resp == "RPRT 0\n":
        pass
    else:
        print "HAMLIB ERROR.\n" + az_resp + el_resp
    gpredict.respond(az_resp)


###############################################################################
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nExiting.\n"
