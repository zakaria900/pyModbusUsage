import argparse
import pymodbus.exceptions
import sdm_modbus_modified
import sdm_modbus_modified.ws100
import time


def single_request_read_data(port,baudrate,id,parity,device_name):
    if device_name == "SDM54-2T":
        device = sdm_modbus_modified.SDM54_2T(device=port, baud=baudrate, unit=id, parity=parity)
        device_type = "sdm"

    elif device_name == "SDM630":
        device = sdm_modbus_modified.SDM630(device=port, baud=baudrate, unit=id, parity=parity)
        device_type = "sdm"

    elif device_name == "WS100-19":
        device = sdm_modbus_modified.ws100.WS100_19XX(device=port, baud=baudrate, unit=id, parity=parity)
        device_type = "ws100"

    else:
        raise ValueError(f"Unsupported device_name: {device_name}")

    # --- Lecture des données ---
    if device_type == "sdm":
        print(device.read_all())
        device.disconnect()

    elif device_type == "ws100":
        print(device.read_all_scaled())
        device.disconnect()

if "__init__" == "__main__":
    parser = argparse.ArgumentParser(description="Read data from a single SDM ou WS100-19XX device.")

    parser.add_argument("-p", "--port", type=str, required=True,
                        help="Serial Port eg : /dev/ttyUSB0")

    parser.add_argument("-b", "--baudrate", type=int, default=9600,
                        help="Baudrate, by default 9600")

    parser.add_argument("-i", "--id", type=int, default=1,
                        help="Modbus Slave ID, by default 1")

    parser.add_argument("--parity", type=str, default="N", choices=["N", "E", "O"],
                        help="Parity : N (None), E (Even), O (Odd). By default : N")

    parser.add_argument("--device_name", type=str, default="SDM54-2T", choices=["SDM54-2T", "SDM630", "WS100-19"],
                        help="Device model. Choose between : SDM54-2T, SDM630, WS100-19")

    args = parser.parse_args()
    
    single_request_read_data(port=args.port, baudrate=args.baudrate, id=args.id , parity=args.parity, device_name=args.device_name)