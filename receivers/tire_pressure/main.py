from DeviceScanner import DeviceScanner
from BLEParser import BLEParser, BLESensors
from TPMSCanSender import TPMSCanSender

# def ToInt32FromBigEndian(startingBit, string):
#     string = string[startingBit*2:(startingBit + INT_32_BIT_LENGTH)*2]
#     byteArr = bytes.fromhex(string)

#     return int.from_bytes(byteArr, 'little')

# def parse(dataString):
#     if len(dataString) != DATA_LENGTH:
#         return
#     else:
#         pressureInPa = ToInt32FromBigEndian(PRESSURE_STARTING_BIT, dataString)
#         temperatureInCelcius = ToInt32FromBigEndian(TEMPERATURE_STARTING_BIT, dataString)*PURE_TEMPERATURE_TO_CELCIUS

#         print("Presure", pressureInPa, "Temperature", temperatureInCelcius)


# def handle_device(dev):
#     scan_data = dev.getScanData()

#     print("Raw", scan_data[2][1])

#     if scan_data[2][1] == "Manufacturer":
#         data = scan_data[2][2]
#         print("data", data)
#         parse(data)

parser = None
tpmsCanSender = TPMSCanSender()


def handle_device(addr, scan_data):
    parser.handle_data(addr, scan_data)
    tpmsCanSender.send()


def main():
    parser = BLEParser(tpmsCanSender)

    scanner = DeviceScanner()
    scanner.add_devices_to_filter(parser.get_devices_addr())
    scanner.set_callback(handle_device)
    scanner.run()


if __name__ == "__main__":
    main()
