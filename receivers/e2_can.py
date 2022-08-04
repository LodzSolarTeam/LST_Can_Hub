import asyncio
import logging
import random
import time

import can

from car import Car
from frames import Frames


async def can_receiver(car: Car, can_interface, mock=False):
    frames = Frames()
    while True:
        try:
            global bus, message

            if not mock:
                logging.info(f"CAN: Configuring can bus at `{can_interface}` interface.")
                bus = can.interface.Bus(can_interface, bustype='socketcan_native')
                logging.info("CAN: Bus ", bus)
            car.canStatus = True
            while True:
                if not mock:
                    message = bus.recv()
                else:
                    arbitration_id = 1412
                    dat = [random.randint(1,30), random.randint(25,255), 10, 10, 10, 10, 00, 10]
                    dat = dat[0: 8]
                    message = can.Message(arbitration_id=arbitration_id,
                                          timestamp=time.time(),
                                          data=dat, extended_id=False)

                frames.save_frame(message.arbitration_id, message.data)
                car.fill_car_model(message.timestamp, frames)
                await asyncio.sleep(0)
        except Exception:
            car.canStatus = False
            logging.info(f"CAN: Failed to configure can at `{can_interface}` interface")
            await asyncio.sleep(5)
