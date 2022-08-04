import asyncio
import io
import logging
import struct

import pynmea2
import serial
from serial import SerialBase

from car import Car

GPS_BAUD_RATE = 38400


async def gps_receiver(car: Car, port: SerialBase):
    while True:  # connection loop
        try:
            logging.info(f"GPS: Initialization")
            ser = serial.Serial(port, baudrate=GPS_BAUD_RATE, timeout=5.0)
            #noinspection PyTypeChecker
            sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
            logging.info(f"GPS: Successfully initialized")
            while True:  # data flow loop
                try:
                    line = sio.readline()
                    msg = pynmea2.parse(line)
                    
                    if msg.sentence_type == 'RMC':
                        if msg.is_valid:
                            gps_datetime = msg.datetime
                            print(gps_datetime.year, gps_datetime.month, gps_datetime.day, gps_datetime.hour, gps_datetime.minute, gps_datetime.second)
                            car.Gps.dateYear = struct.pack("H", gps_datetime.year)
                            car.Gps.dateMonth = struct.pack("B", gps_datetime.month)
                            car.Gps.dateDay = struct.pack("B", gps_datetime.day)
                            car.Gps.timeHour = struct.pack("B", gps_datetime.hour)
                            car.Gps.timeMin = struct.pack("B", msg.datetime.minute)
                            car.Gps.timeSec = struct.pack("B", gps_datetime.second)
                            logging.info("GPS datetime inited")
                    elif msg.sentence_type == 'GGA':
                        if msg.is_valid:
                            car.Gps.latitude = struct.pack('d', msg.latitude) 
                            car.Gps.latitudeDirection = struct.pack('B', ord(msg.lat_dir))
                            car.Gps.longitude = struct.pack('d', msg.longitude)
                            car.Gps.longitudeDirection = struct.pack('B', ord(msg.lon_dir))
                            car.Gps.altitude = struct.pack('d', msg.altitude)
                            car.Gps.satellitesNumber = struct.pack('B', int(msg.num_sats))
                            car.Gps.quality = struct.pack('b', msg.gps_qual)
                            logging.info("GPS localisation inited")
                    elif msg.sentence_type == 'VTG':
                        car.Gps.speedKnots = struct.pack('d', msg.spd_over_grnd_kts)
                        car.Gps.speedKilometers = struct.pack('d', msg.spd_over_grnd_kmph)
                        logging.info("GPS speeed inited")

                    await asyncio.sleep(0)
                except pynmea2.ParseError as e:
                    logging.info(f"GPS: Data parsing error: {e}.")
        except serial.SerialException as e:
            logging.warning(f"GPS: Connection exception {e}. Sleeping for 3 seconds")
            await asyncio.sleep(3)
        except Exception as e:
            logging.warning(f"GPS: {e}")
            await asyncio.sleep(1)