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
        """Calibrate using two-point calibration"""
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


# ========================================
# Example Usage
# ========================================
"""
#############################################
# Example 1: Simple Usage
#############################################

import ph_sensor

# Read pH value
ph = ph_sensor.get_ph_value(35)
print("pH: " + str(ph))


#############################################
# Example 2: Arduino Style (Class API)
#############################################

import ph_sensor
import time

# Setup
sensor = ph_sensor.init(pin=35)

# Loop
while True:
    sensor.update()
    ph = sensor.get_ph_value()
    voltage = sensor.get_voltage()
    
    print("Voltage: " + str(voltage) + " V | pH: " + str(ph))
    time.sleep(1)


#############################################
# Example 3: Two-Point Calibration
#############################################

import ph_sensor

# Initialize
sensor = ph_sensor.init(pin=35)

# Step 1: Put sensor in pH 4.0 buffer, wait 30 seconds
sensor.update()
ph4_voltage = sensor.get_voltage()
print("pH 4.0 voltage: " + str(ph4_voltage))

# Step 2: Rinse sensor, put in pH 7.0 buffer, wait 30 seconds
sensor.update()
ph7_voltage = sensor.get_voltage()
print("pH 7.0 voltage: " + str(ph7_voltage))

# Step 3: Calibrate
sensor.calibrate_two_point(ph4_voltage, ph7_voltage)


#############################################
# Example 4: Set Calibration Manually
#############################################

import ph_sensor

# If you know your calibration values
ph_sensor.set_calibration(slope=-5.70, intercept=21.34)

# Then read pH
ph = ph_sensor.get_ph_value(35)


#############################################
# Example 5: Hydroponics pH Control
#############################################

import ph_sensor
import machine
import time

# Setup
sensor = ph_sensor.init(pin=35)
pump_ph_down = machine.Pin(26, machine.Pin.OUT)
pump_ph_up = machine.Pin(27, machine.Pin.OUT)

# Target pH range
TARGET_PH_MIN = 5.5
TARGET_PH_MAX = 6.5

while True:
    sensor.update()
    ph = sensor.get_ph_value()
    
    print("pH: " + str(ph), end=" ")
    
    if ph < TARGET_PH_MIN:
        print("pH too low - Add pH UP")
        pump_ph_up.on()
        time.sleep(2)
        pump_ph_up.off()
        
    elif ph > TARGET_PH_MAX:
        print("pH too high - Add pH DOWN")
        pump_ph_down.on()
        time.sleep(2)
        pump_ph_down.off()
        
    else:
        print("pH optimal")
    
    time.sleep(300)  # Check every 5 minutes


#############################################
# pH Ranges for Reference
#############################################

# Hydroponics:
# - Lettuce, Herbs: 5.5-6.5
# - Tomatoes: 5.5-6.5
# - Most vegetables: 5.5-6.5

# Aquarium:
# - Freshwater fish: 6.5-7.5
# - Marine fish: 8.0-8.4

# Drinking water:
# - Safe range: 6.5-8.5
# - Ideal: 7.0-8.0
"""