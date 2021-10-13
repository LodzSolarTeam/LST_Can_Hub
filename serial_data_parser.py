import struct
import asyncio
import logging
import serial
import glob
from asyncio.futures import CancelledError

class SerialDataParser:

    PAYLOAD_START_BYTE = 9
    CELL_TYPE_BYTE = 6

    VOLTAGE_FLAG = b'D'
    TEMPERATURE_FLAG = b'E'

    TEMPERATURE_VALUE_LEN = 2
    VOLTAGE_VALUE_LEN = 4

    VOLTAGE_ROW_BEGINNING = {
        b'r00047': 0,
        b'r00037': 16,
        b'r00027': 32,
        b'r00017': 48,
    }

    VOLTAGE_CELLS_IN_ROW = 8
    
    TEMPERATURE_ROW_BEGINNING = {
        b'r00047': 0,
        b'r00037': 4,
        b'r00027': 8,
        b'r00017': 12,
    }

    TEMPERATURE_CELLS_IN_ROW = 4

    MAX_LINE_LENGTH = 100
    ser = None
    def __init__(self, cells_voltage, cells_temperature):
        self.cells_voltage = cells_voltage
        self.cells_temperature = cells_temperature

        self._init_serial()

    def _init_serial(self):
        if self.ser:
            self.ser.close()
        try:
            ports = glob.glob('/dev/ttyUSB*')

            self.ser = serial.Serial(port=ports[0],
                            baudrate=38400,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            timeout=0.1)
            print("Serial communication started succesfully")
        except Exception as e:
            print("Failed to start serial communication")
            self.ser = None

    async def _readline_from_serial(self):
        eol = b'\r'
        leneol = len(eol)
        line = bytearray()
        while True:
            c = self.ser.read(1)
            if not c or len(line) > self.MAX_LINE_LENGTH:
                break
            else:
                line += c
                if line[-leneol:] == eol:
                    break

        await asyncio.sleep(0)
        return bytes(line)

    def _get_value_from_message(self, data, start_byte, length):
        value = int.from_bytes(
            bytearray.fromhex(
                data[start_byte: start_byte + length].decode("utf-8")
            ),
            "big",
        )
        if length == 2:
            return struct.pack('<B', value)
        if length == 4:
            return struct.pack('<H', value)
        if length == 8:
            return struct.pack('<I', value)

    async def _get_data_from_serial(self):
        return await self._readline_from_serial()

    async def start_listening(self):
        while True:
            try:
                if not self.ser:
                    await asyncio.sleep(10)
                    self._init_serial()
                    continue
                data = await self._get_data_from_serial()

                if len(data) > self.CELL_TYPE_BYTE and data[0: self.CELL_TYPE_BYTE] in self.VOLTAGE_ROW_BEGINNING:
                    frame_id = data[0: self.CELL_TYPE_BYTE]
                    if bytes([data[self.CELL_TYPE_BYTE]]) == self.VOLTAGE_FLAG:
                        if frame_id == b'r00017': # for this particular frame byte order needs to be changed
                            data = bytearray(data)
                            data[33:41] = b'ff80ff80'
                        for i in range(self.VOLTAGE_CELLS_IN_ROW):
                            self.cells_voltage[
                                self.VOLTAGE_ROW_BEGINNING[frame_id] + i*int(self.VOLTAGE_VALUE_LEN/2):
                                self.VOLTAGE_ROW_BEGINNING[frame_id] + i*int(self.VOLTAGE_VALUE_LEN/2) + int(self.VOLTAGE_VALUE_LEN/2)
                            ] = self._get_value_from_message(
                                data, self.PAYLOAD_START_BYTE + i*self.VOLTAGE_VALUE_LEN, self.VOLTAGE_VALUE_LEN
                            )
                    elif bytes([data[self.CELL_TYPE_BYTE]]) == self.TEMPERATURE_FLAG:
                        if frame_id == b'r00017': # for this particular frame byte order needs to be changed
                            data = bytearray(data)
                            data[13:15] = b'80'
                        for i in range(self.TEMPERATURE_CELLS_IN_ROW):
                            self.cells_temperature[
                                self.TEMPERATURE_ROW_BEGINNING[frame_id] + i*int(self.TEMPERATURE_VALUE_LEN/2):
                                self.TEMPERATURE_ROW_BEGINNING[frame_id] + i*int(self.TEMPERATURE_VALUE_LEN/2) + int(self.TEMPERATURE_VALUE_LEN/2)
                            ] = self._get_value_from_message(
                                data, self.PAYLOAD_START_BYTE + i*self.TEMPERATURE_VALUE_LEN, self.TEMPERATURE_VALUE_LEN
                            )
            except CancelledError:
                self.ser.close()
            except Exception as e:
                print(f"A problem occured during parsing serial data: {e}")
                await asyncio.sleep(10)
                self._init_serial()
