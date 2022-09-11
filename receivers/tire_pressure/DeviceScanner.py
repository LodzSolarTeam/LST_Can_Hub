from bluepy.btle import Scanner


class DeviceScanner:
    def __init__(self) -> None:
        self._device_filter = []
        self._callback = None

    def add_device_to_filter(self, device_addr: str):
        self._device_filter.append(device_addr)

    def add_devices_to_filter(self, devices_addr):
        self._device_filter.extend(devices_addr)

    def set_callback(self, callback):
        self._callback = callback

    def run(self):
        while True:
            scanner = Scanner()
            devices = scanner.scan()

            for dev in devices:
                if dev.addr in self._device_filter:
                    self._callback(dev.addr, dev.getScanData())
