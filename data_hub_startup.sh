sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up
python3 run.py #send-board-computer=False send-cloud=True log-path=logs.log backup-path=backup.bin