from TPMSCanSender import TPMSCanSender, Wheel

DEVICE_MAP = {
    '80:ea:ca:10:06:7d': Wheel.FRONT_LEFT,
    '81:ea:ca:20:06:55': Wheel.FRONT_RIGHT,
    '82:ea:ca:30:04:0e': Wheel.REAR_LEFT,
    '83:ea:ca:40:03:2e': Wheel.REAR_RIGHT,
}

# PRESSURE_STARTING_BIT = 8
# TEMPERATURE_STARTING_BIT = 12
# PURE_TEMPERATURE_TO_CELCIUS = 0.01
# DATA_LENGTH = 36
# INT_32_BIT_LENGTH = 4


class BLEParser:
    def __init__(self, sender: TPMSCanSender) -> None:
        self._sender = sender

    def handle_data(self, device_addr, device_data):
        if device_addr in DEVICE_MAP:
            manufacturer_data = self._get_manufacturer_data(device_data)

            if manufacturer_data:
                pressure = self._decode_pressure(manufacturer_data)
                self._sender.set_pressure(DEVICE_MAP[device_addr], pressure)
                self._sender.send()

    def get_devices_addr(self):
        return list(DEVICE_MAP.keys())

    def _get_manufacturer_data(self, device_data):
        for data in device_data:
            if data[1] == "Manufacturer":
                return data[2]

        assert None

    def _decode_pressure(self, data):
        return 0
