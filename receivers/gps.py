import asyncio
import glob
import io
import logging
import struct
import datetime
import time
import pynmea2
import serial
from serial import SerialBase

from car import Car

GPS_BAUD_RATE = 38400

GPS_INTERFACE = lambda: '' if not glob.glob('/dev/gps*') else glob.glob('/dev/gps*')[0]

async def gps_receiver(car: Car, set_mock_date: bool = True):
    loop = asyncio.get_event_loop()
    if set_mock_date:
        mock_datetime = datetime.datetime(2005, 4, 2, 21, 37)
        car.Gps.dateYear = struct.pack("H", mock_datetime.year)
        car.Gps.dateMonth = struct.pack("B", mock_datetime.month)
        car.Gps.dateDay = struct.pack("B", mock_datetime.day)
        car.Gps.timeHour = struct.pack("B", mock_datetime.hour)
        car.Gps.timeMin = struct.pack("B", mock_datetime.minute)
        car.Gps.timeSec = struct.pack("B", mock_datetime.second)

    while True:  # connection loop
        try:
            logging.info(f"GPS: Initialization")
            ser = serial.Serial(GPS_INTERFACE(), baudrate=GPS_BAUD_RATE, timeout=0.5)
            # noinspection PyTypeChecker
            sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
            logging.info(f"GPS: Successfully initialized")
            while True:  # data flow loop
                try:
                    line = sio.readline()
                    if len(line) == 0 or line[0] == '\n':
                        continue
                    msg = pynmea2.parse(line)
                    if msg.sentence_type == 'GGA':
                        if msg.is_valid:
                            car.Gps.latitude = struct.pack('d', msg.latitude)
                            car.Gps.latitudeDirection = struct.pack('B', ord(msg.lat_dir))
                            car.Gps.longitude = struct.pack('d', msg.longitude)
                            car.Gps.longitudeDirection = struct.pack('B', ord(msg.lon_dir))
                            car.Gps.altitude = struct.pack('d', msg.altitude)
                            car.Gps.satellitesNumber = struct.pack('B', int(msg.num_sats))
                            car.Gps.quality = struct.pack('b', msg.gps_qual)
                            logging.debug("[GPS] GGA gathered")
                        else:
                            logging.warning("[GPS] GGA is not valid")
                    if msg.sentence_type == 'RMC':
                            if msg.is_valid:
                                car.Gps.latitude = struct.pack('d', msg.latitude)
                                car.Gps.latitudeDirection = struct.pack('B', ord(msg.lat_dir))
                                car.Gps.longitude = struct.pack('d', msg.longitude)
                                car.Gps.longitudeDirection = struct.pack('B', ord(msg.lon_dir))
                                car.Gps.speedKilometers = struct.pack('d', msg.spd_over_grnd)
                                logging.debug("[GPS] RMC gathered")
                            else:
                                logging.warning("[GPS] RMC is not valid")

                    await loop.run_in_executor(None, time.sleep, 0)
                except pynmea2.ParseError as e:
                    logging.warning(f"[GPS] Data parsing error: {e}")
        except serial.SerialException as e:
            logging.warning(f"[GPS] Connection exception {e}. Sleeping 3 seconds")
            await loop.run_in_executor(None, time.sleep, 3)
        except Exception as e:
            logging.warning(f"[GPS] {e}")
            await loop.run_in_executor(None, time.sleep, 0)
