from syspy.lib import char_utility as cu


class HIRANO_BATTERY:
    # ---------------- Frame IDs ---------------- #
    FRAME_VOLT_CUR_SOC = 0x1E1   # [V, I, SOC, DisplaySOC] — big-endian
    FRAME_TEMP = 0x353   # [Temp]
    FRAME_ALARM = 0x1F5   # [AlarmCode, AlarmLevel]
    FRAME_CHARGE_INFO = 0x1E4   # [mode/status bits, precharge bits]
    FRAME_POWER_WATT = 0x211   # [Power]
    FRAME_DATE = 0x202   # [Date: Year-Month-Day-Hour-Minute-Secounds]
    # ---------------- Alarm Codes ---------------- #
    ERROR_CODE_DICT = {
        0xff: "No fault",
        0x17: "Low SOC",
        0x00: "Charging cell overvoltage",
        0x01: "Discharging cell overvoltage",
        0x02: "Charging cell undervoltage",
        0x03: "Discharging cell undervoltage",
        0x04: "Charging pack overvoltage",
        0x05: "Discharging pack overvoltage",
        0x06: "Charging pack undervoltage",
        0x07: "Discharging pack undervoltage",
        0x08: "Charging voltage imbalance",
        0x09: "Discharging voltage imbalance",
        0x0A: "Charging high temperature",
        0x0B: "Discharging high temperature",
        0x0C: "Charging low temperature",
        0x0D: "Discharging low temperature",
        0x0E: "Charging overcurrent",
        0x0F: "Discharging overcurrent",
        0x10: "Charging temperature difference",
        0x11: "Discharging temperature difference",
        0x12: "Fast charging overcurrent",
        0x13: "Slow charging overcurrent",
        0x14: "Fixed charging overcurrent",
        0x15: "Continuous discharging overcurrent",
        0x16: "Instantaneous discharging overcurrent",
        0x18: "High SOC",
        0x19: "Leakage",
        0x1A: "Discharge heating overtemperature",
        0x1B: "Discharge heating overtemperature",
        0x1C: "Charging battery temperature difference too large",
        0x1D: "Discharging battery temperature difference too large",
        0x1E: "Charging overcurrent timeout",
        0x1F: "Discharging overcurrent timeout",
        0x20: "Charging heater overcurrent",
        0x21: "Discharge heater overcurrent",
        0x22: "SOC too low",
        0x23: "Abnormal supply voltage",
        0x24: "Supply undervoltage",
        0x25: "Supply overvoltage",
        0x26: "Discharge terminal temperature difference too large",
        0x27: "Charge terminal temperature difference too large",
        0x28: "Supply voltage abnormal",
        0x80: "Voltage harness",
        0x81: "Temperature harness",
        0x82: "Internal network communication",
        0x83: "DC charging positive socket temperature",
        0x84: "DC charging negative socket temperature",
        0x85: "AC charging AL socket temperature",
        0x86: "AC charging AH socket temperature",
        0x87: "AC charging AN socket temperature",
        0x88: "AC charging signal socket temperature",
        0x89: "Charger communication interrupted",
        0x8A: "Vehicle communication interrupted",
        0x8B: "Full charge diagnosis (Socket temperature acquisition invalid)",
        0x8C: "Charging socket temperature abnormal",
        0x8D: "Precharge failure (Current acquisition abnormal, open circuit fault)",
        0x8E: "Abnormal current",
        0x8F: "BMS initialization failure",
        0x90: "HVIL fault (MSD fault or other HV interlock fault)",
        0x91: "Relay fault (Relay adhesion, open circuit, etc.)",
        0x92: "Heating fault (Any heater fault, defined by project)",
        0x93: "CC2 connection fault (Resistance valid but not within defined range)",
        0x94: "CC1 connection fault (Resistance valid but not within defined range)",
        0x95: "CP connection fault (Frequency valid but duty cycle not within range)",
        0x96: "Heater temperature abnormal",
        0x97: "Terminal temperature abnormal",
        0x98: "Electronic lock fault",
        0x99: "Multiple charging connection fault",
        0x9A: "Battery pole count mismatch",
        0x9B: "Temperature sensor mismatch",
        0x9C: "Abnormal supply voltage",
    }

    # ---------------- Charge Info Mapping ---------------- #
    CHARGE_MODE = {
        0: "(Not charging)",
        1: "(DC mode)",
        2: "(AC mode)",
        3: "(Reserved)",
    }

    CHARGE_STATUS = {
        0: "(Not charging)",
        1: "(Charging)",
        2: "(Charge complete)",
        3: "(Reserved)",
    }

    PRECHARGE_STATUS = {
        0: "(Not precharge)",
        1: "(Precharging)",
        2: "(Precharge complete)",
        3: "(Precharge failed)",
    }

    # ---------------- Parser Functions ---------------- #
    @staticmethod
    def parse_voltage(data):
        # Voltage from 0x1E1: 2 bytes big-endian, scale 0.1 V
        if len(data) < 2:
            return None
        raw = (data[0] << 8) | data[1]   # big-endian
        return raw * 0.1

    @staticmethod
    def parse_current(data):
        # Current from 0x1E1: 2 bytes big-endian, signed int16, scale 0.1 A
        if len(data) < 5:
            return None
        raw = (data[2] << 8) | data[3]   # big-endian
        signed = cu.u16Toint16(raw)
        return signed * 0.1 - 1000

    @staticmethod
    def parse_soc(data):
        # SOC from 0x1E1: 2 bytes big-endian, scale 0.1 %
        if len(data) < 6:
            return None
        raw = (data[4] << 8) | data[5]   # big-endian
        return raw * 0.01

    @staticmethod
    def parse_display_soc(data):
        # Display SOC from 0x1E1: 2 bytes big-endian, scale 0.1 %
        if len(data) < 8:
            return None
        raw = (data[6] << 8) | data[7]   # big-endian
        return raw * 0.01

    @staticmethod
    def parse_temp(data):
        # Parse frame 0x353: Battery Temp (signed int8 °C)
        if len(data) < 1:
            return None
        temp_raw = cu.u8Toint8(data[0])
        # raw = (data[0] << 0) | data[0]
        return temp_raw - 50

    @staticmethod
    def parse_power(data):
        # Parse frame 0x211: Power 2 bytes big-endian
        if len(data) < 6:
            return None
        raw = (data[4] << 8) | data[5]   # big-endian
        return raw * 0.01 - 100

    @staticmethod
    def parse_alarm(data):
        # Parse frame 0x1F5: Alarm Code + Level
        if len(data) < 2:
            return None
        alarm_code = data[0]
        alarm_level = data[1]
        return {
            "AlarmCode": alarm_code,
            "AlarmLevel": alarm_level,
            "AlarmDesc": HIRANO_BATTERY.ERROR_CODE_DICT.get(alarm_code, "Unknown alarm code"),
        }

    @staticmethod
    def parse_charge(data):
        # Parse frame 0x1E4: ChargeMode, ChargeStatus, PrechargeStatus
        if len(data) < 2:
            return None
        b0 = data[0]
        b1 = data[1]
        charge_mode = b0 & 0x03              # bit0-1
        charge_status = (b0 >> 2) & 0x03     # bit2-3
        precharge_status = b1 & 0x03         # bit0-1
        return {
            "BMS_ChargeMode": charge_mode,
            "BMS_ChargeModeDesc": HIRANO_BATTERY.CHARGE_MODE.get(charge_mode, "Unknown"),
            "BMS_ChargeStatus": charge_status,
            "BMS_ChargeStatusDesc": HIRANO_BATTERY.CHARGE_STATUS.get(charge_status, "Unknown"),
            "BMS_PrechargeStatus": precharge_status,
            "BMS_PrechargeStatusDesc": HIRANO_BATTERY.PRECHARGE_STATUS.get(precharge_status, "Unknown"),
        }

    @staticmethod
    def parse_date_time(data):
        # Parse frame 0x202: Date && Time
        if len(data) < 7:
            return None

        year = (data[0] << 8) | data[1]
        month = data[2]
        day = data[3]
        hour = data[4]
        minute = data[5]
        secounds = data[6]
        return {
            "Day": day,
            "Month": month,
            "Year": year,
            "hour": hour,
            "minute": minute,
            "secounds": secounds,
        }
