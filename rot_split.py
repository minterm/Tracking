#!/usr/bin/python

# rot_split.py: allow gpredict to control GH RT-21 Az-El rotor controller
# Do not manually run this script. Run start_rotor.sh.
# Written for UCLA's ELFIN mission <elfin.igpp.ucla.edu>
# By Micah Cliffe (KK6SLK) <micah.cliffe@ucla.edu>

import socket

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
        if sock is None:
            self.sock = socket.socket()
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host,port))

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
        self.sock.bind((host,port))
        self.sock.listen(listeners)
        self.connected, self.address = self.sock.accept()

    def acceptNew(self):
        self.connected, self.address = self.sock.accept()
    
    def listen(self):
        return str(self.connected.recv(REC_SZ))

    def respond(self, response):
        self.connected.send(response)

    def __del__(self):
        self.sock.close()

###############################################################################
def listen_to_gpredict(gpredict, az, el):
    print "____Listen to Gpredict____"
    heard = gpredict.listen()
    if heard != "":
        print "Command: " + heard
    if heard == "":
        print "Waiting to engage with Gpredict."
        gpredict.acceptNew()
        print "Engaged."
        listen_to_gpredict(gpredict, az, el)
    elif heard[0] == 'p':
        get_position(gpredict, az, el, heard)
    elif heard[0] == 'P':
        set_position(gpredict, az, el, heard)
    elif heard[0] == 'q':
        print "Disengaged."
        if not RUN_FOREVER:
            return
        listen_to_gpredict(gpredict, az, el)
    else:
        print "Unknown command: " + str(heard)

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
    listen_to_gpredict(gpredict, az, el)

def set_position(gpredict, az, el, cmd):
    print "____Set Position____"
    cmd  = cmd.split()
    # cmd = [P, AZIMUTH, ELEVATION]
    azCtrl = cmd[0] + ' ' + cmd[1] + ' 0\n'
    az.send(azCtrl)
    elCtrl = cmd[0] + ' ' + cmd[2] + ' 0\n'
    el.send(elCtrl)
    print "Commands sent:"
    print azCtrl
    print elCtrl
    az_resp = az.get_response()
    el_resp = el.get_response()
    if az_resp == el_resp and az_resp == "RPRT 0\n":
        pass
    else:
        print "HAMLIB ERROR.\n" + az_resp + el_resp
    gpredict.respond(az_resp)
    listen_to_gpredict(gpredict, az, el)

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
    listen_to_gpredict(gpredict, az, el)
    print "DONE"

if __name__ == "__main__":
    main()
