import can
import time

filename = './can-data.TXT'


def can_faker():
    can_bus = can.interface.Bus("vcan0", bustype='socketcan')

    with open(filename) as log_file:
        log_file.readline()
        i = 0
        for line in log_file.readlines():
            i = i + 1
            try:
                data, dlc, extended, frame_id, timestamp = decode(line)
                msg = can.Message(
                    timestamp=timestamp,
                    arbitration_id=frame_id,
                    dlc=dlc,
                    is_extended_id=extended,
                    data=data
                )
                can_bus.send(msg)
                time.sleep(0.1)
            except KeyboardInterrupt:
                exit('Aborting at {} lines'.format(i))
            except Exception as e:
                print("Could not process frame", e)
                return


def decode(line):
    parts = line.split(';')

    frame_id = int(parts[4])
    timestamp = int(parts[1])
    dlc = int(parts[5])
    extended = (False if parts[3] == 'S' else True)
    data = [eval(i) for i in parts[6:-1]]

    return data, dlc, extended, frame_id, timestamp
