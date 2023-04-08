import io
import logging
import time
import pynmea2
import serial

from src.car import Car
from src.frames import EagleTwoProxy

finish_line = (50.9888409, 5.2552022)
GPS_BAUD_RATE = 38400


def gps_receiver(frameProxy: EagleTwoProxy):
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
                    fill_gps_data(frameProxy, msg)
                except pynmea2.ParseError as e:
                    logging.warning(f"Data parsing error: {e}")
        except serial.SerialException as e:
            logging.warning(f"Connection exception {e}. Sleeping 3 seconds")
            time.sleep(3)
        except Exception as e:
            logging.warning(f"{e}")
            time.sleep(0)


def fill_gps_data(frameProxy, msg):
    if msg.sentence_type == 'GGA':
        data: pynmea2.GGA = msg
        if msg.is_valid:
            frameProxy.update_signal('GPS_LATITUDE', data.latitude)
            frameProxy.update_signal('GPS_LATITUDE_DIRECTION', data.lat_dir)
            frameProxy.update_signal('GPS_LONGITUDE', data.longitude)
            frameProxy.update_signal('GPS_LONGITUDE_DIRECTION', data.lon_dir)
            frameProxy.update_signal('GPS_ALTITUDE', data.altitude)
            frameProxy.update_signal('GPS_QUALITY', data.gps_qual)
            logging.debug("GGA gathered")
        else:
            logging.warning("GGA is not valid")
    if msg.sentence_type == 'RMC':
        data: pynmea2.RMC = msg
        if msg.is_valid:
            frameProxy.update_signal('GPS_LATITUDE', data.latitude)
            frameProxy.update_signal('GPS_LATITUDE_DIRECTION', data.lat_dir)
            frameProxy.update_signal('GPS_LONGITUDE', data.longitude)
            frameProxy.update_signal('GPS_LONGITUDE_DIRECTION', data.lon_dir)
            frameProxy.update_signal('GPS_SPEED_KILOMETERS', data.spd_over_grnd)
            logging.debug("RMC gathered")
        else:
            logging.warning("RMC is not valid")
