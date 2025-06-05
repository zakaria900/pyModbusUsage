import enum
import importlib
import time
import struct
from pymodbus.constants import Endian
from pymodbus.client import ModbusTcpClient
from pymodbus.client import ModbusUdpClient
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.pdu.register_message import ReadInputRegistersResponse, ReadHoldingRegistersResponse


class connectionType(enum.Enum):
    RTU = 1
    TCP = 2
    UDP = 3


class registerType(enum.Enum):
    INPUT = 1
    HOLDING = 2


class registerDataType(enum.Enum):
    BITS = 1
    UINT8 = 2
    UINT16 = 3
    UINT32 = 4
    UINT64 = 5
    INT8 = 6
    INT16 = 7
    INT32 = 8
    INT64 = 9
    FLOAT16 = 10
    FLOAT32 = 11
    STRING = 12


RETRIES = 3
TIMEOUT = 1
UNIT = 1


class Meter:
    model = "Generic"
    registers = {}

    stopbits = 1
    parity = "N"
    baud = 38400

    wordorder = Endian.BIG
    byteorder = Endian.BIG
    
    udp = False

    def __init__(self, **kwargs):
        parent = kwargs.get("parent")

        if parent:
            self.client = parent.client
            self.mode = parent.mode
            self.timeout = parent.timeout
            self.retries = parent.retries
            self.framer = parent.framer

            unit = kwargs.get("unit")

            if unit:
                self.unit = unit
            else:
                self.unit = parent.unit

            if self.mode is connectionType.RTU:
                self.device = parent.device
                self.stopbits = parent.stopbits
                self.parity = parent.parity
                self.baud = parent.baud
            elif self.mode is connectionType.TCP:
                self.host = parent.host
                self.port = parent.port
            elif self.mode is connectionType.UDP:
                self.host = parent.host
                self.port = parent.port
            else:
                raise NotImplementedError(self.mode)
        else:
            self.timeout = kwargs.get("timeout", TIMEOUT)
            self.retries = kwargs.get("retries", RETRIES)
            self.unit = kwargs.get("unit", UNIT)

            client_args = {}

            framer_name = kwargs.get("framer")
            if framer_name is None:
                self.framer = None
            else:
                try:
                    framer_package_name = f"pymodbus.framer.{framer_name}_framer"
                    framer_class_name = f"Modbus{framer_name[0].upper()}{framer_name[1:]}Framer"
                    self.framer = importlib.import_module(framer_package_name).__getattribute__(framer_class_name)
                    client_args["framer"] = self.framer
                except Exception as e:
                    raise ValueError(f"failed to import {framer_name} framer: {e}")

            device = kwargs.get("device")
            
            udp = kwargs.get("udp")

            if device:
                self.device = device

                stopbits = kwargs.get("stopbits")

                if stopbits:
                    self.stopbits = stopbits

                parity = kwargs.get("parity")

                if (parity
                        and parity.upper() in ["N", "E", "O"]):
                    self.parity = parity.upper()
                else:
                    self.parity = False

                baud = kwargs.get("baud")

                if baud:
                    self.baud = baud

                self.mode = connectionType.RTU
                self.client = ModbusSerialClient(
                    port=self.device,
                    stopbits=self.stopbits,
                    parity=self.parity,
                    baudrate=self.baud,
                    timeout=self.timeout,
                    **client_args
                )
            elif udp:
                self.host = kwargs.get("host")
                self.port = kwargs.get("port", 502)
                
                self.mode = connectionType.UDP

                self.client = ModbusUdpClient(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout,
                    **client_args
                )
            else:
                self.host = kwargs.get("host")
                self.port = kwargs.get("port", 502)
                
                self.mode = connectionType.TCP

                self.client = ModbusTcpClient(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout,
                    **client_args
                )

        self.connect()

    def __repr__(self):
        framer_name = self.framer.__name__ if self.framer is not None else "default"
        if self.mode == connectionType.RTU:
            return f"{self.model}({self.device}, {self.mode}: stopbits={self.stopbits}, parity={self.parity}, baud={self.baud}, timeout={self.timeout}, retries={self.retries}, unit={hex(self.unit)}, framer={framer_name})"
        elif self.mode == connectionType.TCP:
            return f"{self.model}({self.host}:{self.port}, {self.mode}: timeout={self.timeout}, retries={self.retries}, unit={hex(self.unit)}, framer={framer_name})"
        elif self.mode == connectionType.UDP:
            return f"{self.model}({self.host}:{self.port}, {self.mode}: timeout={self.timeout}, retries={self.retries}, unit={hex(self.unit)}, framer={framer_name})"
        else:
            return f"<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}>"


    def _read_input_registers(self, address, length):
        for _ in range(self.retries):
            if not self.connected():
                self.connect()
                time.sleep(0.1)
                continue

            result = self.client.read_input_registers(address=address, count=length, slave=self.unit)

            if result is None or result.isError():
                continue
            if not hasattr(result, "registers") or len(result.registers) != length:
                continue

            return result.registers  # Returns raw registers

        return None


    def _read_holding_registers(self, address, length):
        for _ in range(self.retries):
            if not self.connected():
                self.connect()
                time.sleep(0.1)
                continue
            result = self.client.read_holding_registers(address=address, count=length, slave=self.unit)

            if result is None or result.isError():
                continue
            if not hasattr(result, "registers") or len(result.registers) != length:
                continue

            return result.registers  # Returns raw registers

        return None



    def _write_holding_register(self, address, value):
        return self.client.write_registers(address=address, values=value)

    def _encode_value(self, data, dtype):
        builder = BinaryPayloadBuilder(byteorder=self.byteorder, wordorder=self.wordorder)

        try:
            if dtype == registerDataType.FLOAT32:
                builder.add_32bit_float(data)
            elif dtype == registerDataType.INT32:
                builder.add_32bit_int(data)
            elif dtype == registerDataType.UINT32:
                builder.add_32bit_uint(data)
            elif dtype == registerDataType.INT16:
                builder.add_16bit_int(int(data))
            else:
                raise NotImplementedError(dtype)
        except NotImplementedError:
            raise

        return builder.to_registers()

    def _decode_value(self, data, length, dtype, vtype):
        try:
            # Convert the registers in a byte sequence
            if self.wordorder == Endian.LITTLE:
                data = list(reversed(data))

            raw_bytes = b''.join(word.to_bytes(2, byteorder='big' if self.byteorder == Endian.BIG else 'little') for word in data)

            if dtype == registerDataType.FLOAT32:
                result = struct.unpack(">f", raw_bytes)[0]
            elif dtype == registerDataType.INT32:
                result = struct.unpack(">i", raw_bytes)[0]
            elif dtype == registerDataType.UINT32:
                result = struct.unpack(">I", raw_bytes)[0]
            elif dtype == registerDataType.INT16:
                result = struct.unpack(">h", raw_bytes)[0]
            else:
                raise NotImplementedError(f"Unsupported data type: {dtype}")

            return vtype(result)

        except Exception as e:
            raise ValueError(f"Could not decode {dtype}: {e}")


    def _read(self, value):
        address, length, rtype, dtype, vtype, label, fmt, batch, sf = value[:9]

        try:
            if rtype == registerType.INPUT:
                return self._decode_value(self._read_input_registers(address, length), length, dtype, vtype)
            elif rtype == registerType.HOLDING:
                return self._decode_value(self._read_holding_registers(address, length), length, dtype, vtype)
            else:
                raise NotImplementedError(rtype)
        except NotImplementedError:
            raise

    def _read_all(self, values, rtype):
        addr_min = False
        addr_max = False

        for k, v in values.items():
            v_addr = v[0]
            v_length = v[1]

            if addr_min is False:
                addr_min = v_addr
            if addr_max is False:
                addr_max = v_addr + v_length

            if v_addr < addr_min:
                addr_min = v_addr
            if (v_addr + v_length) > addr_max:
                addr_max = v_addr + v_length

        results = {}
        offset = addr_min
        length = addr_max - addr_min

        try:
            if rtype == registerType.INPUT:
                data = self._read_input_registers(offset, length)
            elif rtype == registerType.HOLDING:
                data = self._read_holding_registers(offset, length)
            else:
                raise NotImplementedError(rtype)

            if not data:
                return results
            for k, v in values.items():
                address, length, rtype, dtype, vtype, label, fmt, batch, sf = v[:9]

                relative_offset = address - addr_min
                registers_slice = data[relative_offset:relative_offset + length]

                results[k] = self._decode_value(registers_slice, length, dtype, vtype)

        except NotImplementedError:
            raise

        return results

    def _write(self, value, data):
        address, length, rtype, dtype, vtype, label, fmt, batch, sf = value

        try:
            if rtype == registerType.HOLDING:
                return self._write_holding_register(address, self._encode_value(data, dtype))
            else:
                raise NotImplementedError(rtype)
        except NotImplementedError:
            raise

    def connect(self):
        return self.client.connect()

    def disconnect(self):
        self.client.close()

    def connected(self):
        return self.client.is_socket_open()

    def get_scaling(self, key):
        address, length, rtype, dtype, vtype, label, fmt, batch, sf = self.registers[key]
        return sf

    def read(self, key, scaling=False):
        if key not in self.registers:
            raise KeyError(key)

        if scaling:
            return self._read(self.registers[key]) * self.get_scaling(key)
        else:
            return self._read(self.registers[key])

    def write(self, key, data):
        if key not in self.registers:
            raise KeyError(key)

        return self._write(self.registers[key], data / self.get_scaling(key))

    def read_all(self, rtype=registerType.INPUT, scaling=False):
        registers = {k: v for k, v in self.registers.items() if (v[2] == rtype)}
        results = {}

        for batch in range(1, max(len(registers), 2)):
            register_batch = {k: v for k, v in registers.items() if (v[7] == batch)}

            if not register_batch:
                break

            results.update(self._read_all(register_batch, rtype))

        if scaling:
            return {k: v * self.get_scaling(k) for k, v in results.items()}
        else:
            return {k: v for k, v in results.items()}
