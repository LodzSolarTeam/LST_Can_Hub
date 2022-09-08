import logging
from struct import pack
import can 
import time

from receivers.e2_can import CAN_INTERFACE


def send_timesync():
    with can.interface.Bus(CAN_INTERFACE, bustype='socketcan') as bus:
        while True:
            msg = can.Message(
                arbitration_id=0x1, 
                data=pack("Q", (time.time_ns() // 1_000_000)),
            )
            try:
                bus.send(msg)
                logging.info(f"Message sent on {bus.channel_info}")
            except can.CanError:
                logging.info("Message NOT sent")
            time.sleep(60)

if __name__ == "__main__":
    send_timesync()