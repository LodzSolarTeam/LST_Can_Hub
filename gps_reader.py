import struct
import serial
import asyncio
from datetime import datetime
import subprocess
# import serial_asyncio

class GpsReader:
    def __init__(self, gps) -> None:
        self.gps = gps

    async def start_listening(self):
        while True:
            try:
                process = subprocess.Popen(['sudo', 'rfcomm', 'bind', '0', '00:08:F4:01:98:E5'],
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
                _, stderr = process.communicate()
                if stderr and stderr != b"Can't create device: Address already in use\n":
                    print(f"Error while binding /dev/rfcomm0 interface {stderr}. Retrying in 10 sec.")
                    continue
                ser = serial.Serial('/dev/rfcomm0', 38400, timeout=0)
                break
            except Exception as e:
                print(f"Error while establishing bluetooth connection {str(e)}. Retrying in 10 sec.")
                await asyncio.sleep(10)

        while True:
            try:
                await asyncio.sleep(0.1)
                gps_data = ser.readline()
                if not gps_data:
                    continue

                gps_array = str(gps_data)[2:-1].split(",")
                if gps_array[0][0:7] == "$GPGGA":
                    print(gps_array[2])
                    print(gps_array[4])
                    self.gps.latitude = struct.pack('d', float(0 if gps_array[2] == '' else
                        float(float(gps_array[2][0:2])) + float(float(gps_array[2][2:8]))/60
                    ))
                    self.gps.latitudeDirection = bytes(gps_array[3], "utf-8")
                    self.gps.longitude = struct.pack('d', float(0 if gps_array[4] == '' else
                        float(float(gps_array[4][1:3])) + float(float(gps_array[4][3:9]))/60
                    ))
                    self.gps.longitudeDirection = bytes(gps_array[5], "utf-8")
                    self.gps.altitude = struct.pack('d', float(0 if gps_array[9] == '' else gps_array[9]))
                    self.gps.satellitesNumber = struct.pack('b', int(0 if gps_array[7] == '' else gps_array[7]))
                    self.gps.quality = struct.pack('b', int(0 if gps_array[6] == '' else gps_array[6]))
                elif gps_array[0][0:7] == "$GPVTG":
                    self.gps.speedKnots = struct.pack('d', float(0 if gps_array[5] == '' else gps_array[5]))
                    self.gps.speedKilometers = struct.pack('d', float(0 if gps_array[7] == '' else gps_array[7]))
            except Exception as e:
                print(f"Error parsing gps data {e}")
                await asyncio.sleep(4)
