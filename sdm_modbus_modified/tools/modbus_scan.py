import pymodbus.exceptions
import sdm_modbus_modified
import time 
import pymodbus
import argparse

def modbus_scan(start_id,end_id,port,baudrate,parity):
    connected_devices_id_list = list()
    
    for address in range(start_id, end_id +1):
            device = sdm_modbus_modified.SDM630(device=port,baud=baudrate, unit=address, parity=parity)
            if device.connected() :
                 print("Device connected")

            try:
                device.read('l1_voltage')
                print(f'Device detected at ID {address}')
                print("")
                connected_devices_id_list.append(address)
                device.disconnect()
                time.sleep(1)
            except pymodbus.exceptions.ModbusIOException:
                print(f"No Device at ID {address}")
                device.disconnect()
                print("")
                
    return connected_devices_id_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan Modbus RTU network for responding devices (SDM-compatible).")

    parser.add_argument("-p", "--port", type=str, required=True,
                        help="Serial port (e.g. /dev/ttyUSB0 or COM4)")

    parser.add_argument("-b", "--baudrate", type=int, default=9600,
                        help="Baudrate (default: 9600)")

    parser.add_argument("--parity", type=str, default="N", choices=["N", "E", "O"],
                        help="Parity: N (None), E (Even), O (Odd). Default: N")

    parser.add_argument("--start_id", type=int, default=1,
                        help="Start of Modbus slave ID range to scan (default: 1)")

    parser.add_argument("--end_id", type=int, default=247,
                        help="End of Modbus slave ID range to scan (default: 247)")

    args = parser.parse_args()

    modbus_scan(
        start_id=args.start_id,
        end_id=args.end_id,
        port=args.port,
        baudrate=args.baudrate,
        parity=args.parity
    )