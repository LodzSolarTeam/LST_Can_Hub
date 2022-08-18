import asyncio
import logging
import random
import time

import can

from car import Car
from frames import Frames

CAN_INTERFACE = 'can0'
def can_receiver(car: Car, mock=False):
    global CAN_INTERFACE
    frames = Frames()
    while True:
        try:
            global bus, message

            if not mock:
                bus = can.interface.Bus(CAN_INTERFACE, bustype='socketcan')
                logging.info("CAN: Bus ", bus)

            while True:
                if not mock:
                    message = bus.recv(0.1)
                else:
                    arbitration_id = 1412
                    dat = [random.randint(1, 30), random.randint(25, 255), 10, 10, 10, 10, 00, 10]
                    dat = dat[0: 8]
                    message = can.Message(arbitration_id=arbitration_id,
                                          timestamp=time.time(),
                                          data=dat, extended_id=False)

                frames.save_frame(message.arbitration_id, message.data)
                car.fill_can_data(frames)
                logging.debug(f"[CAN] Messsage gathered id={message.arbitration_id}")
                time.sleep(1 if mock else 0)
        except Exception:
            logging.warning(f"CAN: Failed to configure can at `{CAN_INTERFACE}` interface")
            time.sleep(1)
