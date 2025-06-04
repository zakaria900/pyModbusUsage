import pymodbus.exceptions
import sdm_modbus
import time 
import pymodbus

start_ID = 1
end_ID = 10

for address in range(start_ID, end_ID +1):
        device = sdm_modbus.SDM630(device="/dev/ttyUSB1",baud=9600, unit=address, parity="N")
        print(device.connected())
        try:
            device.read('l1_voltage')
            print(f'Device detected at ID {address}')
            print("")
            device.disconnect()
            time.sleep(1)
        except pymodbus.exceptions.ModbusIOException:
            print(f"No Device at ID {address}")
            device.disconnect()
            print("")