from DeviceScanner import DeviceScanner
from BLEParser import BLEParser
from TPMSCanSender import TPMSCanSender

parser = None
tpmsCanSender = TPMSCanSender()


def handle_device(addr, scan_data):
    global parser
    parser.handle_data(addr, scan_data)
    tpmsCanSender.send()


def main():
    global parser
    parser = BLEParser(tpmsCanSender)

    scanner = DeviceScanner()
    scanner.add_devices_to_filter(parser.get_devices_addr())
    scanner.set_callback(handle_device)
    scanner.run()


if __name__ == "__main__":
    main()
