import argparse
import sdm_modbus_modified
from sdm_modbus_modified.tools import modbus_scan, modbus_single_request_read_data
import time



def find_name_of_detected_devices(start_id,end_id,port,baudrate,parity):
    connected_devices_list = modbus_scan.modbus_scan(start_id=start_id,
                                                        end_id=end_id,
                                                        port=port,
                                                        baudrate=baudrate,
                                                        parity=parity)
    models_of_detected_devices = dict()

    for id in connected_devices_list:
        device = sdm_modbus_modified.SDM630(device=port,baud=baudrate, unit=id, parity=parity)
        data = device.read('l1_voltage')
        
        if data == 0 :
            models_of_detected_devices[id] = 'WS100-19'
        else :
            models_of_detected_devices[id] = 'SDM'    
            data = device.read('import_demand_power_active')
            if data == 0:
                models_of_detected_devices[id] = 'SDM54-2T'
            else:
                models_of_detected_devices[id] = 'SDM630'
        device.disconnect()
        time.sleep(1)
    print(models_of_detected_devices)
    return models_of_detected_devices

def parse_arguments():
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

    return args

def read_data_connected_devices(devices_id_and_name :dict[int,str],port:str,baudrate:int = 9600,parity:str = 'N'):
    for id,device_name in devices_id_and_name.items():
        print("")
        print(f'Data from {device_name} at ID {id}')
        modbus_single_request_read_data.single_request_read_data(port,baudrate,id,parity,device_name)
        print("")
    
def main():
    args = parse_arguments()

    devices_id_and_name = find_name_of_detected_devices(
        start_id=args.start_id,
        end_id=args.end_id,
        port=args.port,
        baudrate=args.baudrate,
        parity=args.parity
    )

    read_data_connected_devices(devices_id_and_name,port=args.port,baudrate=args.baudrate,parity=args.parity)

if __name__ == "__main__":
    main()