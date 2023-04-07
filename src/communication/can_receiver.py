import logging

import can
import cantools.database


def can_receiver(managed_dict: dict, can_interface):
    db = cantools.database.load_file('./Eagle2-DBC/EAGLE_2_DBC.dbc')
    can_bus = can.interface.Bus(bustype='socketcan', channel=can_interface, bitrate=250000)

    while True:
        message = can_bus.recv()
        try:
            data = db.decode_message(message.arbitration_id, message.data)

            for item in data.items():
                managed_dict[item[0]] = item[1]
        except KeyError as e:
            logging.info(f"Messaged decoding from can failed. {e}")
        except Exception as e:
            logging.info(f"Error: {e}")

    # while True:
    #     try:
    #         global bus, message
    #
    #         if not mock:
    #             bus = can.interface.Bus(CAN_INTERFACE, bustype='socketcan')
    #             logging.info(f"CAN: Bus = {bus}")
    #
    #         frames = Frames()
    #         while True:
    #             if not mock:
    #                 message = bus.recv(0.1)
    #             else:
    #                 arbitration_id = 1412
    #                 dat = [random.randint(1, 30), random.randint(25, 255), 10, 10, 10, 10, 00, 10]
    #                 dat = dat[0: 8]
    #                 message = can.Message(arbitration_id=arbitration_id,
    #                                       timestamp=time.time(),
    #                                       data=dat, extended_id=False)
    #             frames.save_frame(message.arbitration_id, message.data)
    #             car.fill_can_data(frames)
    #             logging.debug(f"[CAN] Messsage gathered id={message.arbitration_id} data={message.data}")
    #             time.sleep(1 if mock else 0.0)
    #     except Exception:
    #         logging.warning(f"CAN: Failed to configure can at `{CAN_INTERFACE}` interface")
    #         time.sleep(1)
