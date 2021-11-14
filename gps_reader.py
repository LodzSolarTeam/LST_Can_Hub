import glob
import io
import logging
import struct

import serial
import asyncio
import pynmea2

GPS_BAUD_RATE = 38400


class GpsReader:
    def __init__(self, gps) -> None:
        self.gps = gps

    async def start_listening(self):
        while True:  # connection loop
            try:
                ports = glob.glob('/dev/gps*')
                ser = serial.Serial(ports[0], baudrate=GPS_BAUD_RATE, timeout=5.0)
                # noinspection PyTypeChecker
                sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

                while True:  # data flow loop
                    try:
                        await asyncio.sleep(0)

                        line = sio.readline()
                        msg = pynmea2.parse(line)

                        if msg.sentence_type == 'GGA':
                            if msg.is_valid:
                                self.gps.latitude = struct.pack('d', msg.latitude)
                                self.gps.latitudeDirection = struct.pack('c', msg.lat_dir)
                                self.gps.longitude = struct.pack('d', msg.longitude)
                                self.gps.longitudeDirection = struct.pack('c', msg.lon_dir)
                                self.gps.altitude = struct.pack('d', msg.altitude)
                                self.gps.satellitesNumber = struct.pack('b', msg.num_sats)
                                self.gps.quality = struct.pack('b', msg.gps_qual)
                        elif msg.sentence_type == 'VTG':
                            self.gps.speedKnots = struct.pack('d', msg.spd_over_grnd_kts)
                            self.gps.speedKilometers = struct.pack('d', msg.spd_over_grnd_kmph)
                    except pynmea2.ParseError as e:
                        logging.info(f"[GPS_READER] Data parsing error: {e}.")
            except serial.SerialException as e:
                logging.warning(f"[GPS_READER] Connection exception {e}. Sleeping for 5 seconds")
                await asyncio.sleep(1)
            except Exception as e:
                logging.warning(f"[GPS_READER] {e}")
                await asyncio.sleep(1)