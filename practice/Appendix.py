'''This is appendix
I think I won't show much code here. But I will introduce other functions of the slowcontrol code
I don't show the code because they should be different language. i.e. Linux bash or Mysql.  But hopefully finally I will direct you to an elog: either SBC or
ucsb elog
1. Auto startup of Background code
in bash script: sudo crontab -e
@reboot BKGcron-init.sh
You may need to make the code into executatable before it can take effects.
To do this:
sudo chmod +X
So BKGcron_init.sh is the bash code to set python environment and run the python code. Besides, if anything trigger the exit code,
The BKGcron_init.sh will make background code running again. that is what we want, it runs 24/7 unless we comment the line out and reboot the computer.
BKG_init.sh is a terminal version. Basically it has same function but for code debugging. i.e, you can run it in the terminal to see the errors/outputs while BKGcron_init
won't have any outputs.

To end the process, you need to run ps aux | grep BKG
and kill the sh code. otherwise, Henry_background code will keep restarting after you kill it.
Of course, you also need to run ps aux | grep python to kill the Henry_background.py after the above step to finally terminate it.


2. Mysql settings, mirroring and data display
link:


3.PLC coding




4. Lakeshore coding???
'''