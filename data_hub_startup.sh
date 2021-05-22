sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up
python3 receiver.py
