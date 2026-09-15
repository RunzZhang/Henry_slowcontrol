The active source files are located in the slowcontrol_reconstruct directory.

The system runs on two main programs: Henry_background.py and Henry_GUI.py.
Henry_background.py is a daemon that continuously acquires physical data from the detector, detects and broadcasts alarms, and writes the data to a MySQL database.
These functions must run 24/7 to satisfy the requirement of uninterrupted data collection. To handle unexpected crashes and power outages, the program is launched by BKGcron_init.sh, which is invoked by the Linux crontab. BKGcron_init.sh restarts the program after an unexpected crash, while crontab ensures it is relaunched when the system reboots following a power recovery.
Henry_background.py also contains an UpdateServer class that communicates with Henry_GUI.py. This isolates the human interface from the continuously running data pipeline, preserving the stability of the daemon.
Henry_GUI.py provides a multi-tab graphical interface for manual control of instrument states (valves, heaters, alarms). It covers over 30+ instruments and supports display customization such as expanding/collapsing widgets and switching between subsystems.
The remaining packages define the function classes imported by the two main programs.
