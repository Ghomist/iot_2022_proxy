# wait for system boot
sleep 15s

# set tty_usb0
sudo modprobe option
sudo sh -c 'echo " 1782 4d11" > /sys/bus/usb-serial/drivers/option1/new_id'
# remove lock file
sudo rm /var/lock/LCK..ttyUSB0

# kill last minicom
pkill -f minicom

# open screen
pkill -f "SCREEN -dmS minic"
screen -dmS minic

# input command
screen -S minic -p 0 -X stuff "minicom^M"
sleep 1s
screen -S minic -p 0 -X stuff "AT+GTUSBMODE=32^M"
sleep 1s
screen -S minic -p 0 -X stuff "AT+CGDCONT=2,\"IP\",\"CMNET\"^M"
sleep 1s
screen -S minic -p 0 -X stuff "AT+GTRNDIS=1,2^M"

# start mqtt proxy
# screen -dmS proxy
# screen -S proxy -p 0 -X stuff "cd ~/SmartElectricPile-Proxy^M"
# screen -S proxy -p 0 -X stuff "python main.py"

# exit
# pkill -f minicom
# pkill -f "SCREEN -dmS minic"

# end
echo done!