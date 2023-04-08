import os
import cantools.database

db = cantools.database.load_file(os.getcwd() + '/external/Eagle2-DBC/EAGLE_2_DBC.dbc')

i = 0
for msg in db.messages:
    for signal in msg.signals:
        i += 1
        print(f"optional {msg.send_type} {signal.name} = {i}")
