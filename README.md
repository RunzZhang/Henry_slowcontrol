# Henry-SlowControl
Henry-SlowControl

The active source files are located in the UCSB_reconstruct directory. The entire project — architecture, daemon, GUI, and alarm system — was independently designed and developed by the author with the exception of capacitor readings (fdc1004_logger.py and ssp_protocol.py).

The Henry project of HydroX is measuring hydrogen solubility in liquid xenon, which requires a stable thermodynamic environment, maintained by this slow control system, which manages 30+ instruments including temperature and pressure transducers, pneumatic and solenoid valves, heaters, and photon sensors.

The system runs on two main programs: Henry_background.py and Henry_GUI.py.

Henry_background.py is a daemon that continuously acquires data from the detector, detects and broadcasts alarms, and writes data to a MySQL database. Alarms are threshold-based and broadcast via Slack. MySQL was chosen for reliable long-term storage of time-series data and compatibility with the Grafana/SeeQ visualization tools.

These functions must run 24/7 to meet the requirement of uninterrupted data collection. To handle unexpected crashes and power outages, the program is launched by BKG_init.sh, invoked by the Linux crontab: BKG_init.sh restarts the program after a crash, while crontab relaunches it after a system reboot following power recovery. The background daemon has been running continuously at UCSB for 1+ years.

Henry_background.py also contains an UpdateServer class that communicates with Henry_GUI.py, isolating the human interface from the continuously running data pipeline and preserving the stability of the daemon.

Henry_GUI.py provides a multi-tab graphical interface for manual control of instrument states (valves, heaters, alarms). It covers 30+ instruments and supports display customization, including expanding/collapsing widgets and switching between subsystems.

UCSB_reconstruct/
├── Henry_background.py       # daemon: data acquisition, alarms, DB writes
├── Henry_GUI.py               # operator interface
├── Henry_GUI_Widgets.py       # operator interface graphic design
├── Henry_env.py               # background environmental variables
├── Henry_alarm_autoload.py    # alarm pre-loading from local configuration files
├── Henry_watchdog_database.py  # alarm and MySQL protocol classes
├── BKG_init.sh          # crash/reboot recovery wrapper
└── utils/                  # auxiliary functions


