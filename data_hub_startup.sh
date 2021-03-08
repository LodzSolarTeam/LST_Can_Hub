sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up
python3 receiver.py -u ws://192.168.43.117:55201/api/WebSocket
