# LST_CanHub

## Table of contents

1. [Setup](#setup)
2. [Views for data](#views-for-data)
3. [Autorun script](#autorun-script)
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
$HOME/lst_canhub_py/new
```


## Autorun script


Project should start automatically with Raspberry.

For that, there should be a script:

```bash
/etc/init.d/can_receiver_startup
```

Available commands
```bash
service can_receiver_startup - list process
service can_receiver_startup start
service can_receiver_startup stop
```

