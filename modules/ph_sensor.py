"""
PH Sensor Module for MicroPython (ESP32)
Analog pH Sensor with Linear Calibration

Based on Arduino example code
Ported to MicroPython by Cap_Apiluk

Features:
- Median-style filtering (Arduino-like)
- Two-point calibration (pH 4.0 and pH 7.0)
- Auto-save calibration to file
- Simple API
"""

import machine
import time
import json


class PHSensor:

    SAMPLE_COUNT = 10  # number of ADC samples

    def __init__(self):
        self._pin = None
        self._adc = None
        self._aref = 3.3
        self._adc_range = 4095

        # Default calibration (Arduino example)
        self._slope = -6.80
        self._intercept = 25.85

        self._ph_value = 0.0
        self._voltage = 0.0

        self._cal_file = "/ph_calibration.json"

    # -------------------------------------------------

    def set_pin(self, pin):
        self._pin = pin
        self._adc = machine.ADC(machine.Pin(pin))
        self._adc.atten(machine.ADC.ATTN_11DB)     # 0–3.3V
        self._adc.width(machine.ADC.WIDTH_12BIT)  # 0–4095

    # -------------------------------------------------

    def begin(self):
        if self._adc is None:
            raise ValueError("Please call set_pin() before begin()")

        self._load_calibration()
        print("PH Sensor Ready")
        print("Pin: GPIO", self._pin)
        print("Slope (m): %.2f" % self._slope)
        print("Intercept (c): %.2f" % self._intercept)

    # -------------------------------------------------
    # *** FIXED PART: Arduino-style ADC reading ***
    # -------------------------------------------------

    def _read_average(self):
        samples = []

        # Read ADC multiple times
        for _ in range(self.SAMPLE_COUNT):
            samples.append(self._adc.read())
            time.sleep_ms(10)

        # Arduino-style filtering:
        # sort → remove min & max → average
        if len(samples) >= 5:
            samples.sort()
            samples = samples[1:-1]

        avg = sum(samples) / len(samples)

        # Convert to voltage
        voltage = avg * self._aref / self._adc_range
        return voltage

    # -------------------------------------------------

    def update(self):
        self._voltage = self._read_average()
        self._ph_value = self._slope * self._voltage + self._intercept

    # -------------------------------------------------

    def get_ph_value(self):
        return round(self._ph_value, 2)

    def get_voltage(self):
        return round(self._voltage, 3)

    # -------------------------------------------------

    def calibrate_two_point(self, ph4_voltage, ph7_voltage):
        if ph4_voltage == ph7_voltage:
            print("Error: Same voltage for both points!")
            return False

        self._slope = (7.0 - 4.0) / (ph7_voltage - ph4_voltage)
        self._intercept = 4.0 - self._slope * ph4_voltage
        self._save_calibration()

        print("=" * 50)
        print("Two-Point Calibration Complete")
        print("pH 4.0 voltage: %.3f V" % ph4_voltage)
        print("pH 7.0 voltage: %.3f V" % ph7_voltage)
        print("Slope (m): %.4f" % self._slope)
        print("Intercept (c): %.4f" % self._intercept)
        print("=" * 50)
        return True

    # -------------------------------------------------

    def set_calibration(self, slope, intercept):
        self._slope = float(slope)
        self._intercept = float(intercept)
        self._save_calibration()

    def get_calibration(self):
        return (self._slope, self._intercept)

    # -------------------------------------------------

    def _save_calibration(self):
        try:
            data = {
                "slope": self._slope,
                "intercept": self._intercept
            }
            with open(self._cal_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print("Warning: cannot save calibration:", e)

    def _load_calibration(self):
        try:
            with open(self._cal_file, "r") as f:
                data = json.load(f)
                self._slope = data.get("slope", self._slope)
                self._intercept = data.get("intercept", self._intercept)
                print("Calibration loaded")
        except:
            print("Using default calibration")

    # -------------------------------------------------

    def reset_calibration(self):
        self._slope = -6.80
        self._intercept = 25.85
        self._save_calibration()

    # -------------------------------------------------

    def print_info(self):
        print("=" * 50)
        print("pH Sensor Readings")
        print("Pin: GPIO", self._pin)
        print("Voltage: %.3f V" % self._voltage)
        print("pH: %.2f" % self._ph_value)
        print("Slope: %.4f" % self._slope)
        print("Intercept: %.4f" % self._intercept)
        print("=" * 50)


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


def get_ph_value(pin=35):
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    _sensor.update()
    return _sensor.get_ph_value()


def get_voltage(pin=35):
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    _sensor.update()
    return _sensor.get_voltage()


def set_calibration(slope, intercept):
    global _sensor
    if _sensor is None:
        init()
    _sensor.set_calibration(slope, intercept)


def get_calibration():
    global _sensor
    if _sensor is None:
        init()
    return _sensor.get_calibration()


def calibrate_two_point(pin, ph4_voltage, ph7_voltage):
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    return _sensor.calibrate_two_point(ph4_voltage, ph7_voltage)


def print_readings(pin=35):
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    _sensor.update()
    _sensor.print_info()


def read_all_values(pin=35):
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    _sensor.update()
    slope, intercept = _sensor.get_calibration()
    return {
        "ph": _sensor.get_ph_value(),
        "voltage": _sensor.get_voltage(),
        "slope": slope,
        "intercept": intercept
    }
