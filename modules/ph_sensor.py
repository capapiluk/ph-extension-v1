"""
PH Sensor Module for MicroPython 1.6.0 (ESP32)
Arduino-style averaging (remove min/max)

Author: Cap_Apiluk (modified)
"""

import machine
import time
import json

# =====================================================
# pH Sensor Class
# =====================================================

class PHSensor:

    SAMPLE_COUNT = 10

    def __init__(self):
        self._pin = None
        self._adc = None
        self._aref = 3.3
        self._adc_range = 4095

        # Default calibration
        self._slope = -6.80
        self._intercept = 25.85

        self._ph_value = 0.0
        self._voltage = 0.0
        self._raw_adc = 0

        self._samples = [0] * self.SAMPLE_COUNT
        self._index = 0

        self._cal_file = "ph_calibration.json"

    # -------------------------------------------------

    def set_pin(self, pin):
        self._pin = pin
        self._adc = machine.ADC(machine.Pin(pin))
        self._adc.atten(machine.ADC.ATTN_11DB)   # สำคัญ!
        self._adc.width(machine.ADC.WIDTH_12BIT)

    # -------------------------------------------------

    def begin(self):
        if self._adc is None:
            raise ValueError("Call set_pin() first")

        self._load_calibration()
        print("PH Sensor Ready")
        print("Pin: GPIO", self._pin)
        print("Slope (m): %.2f" % self._slope)
        print("Intercept (c): %.2f" % self._intercept)

    # -------------------------------------------------

    def _average_array(self):
        values = self._samples[:]

        if len(values) < 5:
            return sum(values) / len(values)

        min_v = min(values)
        max_v = max(values)

        total = 0
        count = 0
        for v in values:
            if v != min_v and v != max_v:
                total += v
                count += 1

        if count == 0:
            return sum(values) / len(values)

        return total / count

    # -------------------------------------------------

    def update(self):
        # อ่านค่า ADC ดิบ
        raw = self._adc.read()
        self._raw_adc = raw

        # เก็บลง buffer
        self._samples[self._index] = raw
        self._index = (self._index + 1) % self.SAMPLE_COUNT

        # average แบบ Arduino
        avg_adc = self._average_array()

        self._voltage = avg_adc * self._aref / self._adc_range
        self._ph_value = self._slope * self._voltage + self._intercept

    # -------------------------------------------------

    def get_ph_value(self):
        return round(self._ph_value, 2)

    def get_voltage(self):
        return round(self._voltage, 3)

    def get_raw_adc(self):
        return self._raw_adc

    # -------------------------------------------------
    # Calibration
    # -------------------------------------------------

    def calibrate_two_point(self, ph4_voltage, ph7_voltage):
        if ph4_voltage == ph7_voltage:
            print("Calibration error: same voltage")
            return False

        self._slope = (7.0 - 4.0) / (ph7_voltage - ph4_voltage)
        self._intercept = 4.0 - self._slope * ph4_voltage

        self._save_calibration()

        print("=" * 40)
        print("Two-Point Calibration Done")
        print("Slope (m): %.4f" % self._slope)
        print("Intercept (c): %.4f" % self._intercept)
        print("=" * 40)

        return True

    def set_calibration(self, slope, intercept):
        self._slope = float(slope)
        self._intercept = float(intercept)
        self._save_calibration()

    def get_calibration(self):
        return (self._slope, self._intercept)

    # -------------------------------------------------

    def _save_calibration(self):
        try:
            f = open(self._cal_file, "w")
            json.dump({
                "slope": self._slope,
                "intercept": self._intercept
            }, f)
            f.close()
        except:
            print("Warning: cannot save calibration")

    def _load_calibration(self):
        try:
            f = open(self._cal_file, "r")
            data = json.load(f)
            f.close()
            self._slope = data.get("slope", self._slope)
            self._intercept = data.get("intercept", self._intercept)
            print("Calibration loaded")
        except:
            print("Using default calibration")

    # -------------------------------------------------

    def print_info(self):
        print("=" * 40)
        print("ADC raw:", self._raw_adc)
        print("Voltage: %.3f V" % self._voltage)
        print("pH: %.2f" % self._ph_value)
        print("=" * 40)


# =====================================================
# Simplified API
# =====================================================

_sensor = None

def init(pin=35):
    global _sensor
    _sensor = PHSensor()
    _sensor.set_pin(pin)
    _sensor.begin()
    return _sensor

def print_readings(pin=35):
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    _sensor.update()
    _sensor.print_info()
