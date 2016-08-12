# Tracking
Python and Bash scripts that allow Gpredict (on Linux) to control the Green 
Heron RT-21 Az-El rotor controller for satellite tracking.

Gpredict uses Hamlib to interface with a rotor controller. It has information
for azimuth and elevation. The RT-21 Az-El rotor controller by Green Heron is 
basically two RT-21s in the same casing, so GPredict will not work. This is 
an interface that intercepts the GPredict signals, splits them into az
and el, and sends them to the correct controllers. In addition, it sends the
responses to Gpredict.

To set up Gpredict: go to Edit->Preferences->Interfaces->Rotators. A rotator 
configuration must be made, declaring min/max az and el for the rotor, and the
port on the computer to send commands to. By default this port is 4533 (the 
port that Hamlib by default listens on). This is where rot_split.py intercepts 
the commands. rot_split.py uses 4533, but this can be edited if you want to
use a different port. The Bash script creates two instances of rotctld on 
ports 4535 and 4537. One for the az part of the controller and one for the el.

TO RUN:
Just run start_rotor.sh with root permissions and engage on Gpredict.

TO STOP:
CTRL-C. It's not pretty but it works.
