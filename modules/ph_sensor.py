"""
PH Sensor Module for MicroPython (ESP32)
Analog pH Sensor with Linear Calibration

Compatible with MicroPython 1.6.0+
No f-strings, compatible with older versions

Based on Arduino example code
Ported to MicroPython by Cap_Apiluk
"""

import machine
import time
import json

class PHSensor:
    """
    Analog pH Sensor Class
    
    Features:
    - Median filtering (10 samples)
    - Linear calibration (y = mx + c)
    - Auto-save calibration
    - Three calibration methods: 2-point, 3-point, offset
    """
    
    # Constants
    SAMPLE_COUNT = 10
    
    def __init__(self):
        """Initialize pH sensor"""
        self._pin = None
        self._adc = None
        self._aref = 3.3
        self._adc_range = 4095
        
        # Calibration parameters (y = mx + c)
        self._slope = -6.80
        self._intercept = 25.85
        
        # pH value
        self._ph_value = 0.0
        self._voltage = 0.0
        
        # Calibration file
        self._cal_file = "/ph_calibration.json"
        
    def set_pin(self, pin):
        """Set ADC pin number"""
        self._pin = pin
        self._adc = machine.ADC(machine.Pin(pin))
        self._adc.atten(machine.ADC.ATTN_11DB)
        self._adc.width(machine.ADC.WIDTH_12BIT)
        
    def begin(self):
        """Initialize sensor and load calibration"""
        if self._adc is None:
            raise ValueError("Please call set_pin() before begin()")
        
        # Load calibration
        self._load_calibration()
        print("PH Sensor Ready")
        print("Pin: GPIO " + str(self._pin))
        print("Slope (m): " + str(round(self._slope, 2)))
        print("Intercept (c): " + str(round(self._intercept, 2)))
        
    def _read_average(self):
        """Read average analog value from multiple samples"""
        total = 0
        
        # Take multiple samples
        for _ in range(self.SAMPLE_COUNT):
            total += self._adc.read()
            time.sleep_ms(10)
        
        # Calculate average
        avg = total / self.SAMPLE_COUNT
        
        # Convert to voltage
        voltage = avg * self._aref / self._adc_range
        
        return voltage
    
    def update(self):
        """Read sensor and calculate pH value"""
        if self._adc is None:
            raise ValueError("Sensor not initialized. Call begin() first.")
        
        # Read voltage
        self._voltage = self._read_average()
        
        # Calculate pH: pH = m*V + c
        self._ph_value = self._slope * self._voltage + self._intercept
        
    def get_ph_value(self):
        """Get pH value"""
        return round(self._ph_value, 2)
    
    def get_voltage(self):
        """Get current voltage reading"""
        return round(self._voltage, 3)
    
    def calibrate_two_point(self, ph4_voltage, ph7_voltage):
        """Calibrate using two-point calibration
        
        Args:
            ph4_voltage: Voltage reading at pH 4.0
            ph7_voltage: Voltage reading at pH 7.0
        """
        # Calculate slope
        if ph7_voltage == ph4_voltage:
            print("Error: Same voltage for both points!")
            return False
        
        self._slope = (7.0 - 4.0) / (ph7_voltage - ph4_voltage)
        
        # Calculate intercept
        self._intercept = 4.0 - self._slope * ph4_voltage
        
        # Save calibration
        self._save_calibration()
        
        print("=" * 50)
        print("Two-Point Calibration Complete!")
        print("=" * 50)
        print("pH 4.0 voltage:  " + str(round(ph4_voltage, 3)) + " V")
        print("pH 7.0 voltage:  " + str(round(ph7_voltage, 3)) + " V")
        print("New Slope (m):   " + str(round(self._slope, 4)))
        print("New Intercept (c): " + str(round(self._intercept, 4)))
        print("=" * 50)
        
        return True
    
    def calibrate_three_point(self, ph1_voltage, ph2_voltage, ph3_voltage, 
                            ph1_value=4.0, ph2_value=7.0, ph3_value=9.0):
        """Calibrate using three-point calibration (best fit line)
        
        Uses least squares method to find best slope and intercept
        
        Args:
            ph1_voltage: Voltage reading at first pH point
            ph2_voltage: Voltage reading at second pH point
            ph3_voltage: Voltage reading at third pH point
            ph1_value: Actual pH value of first buffer (default: 4.0)
            ph2_value: Actual pH value of second buffer (default: 7.0)
            ph3_value: Actual pH value of third buffer (default: 9.0)
        """
        # Check for duplicate voltages
        if (ph1_voltage == ph2_voltage or ph2_voltage == ph3_voltage or 
            ph1_voltage == ph3_voltage):
            print("Error: Duplicate voltages detected!")
            return False
        
        # Three points: (V, pH)
        x_vals = [ph1_voltage, ph2_voltage, ph3_voltage]
        y_vals = [ph1_value, ph2_value, ph3_value]
        
        # Calculate means
        x_mean = sum(x_vals) / 3.0
        y_mean = sum(y_vals) / 3.0
        
        # Calculate slope using least squares
        numerator = 0
        denominator = 0
        for i in range(3):
            numerator += (x_vals[i] - x_mean) * (y_vals[i] - y_mean)
            denominator += (x_vals[i] - x_mean) * (x_vals[i] - x_mean)
        
        if denominator == 0:
            print("Error: Cannot calculate slope!")
            return False
        
        self._slope = numerator / denominator
        self._intercept = y_mean - self._slope * x_mean
        
        # Save calibration
        self._save_calibration()
        
        print("=" * 50)
        print("Three-Point Calibration Complete!")
        print("=" * 50)
        print("pH " + str(ph1_value) + " voltage:  " + str(round(ph1_voltage, 3)) + " V")
        print("pH " + str(ph2_value) + " voltage:  " + str(round(ph2_voltage, 3)) + " V")
        print("pH " + str(ph3_value) + " voltage:  " + str(round(ph3_voltage, 3)) + " V")
        print("New Slope (m):   " + str(round(self._slope, 4)))
        print("New Intercept (c): " + str(round(self._intercept, 4)))
        print("=" * 50)
        
        return True
    def calibrate_offset(self, measured_ph, actual_ph):
        """Calibrate using offset method (single point)
        
        Adjusts intercept only, keeps slope the same
        Useful for quick calibration with one buffer solution
        
        Args:
            measured_ph: pH value that sensor currently reads
            actual_ph: Actual pH value of the buffer solution
        """
        # Calculate the offset
        offset = actual_ph - measured_ph
        
        # Adjust intercept only (slope stays the same)
        self._intercept = self._intercept + offset
        
        # Save calibration
        self._save_calibration()
        
        print("=" * 50)
        print("Offset Calibration Complete!")
        print("=" * 50)
        print("Measured pH:      " + str(round(measured_ph, 2)))
        print("Actual pH:        " + str(round(actual_ph, 2)))
        print("Offset:           " + str(round(offset, 2)))
        print("New Intercept (c): " + str(round(self._intercept, 4)))
        print("Slope (m):        " + str(round(self._slope, 4)) + " (unchanged)")
        print("=" * 50)
        
        return True
    
    def set_calibration(self, slope, intercept):
        """Set calibration parameters manually"""
        self._slope = float(slope)
        self._intercept = float(intercept)
        self._save_calibration()
        print("Calibration set: m=" + str(round(self._slope, 4)) + ", c=" + str(round(self._intercept, 4)))
    
    def get_calibration(self):
        """Get current calibration parameters"""
        return (self._slope, self._intercept)
    
    def _save_calibration(self):
        """Save calibration to file"""
        try:
            data = {
                'slope': self._slope,
                'intercept': self._intercept,
                'calibrated_at': time.time()
            }
            with open(self._cal_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print("Warning: Could not save calibration: " + str(e))
    
    def _load_calibration(self):
        """Load calibration from file"""
        try:
            with open(self._cal_file, 'r') as f:
                data = json.load(f)
                self._slope = data.get('slope', -6.80)
                self._intercept = data.get('intercept', 25.85)
                print("Loaded calibration: m=" + str(round(self._slope, 2)) + ", c=" + str(round(self._intercept, 2)))
        except:
            print("No calibration file found, using default values")
            self._slope = -6.80
            self._intercept = 25.85
    
    def reset_calibration(self):
        """Reset to default calibration"""
        self._slope = -6.80
        self._intercept = 25.85
        self._save_calibration()
        print("Calibration reset to default")
    
    def print_info(self):
        """Print sensor information"""
        print("=" * 50)
        print("pH Sensor Readings")
        print("=" * 50)
        print("Pin:              GPIO " + str(self._pin))
        print("Voltage:          " + str(round(self._voltage, 3)) + " V")
        print("pH:               " + str(round(self._ph_value, 2)))
        print("Slope (m):        " + str(round(self._slope, 4)))
        print("Intercept (c):    " + str(round(self._intercept, 4)))
        print("=" * 50)


# ========================================
# Simplified API Functions
# ========================================

_sensor = None

def init(pin=35):
    """Initialize pH sensor"""
    global _sensor
    _sensor = PHSensor()
    _sensor.set_pin(pin)
    _sensor.begin()
    return _sensor

def get_ph_value(pin):
    """Get pH value"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    return _sensor.get_ph_value()

def get_voltage(pin):
    """Get voltage reading"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    return _sensor.get_voltage()

def set_calibration(slope, intercept):
    """Set calibration parameters"""
    global _sensor
    if _sensor is None:
        init()
    _sensor.set_calibration(slope, intercept)

def get_calibration():
    """Get calibration parameters"""
    global _sensor
    if _sensor is None:
        init()
    return _sensor.get_calibration()

def calibrate_two_point(pin, ph4_voltage, ph7_voltage):
    """Two-point calibration"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    return _sensor.calibrate_two_point(ph4_voltage, ph7_voltage)

def calibrate_three_point(pin, ph4_voltage, ph7_voltage, ph9_voltage):
    """Three-point calibration"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    return _sensor.calibrate_three_point(ph4_voltage, ph7_voltage, ph9_voltage)

def calibrate_offset(pin, measured_ph, actual_ph):
    """Offset calibration"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    return _sensor.calibrate_offset(measured_ph, actual_ph)

def print_readings(pin):
    """Print all sensor readings"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    _sensor.print_info()

def read_all_values(pin):
    """Read all sensor values as dictionary"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    
    slope, intercept = _sensor.get_calibration()
    
    return {
        'ph': _sensor.get_ph_value(),
        'voltage': _sensor.get_voltage(),
        'slope': slope,
        'intercept': intercept
    }