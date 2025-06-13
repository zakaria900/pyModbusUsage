from sdm_modbus_modified import meter
import pymodbus.exceptions


class WS100(meter.Meter):
    pass

class WS100_19XX(WS100):

    def __init__(self, *args, **kwargs):
        self.model = "WS100_19XX"
        self.baud = 9600

        super().__init__(*args, **kwargs)
        self.registers = {
        # ======================
        # Instant Measures
        # ======================
        "voltage": (0x0100, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Voltage", "V", 1, 1, 3),  # m+n = 3+3
        "current": (0x0102, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Current", "A", 1, 1, 3),  # 2+3
        "active_power": (0x0104, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Active Power", "W", 1, 1, 0),  # 5+0
        "apparent_power": (0x0106, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Apparent Power", "VA", 1, 1, 0),
        "reactive_power": (0x0108, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Reactive Power", "var", 1, 1, 0),
        "frequency": (0x010A, 1, meter.registerType.INPUT, meter.registerDataType.INT16, float, "Frequency", "Hz", 1, 0.1, 0),  # 2+1
        "power_factor": (0x010B, 1, meter.registerType.INPUT, meter.registerDataType.INT16, float, "Power Factor", "", 1, 0.001, 3),  # 1+3

        # ======================
        # Active Energy
        # ======================
        "total_forward_active_energy": (0x010E, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Total Forward Active Energy", "kWh", 1, 1, 2),
        "t1_forward_active_energy": (0x0110, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "T1 Forward Active Energy", "kWh", 1, 1, 2),
        "t2_forward_active_energy": (0x0112, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "T2 Forward Active Energy", "kWh", 1, 1, 2),
        "t3_forward_active_energy": (0x0114, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "T3 Forward Active Energy", "kWh", 1, 1, 2),
        "t4_forward_active_energy": (0x0116, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "T4 Forward Active Energy", "kWh", 1, 1, 2),

        "total_reverse_active_energy": (0x0118, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Total Reverse Active Energy", "kWh", 1, 1, 2),
        "t1_reverse_active_energy": (0x011A, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "T1 Reverse Active Energy", "kWh", 1, 1, 2),
        "t2_reverse_active_energy": (0x011C, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "T2 Reverse Active Energy", "kWh", 1, 1, 2),
        "t3_reverse_active_energy": (0x011E, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "T3 Reverse Active Energy", "kWh", 1, 1, 2),
        "t4_reverse_active_energy": (0x0120, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "T4 Reverse Active Energy", "kWh", 1, 1, 2),

        "total_active_energy": (0x0122, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Total Active Energy", "kWh", 1, 1, 2),

        # ======================
        # Reactive Energy
        # ======================
        "total_forward_reactive_energy": (0x012C, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Total Forward Reactive Energy", "kvarh", 1, 1, 2),
        "total_reverse_reactive_energy": (0x0136, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Total Reverse Reactive Energy", "kvarh", 1, 1, 2),
        "total_reactive_energy": (0x0140, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Total Reactive Energy", "kvarh", 1, 1, 2),

        # ======================
        # Power Demand
        # ======================
            "forward_active_demand": (0x0176, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Forward Active Demand", "W", 2, 1,1),
            "reverse_active_demand": (0x017A, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Reverse Active Demand", "W", 2, 1,1),
            "forward_reactive_demand": (0x0180, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Forward Reactive Demand", "var", 2, 1,1),
            "reverse_reactive_demand": (0x0184, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Reverse Reactive Demand", "var", 2, 1,1),

        # ======================
        # 3. Meter Parameters (Zählerparameter)
        # ======================
        "serial_number": (0x1000, 6, meter.registerType.INPUT, meter.registerDataType.BYTES, bytes, "Serial Number", "–", None, None, None),
        "modbus_id": (0x1003, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "Modbus ID", "–", None, None, None),
        "hw_version": (0x1004, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "HW Version", "–", None, None, None),
        "fw_checksum": (0x1005, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "FW Checksum", "–", None, None, None),
        "time": (0x1007, 4, meter.registerType.INPUT, meter.registerDataType.BYTES, bytes, "Time (Current Date & Time)", "–", None, None, None),
        "cycle_display": (0x100B, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "Cycle Display Time", "s", None, None, None),
        "baud_rate": (0x100C, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "485 Baud Rate", "–", None, None, None),
        "parity": (0x100D, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "Parity", "–", None, None, None),
        "stop_bit": (0x100E, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "Stop Bit", "–", None, None, None),
        "energy_calc_code": (0x100F, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "Energy Calculation Code", "–", None, None, None),
        "demand_mode": (0x1010, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "Demand Mode", "–", None, None, None),
        "demand_cycle": (0x1011, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "Demand Cycle", "min", None, None, None),
        "auto_cycle_display": (0x1012, 4, meter.registerType.INPUT, meter.registerDataType.BYTES, bytes, "Auto Cycle Display Content", "–", None, None, None),
        "password_setting": (0x1016, 1, meter.registerType.INPUT, meter.registerDataType.INT16, int, "Password Setting", "–", None, None, None),
        "meter_running_time": (0x1018, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Meter Running Time", "–", None, None, None),
        "timing_current": (0x101A, 2, meter.registerType.INPUT, meter.registerDataType.INT32, int, "Timing Current Value", "mA", None, None, None),
    
        # ======================
        # 4. Tariff Parameters (Tarifparameter)
        # ======================
        "tariff_table_1": (0x1700, 12, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Time Period Table 1", "", None, None, None),
        "tariff_table_2": (0x170C, 12, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Time Period Table 2", "", None, None, None),
        "tariff_table_3": (0x1718, 12, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Time Period Table 3", "", None, None, None),
        "tariff_table_4": (0x1724, 12, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Time Period Table 4", "", None, None, None),
        "tariff_table_5": (0x1730, 12, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Time Period Table 5", "", None, None, None),
        "tariff_table_6": (0x173C, 12, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Time Period Table 6", "", None, None, None),
        "tariff_table_7": (0x1748, 12, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Time Period Table 7", "", None, None, None),
        "tariff_table_8": (0x1754, 12, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Time Period Table 8", "", None, None, None),
        "time_zone_table": (0x1760, 12, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Time Zone Table", "", None, None, None),
        "holidays_table": (0x176C, 21, meter.registerType.HOLDING, meter.registerDataType.BYTES, bytes, "Holidays Table", "", None, None, None),
                }

    def read_scaled(self, key):
            """Reads a register and scales the data"""
            if key not in self.registers:
                raise KeyError(key)

            value = self._read(self.registers[key])
            _, _, _, _, _, _, _, _, scale, decimals = self.registers[key]
            return value * scale * (10 ** -decimals)

    def read_all_scaled(self):
        """Reads all registers with their scales"""
        result = {}
        for k in self.registers.keys():
            try:
                result[k] = self.read_scaled(k)
            except pymodbus.exceptions.ModbusIOException:
                print(f'Problem with register address: {k}')
        return result
