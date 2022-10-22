import os
import can, time

filename = './can-data.TXT'


def can_faker():
    can_bus = can.interface.Bus("vcan0", bustype='socketcan')

    with open(filename) as log_file:
        print("Input file opened")
        log_file.readline()
        i = 0
        for line in log_file.readlines():
            i = i + 1
            parts = line.split(';')
            try:
                ID = int(parts[4])
                TIMESTAMP = int(parts[1])
                DLC = int(parts[5])
                msg = can.Message(
                    timestamp=TIMESTAMP,
                    arbitration_id=ID,
                    dlc=DLC,
                    is_extended_id=(False if parts[3] == 'S' else True),
                    data=[eval(i) for i in parts[6:-1]]
                )
                can_bus.send(msg)
                time.sleep(0.5)
            except KeyboardInterrupt:
                exit('Aborting at {} lines'.format(i))
            except Exception as e:
                print("Could not process frame", e)
                return
