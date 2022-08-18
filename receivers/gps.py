import asyncio
import glob
import io
import logging
import time
import pynmea2
import serial

from car import Car

GPS_BAUD_RATE = 38400

GPS_INTERFACE = lambda: '' if not glob.glob('/dev/gps*') else glob.glob('/dev/gps*')[0]

def gps_receiver(car: Car):
    # connection loop
    while True: 
        try:
            logging.info(f"Initialization")
            ser = serial.Serial(GPS_INTERFACE(), baudrate=GPS_BAUD_RATE, timeout=0.5)
            sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
            logging.info(f"Successfully initialized")
            while True:
                try:
                    line = sio.readline()
                    if len(line) == 0 or line[0] == '\n':
                        continue
                    msg = pynmea2.parse(line)
                    car.fill_gps_data(msg)
                except pynmea2.ParseError as e:
                    logging.warning(f"Data parsing error: {e}")
        except serial.SerialException as e:
            logging.warning(f"Connection exception {e}. Sleeping 3 seconds")
            time.sleep(3)
        except Exception as e:
            logging.warning(f"{e}")
            time.sleep(0)
