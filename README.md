# LST_CanHub

## Table of contents

1. [Setup](#setup)
2. [Views for data](#views-for-data)
3. [Autorun script](#autorun-script)
4. [Login to RPi](#login-to-rpi)
5. [Sending data](#sending-data)
6. [List of parameters](#list-of-parameters)



## Setup

Commands for configuring CAN and starting data transfer are in `data_hub_startup.sh`.

For telemetry to work:

1. Turn on hotspot with Internet connection:
    ```yaml
    Name: 4DS612
    Password: mTzW4snd
    ```
2. Turn on RPi and connect CAN to shield. 
   

Telemetry should be sent after 5 seconds.


## Views for data

Data will be available in:

- Clean data: https://lst-api-v1.azurewebsites.net/api/car/recent
- Frontend: https://white-sky-0251a6303.azurestaticapps.net

If done correctly, you will see 'clean data' with current timestamp.
Data from CAN is sent every 3 seconds to the cloud's backend.



## Autorun script

Project should start automatically with Raspberry.

For that, there should be a script:

```bash
/etc/init.d/can_*
```
To turn off autorun type: 
```bash
sudo update-rc.d can_* remove
```



## Login to RPi

If necessary, you can login to RPi. Use:

 ```yaml
 Username: pi
 Password: raspberry
 ```



## Sending data

Function named `create_final_message` in  `receiver.py`  is used for aggregating data before sending. It uses properties from the class *Car* in `car.py`.



## List of parameters

1. [GENERAL](#general)
2. [BATTERY](#battery)
3. [SERIAL DATA](#serial-data)
4. [LIGHTS](#lights)
5. [SOLAR](#solar)
6. [TIRES](#tires)
7. [GPS](#gps)

### GENERAL

```python
timestamp: bytearray(8)
throttlePosition: bytearray(1)
motorController: bytearray(1)
regenerationBrake: bytearray(1)
cruiseThrottle: bytearray(1)
cruiseDesiredSpeed: bytearray(1)
batteryError: bytearray(1)
engineError: bytearray(1)
driveMode: bytearray(1)
cruiseEngaged: bytearray(1)
horn: bytearray(1)
handBrake: bytearray(1)
temperatures: bytearray(4)
rpm: bytearray(2)
solarRadiance: bytearray(2)
motorTemperature: bytearray(2)
```

### BATTERY

```python
remainingChargeTime: bytearray(4)
chargerEnabled: bytearray(1)
systemState: bytearray(1)
inputOutputState: bytearray(1)
packCRate: bytearray(2)
stateOfCharge: bytearray(1)
stateOfHealth: bytearray(1)
numberOfCellsConnected: bytearray(1)
remainingEnergy: bytearray(2)
deviationOfVoltageInCells: bytearray(2)
packTemperatureMax: bytearray(1)
LMUNumberWithMaxTemperature: bytearray(1)
packTemperatureMin: bytearray(1)
LMUNumberWithMinTemperature: bytearray(1)
cellVoltageMax: bytearray(2)
cellNumberWithMaxVoltage: bytearray(1)
cellVoltageMin: bytearray(2)
cellNumberWithMinVoltage: bytearray(1)
cellAvgVoltage: bytearray(2)
packVoltage: bytearray(2)
packCurrent: bytearray(2)
warnings: bytearray(3)
errors: bytearray(4)
```

### SERIAL DATA
```python
cells_voltage: bytearray(64)
cells_temperature: bytearray(16)
```

### LIGHTS
```python
stopLights: bytearray(1)
lowBeamLights: bytearray(1)
highBeamLights: bytearray(1)
rightIndicatorLights: bytearray(1)
leftIndicatorLights: bytearray(1)
parkLights: bytearray(1)
interiorLights: bytearray(1)
emergencyLights: bytearray(1)
```

### SOLAR
```python
mpptInputVoltage: bytearray(16)
mpptInputCurrent: bytearray(16)
mpptOutputVoltage: bytearray(16)
mpptOutputPower: bytearray(16)
mpptPcbTemperature: bytearray(8)
mpptMofsetTemperature: bytearray(8)
```

### TIRES
```python
pressures: bytearray(4)
tiresTemperatures: bytearray(4)
```

### GPS
```python
dateDay: bytearray(1)
dateMonth: bytearray(1)
dateYear: bytearray(2)
timeHour: bytearray(1)
timeMin: bytearray(1)
timeSec: bytearray(1)
latitude: bytearray(8)
latitudeDirection: bytearray(1)
longitude: bytearray(8)
longitudeDirection: bytearray(1)
altitude: bytearray(8)
speedKnots: bytearray(8)
speedKilometers: bytearray(8)
satellitesNumber: bytearray(1)
quality: bytearray(1)
```