import io
import logging
import time
import pynmea2
import serial

from src.car import Car

finish_line = (50.9888409, 5.2552022)
GPS_BAUD_RATE = 38400


def gps_receiver(car: Car):
    logging.info("Initialization")
    # connection loop
    while True:
        try:
            logging.info(f"Connecting")
            ser = serial.Serial("/dev/ttyUSB_GPS", baudrate=GPS_BAUD_RATE, timeout=3)
            sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
            logging.info(f"Connected")
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
