# LST_CanHub

Logs on RPI available via command 
```bash
journalctl -fu lst_can_hub.service
```

## Table of contents

1. [Setup](#setup)
2. [Views for data](#views-for-data)
3. [Scripts](#Scripts)
4. [Login to RPi](#login-to-rpi)

## Setup

Commands for configuring CAN and starting data transfer are in `data_hub_startup.sh`.

For telemetry to work:

1. Turn on hotspot with Internet connection:
    ```yaml
    Name: Eagle
    Password: 12345678
    ```
2. Turn on RPi and connect CAN to shield. 
   
Telemetry should be sent after 5 seconds.

## Views for data

Data will be available in:

- Clean data: https://lst-api-v1.azurewebsites.net/api/car/recent
- Frontend: https://white-sky-0251a6303.azurestaticapps.net

If done correctly, you will see 'clean data' with current timestamp.
Data from CAN is sent every 3 seconds to the cloud's backend.


## Login to RPi

via Ethernet connection you can use raspberrypi.local as IP otherwise please scan network

If necessary, you can login to RPi. Use:

 ```yaml
 Username: pi
 Password: raspberry
 ```

Project directory 
```bash
$HOME/LST_CAN_HUB
```


## Scripts

```bash
/lib/systemd/system/lst_can_hub.service
```

Available commands
```bash
sudo systemctl enablie lst_can_hub.service
sudo systemctl disable lst_can_hub.service
sudo systemctl restart lst_can_hub.service
sudo systemctl status lst_can_hub.service
```

