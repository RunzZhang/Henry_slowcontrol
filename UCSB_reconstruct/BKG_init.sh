#!/bin/bash

PATH=/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/hep/.local/bin:/home/hep/bin

if [ -n "$DISPLAY" ]; then
    # Check if the display is a physical desktop display
    if [[ "$DISPLAY" == :0 ]]; then
        # Launch the application if a display is connected
        source ~/conda_init.sh
        source /home/hep/miniforge3/bin/activate slowcontrol
        which python
        while true; do
        cd /home/hep/PycharmProjects/pythonProject/Henry_slowcontrol/UCSB_reconstruct
        python ./Henry_background.py
        sleep 2
        done
        echo "Python application started." > /home/hep/bkgshlog.txt
    else
        echo "No display connected. Skipping application launch." > /home/hep/bkgshlog.txt
    fi
else
    echo "DISPLAY variable is not set. Exiting."
    exit 1

fi

