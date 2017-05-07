#!/bin/bash
#
# This script helps find which USB device is az and which is el

for sysdevpath in $(find /sys/bus/usb/devices/usb*/ -name dev); do
    (
        syspath="${sysdevpath%/dev}"
        devname="$(udevadm info -q name -p $syspath)"
        [[ "$devname" == "bus/"* ]] && continue
        eval "$(udevadm info -q property --export -p $syspath)"
        [[ -z "$ID_SERIAL" ]] && continue
        #echo "/dev/$devname - $ID_SERIAL"
        if [ $ID_SERIAL = "FTDI_FT232R_USB_UART_AI02R1BA" ]
        then
            az="/dev/$devname"
            echo "azimuth:   $az"
        elif [ $ID_SERIAL = "FTDI_FT232R_USB_UART_AI02R1CX" ]
        then
            el="/dev/$devname"
            echo "elevation: $el"
        fi
    )
done
