How to run the reconstructed function
$ reconstruct$
$chmod +x BKG_init.sh$
$crontab -e$ and uncomment the BKG_init.sh part

crontab -e

@reboot export DISPLAY=:0 && /home/hep/PycharmProjects/pythonProject/runze/UCSB_TS_slowcontrol/UCSB_reconstruct/BKG_init.sh &

NOTE: config.json is for the capacitor. It is used to create the offsets via CAPDAC, as well as set the differential mode. Does not need to be adjusted (for now)
