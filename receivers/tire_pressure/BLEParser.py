from struct import unpack
from TPMSCanSender import TPMSCanSender, Wheel

DEVICE_MAP = {
    '80:ea:ca:10:06:7d': Wheel.FRONT_LEFT,
    '81:ea:ca:20:06:55': Wheel.FRONT_RIGHT,
    '82:ea:ca:30:04:0e': Wheel.REAR_LEFT,
    '83:ea:ca:40:03:2e': Wheel.REAR_RIGHT,
}


class BLEParser:
    def __init__(self, sender: TPMSCanSender) -> None:
        self._sender = sender

    def handle_data(self, device_addr, device_data):
        if device_addr in DEVICE_MAP:
            manufacturer_data = self._get_manufacturer_data(device_data)

            if manufacturer_data:
                pressure = self._decode_pressure(manufacturer_data)
                self._sender.set_pressure(DEVICE_MAP[device_addr], pressure)

    def get_devices_addr(self):
        return list(DEVICE_MAP.keys())

    def _get_manufacturer_data(self, device_data):
        for data in device_data:
            if data[1] == "Manufacturer":
                return data[2]

        assert None

    def _decode_pressure(self, data):
        unpacked = unpack("HIIIBB", bytes.fromhex(data))

        pressure = unpacked[2]
        temperature = unpacked[3] * 0.01
        battery = unpacked[4]

        return pressure
