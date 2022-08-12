import asyncio
import io
import logging
import struct
import datetime

import pynmea2
import serial
from serial import SerialBase

from car import Car

GPS_BAUD_RATE = 38400


async def gps_receiver(car: Car, port: SerialBase, set_mock_date: bool = True):

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
            ser = serial.Serial(port, baudrate=GPS_BAUD_RATE, timeout=0.5)
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
                            logging.info("[GPS] GGA gathered")
                        else:
                            logging.info("[GPS] GGA is not valid")
                    if msg.sentence_type == 'RMC':
                        if msg.is_valid:
                            car.Gps.latitude = struct.pack('d', msg.latitude)
                            car.Gps.latitudeDirection = struct.pack('B', ord(msg.lat_dir))
                            car.Gps.longitude = struct.pack('d', msg.longitude)
                            car.Gps.longitudeDirection = struct.pack('B', ord(msg.lon_dir))
                            car.Gps.speedKilometers = struct.pack('d', msg.spd_over_grnd)
                            logging.info("[GPS] RMC gathered")
                        else:
                            logging.info("[GPS] RMC is not valid")
                        await asyncio.sleep(1)

                except pynmea2.ParseError as e:
                    logging.warning(f"[GPS] Data parsing error: {e}")
        except serial.SerialException as e:
            logging.warning(f"[GPS] Connection exception {e}. Sleeping 3 seconds")
            await asyncio.sleep(3)
        except Exception as e:
            logging.warning(f"[GPS] {e}")
            await asyncio.sleep(0)
