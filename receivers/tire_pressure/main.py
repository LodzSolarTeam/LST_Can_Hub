import bluepy

TPMSDictionary = {'80:ea:ca:10:06:7d': 'FrontLeft',
                    '81:ea:ca:20:06:55': 'FrontRight',
                    '82:ea:ca:30:04:0e': 'RearLeft',
                    '83:ea:ca:40:03:2e': 'RearRight'}

PRESSURE_STARTING_BIT = 8
TEMPERATURE_STARTING_BIT = 12
PURE_TEMPERATURE_TO_CELCIUS = 0.01
DATA_LENGTH = 36
INT_32_BIT_LENGTH = 4


def ToInt32FromBigEndian(startingBit, string):
    string = string[startingBit*2:(startingBit + INT_32_BIT_LENGTH)*2]
    byteArr = bytes.fromhex(string)

    return int.from_bytes(byteArr, 'little')

def parse(dataString):
    if len(dataString) != DATA_LENGTH:
        return
    else:
        pressureInPa = ToInt32FromBigEndian(PRESSURE_STARTING_BIT, dataString)
        temperatureInCelcius = ToInt32FromBigEndian(TEMPERATURE_STARTING_BIT, dataString)*PURE_TEMPERATURE_TO_CELCIUS

        print("Presure", pressureInPa, "Temperature", temperatureInCelcius)


def handle_device(dev):
    scan_data = dev.getScanData()

    print("Raw", scan_data[2][1])

    if scan_data[2][1] == "Manufacturer":
        data = scan_data[2][2]
        print("data", data)
        parse(data)


def main():
    while True:
        scanner = bluepy.btle.Scanner()
        devices = scanner.scan()

        for dev in devices:

            if dev.addr in TPMSDictionary:
                print("Device", TPMSDictionary[dev.addr], "(", dev.addr, ")")
                handle_device(dev)



if __name__ == "__main__":
    main()

