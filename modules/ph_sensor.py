"""
PH Sensor Module for MicroPython (ESP32)
Analog pH Sensor with Linear Calibration

Based on Arduino example code
Ported to MicroPython by Cap_Apiluk

Features:
- Median filtering for stable readings
- Two-point calibration (pH 4.0 and pH 7.0)
- Auto-save calibration to file
- Simple API
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
    SAMPLE_COUNT = 10  # Number of samples for averaging
    
    def __init__(self):
        """Initialize pH sensor"""
        self._pin = None
        self._adc = None
        self._aref = 3.3  # ESP32 voltage
        self._adc_range = 4095  # ESP32 12-bit ADC
        
        # Calibration parameters (y = mx + c)
        # Default values from Arduino example
        self._slope = -6.80  # m (slope)
        self._intercept = 25.85  # c (constant)
        
        # pH value
        self._ph_value = 0.0
        self._voltage = 0.0
        
        # Calibration file
        self._cal_file = "/ph_calibration.json"
        
    def set_pin(self, pin):
        """Set ADC pin number
        
        Args:
            pin: GPIO pin number (ADC capable: 32-39 for ESP32)
        """
        self._pin = pin
        self._adc = machine.ADC(machine.Pin(pin))
        self._adc.atten(machine.ADC.ATTN_11DB)  # 0-3.3V range
        self._adc.width(machine.ADC.WIDTH_12BIT)
        
    def begin(self):
        """Initialize sensor and load calibration"""
        if self._adc is None:
            raise ValueError("Please call set_pin() before begin()")
        
        # Load calibration
        self._load_calibration()
        print("PH Sensor Ready")
        print("Pin: GPIO", self._pin)
        print("Slope (m): %.2f" % self._slope)
        print("Intercept (c): %.2f" % self._intercept)
        
    def _read_average(self):
        """Read average analog value from multiple samples
        
        Returns:
            float: Average voltage
        """
        total = 0
        
        # Take multiple samples
        for _ in range(self.SAMPLE_COUNT):
            total += self._adc.read()
            time.sleep_ms(10)
        
        # Calculate average
        avg = total / self.SAMPLE_COUNT
        
        # Convert to voltage
        # Arduino: voltage = analog * (5.0 / 1023.0)
        # ESP32:   voltage = analog * (3.3 / 4095.0)
        voltage = avg * self._aref / self._adc_range
        
        return voltage
    
    def update(self):
        """Read sensor and calculate pH value
        
        Call this before getting pH value
        """
        if self._adc is None:
            raise ValueError("Sensor not initialized. Call begin() first.")
        
        # Read voltage
        self._voltage = self._read_average()
        
        # Calculate pH using linear equation: pH = m*V + c
        self._ph_value = self._slope * self._voltage + self._intercept
        
    def get_ph_value(self):
        """Get pH value
        
        Returns:
            float: pH value (0-14)
        """
        return round(self._ph_value, 2)
    
    def get_voltage(self):
        """Get current voltage reading
        
        Returns:
            float: Voltage in volts
        """
        return round(self._voltage, 3)
    
    def calibrate_two_point(self, ph4_voltage, ph7_voltage):
        """Calibrate using two-point calibration
        
        Args:
            ph4_voltage: Voltage reading at pH 4.0
            ph7_voltage: Voltage reading at pH 7.0
        
        Two-point calibration:
        - Point 1: (V1, pH1) = (ph4_voltage, 4.0)
        - Point 2: (V2, pH2) = (ph7_voltage, 7.0)
        - Slope: m = (pH2 - pH1) / (V2 - V1)
        - Intercept: c = pH1 - m*V1
        """
        # Calculate slope: m = (7.0 - 4.0) / (V2 - V1)
        if ph7_voltage == ph4_voltage:
            print("Error: Same voltage for both points!")
            return False
        
        self._slope = (7.0 - 4.0) / (ph7_voltage - ph4_voltage)
        
        # Calculate intercept: c = 4.0 - m*V1
        self._intercept = 4.0 - self._slope * ph4_voltage
        
        # Save calibration
        self._save_calibration()
        
        print("=" * 50)
        print("Two-Point Calibration Complete!")
        print("=" * 50)
        print(f"pH 4.0 voltage:  {ph4_voltage:.3f} V")
        print(f"pH 7.0 voltage:  {ph7_voltage:.3f} V")
        print(f"New Slope (m):   {self._slope:.4f}")
        print(f"New Intercept (c): {self._intercept:.4f}")
        print("=" * 50)
        
        return True
    
    def calibrate_interactive(self):
        """Interactive calibration wizard
        
        Step 1: Put sensor in pH 4.0 buffer
        Step 2: Put sensor in pH 7.0 buffer
        """
        print("=" * 50)
        print("Interactive pH Calibration")
        print("=" * 50)
        print()
        
        # Step 1: pH 4.0
        print("STEP 1: pH 4.0 Buffer Solution")
        print("Put sensor in pH 4.0 buffer and wait 30 seconds...")
        input("Press Enter when ready...")
        
        print("Reading pH 4.0...")
        time.sleep(2)
        self.update()
        ph4_voltage = self.get_voltage()
        print(f"pH 4.0 voltage: {ph4_voltage:.3f} V")
        print()
        
        # Step 2: pH 7.0
        print("STEP 2: pH 7.0 Buffer Solution")
        print("Rinse sensor with distilled water")
        print("Put sensor in pH 7.0 buffer and wait 30 seconds...")
        input("Press Enter when ready...")
        
        print("Reading pH 7.0...")
        time.sleep(2)
        self.update()
        ph7_voltage = self.get_voltage()
        print(f"pH 7.0 voltage: {ph7_voltage:.3f} V")
        print()
        
        # Calculate and save
        return self.calibrate_two_point(ph4_voltage, ph7_voltage)
    
    def set_calibration(self, slope, intercept):
        """Set calibration parameters manually
        
        Args:
            slope: Slope (m) of linear equation
            intercept: Intercept (c) of linear equation
        """
        self._slope = float(slope)
        self._intercept = float(intercept)
        self._save_calibration()
        print(f"Calibration set: m={self._slope:.4f}, c={self._intercept:.4f}")
    
    def get_calibration(self):
        """Get current calibration parameters
        
        Returns:
            tuple: (slope, intercept)
        """
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
            print(f"Warning: Could not save calibration: {e}")
    
    def _load_calibration(self):
        """Load calibration from file"""
        try:
            with open(self._cal_file, 'r') as f:
                data = json.load(f)
                self._slope = data.get('slope', -6.80)
                self._intercept = data.get('intercept', 25.85)
                print(f"Loaded calibration: m={self._slope:.2f}, c={self._intercept:.2f}")
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
        print(f"Pin:              GPIO {self._pin}")
        print(f"Voltage:          {self._voltage:.3f} V")
        print(f"pH:               {self._ph_value:.2f}")
        print(f"Slope (m):        {self._slope:.4f}")
        print(f"Intercept (c):    {self._intercept:.4f}")
        print("=" * 50)


# ========================================
# Simplified API Functions
# ========================================

_sensor = None

def init(pin=35):
    """Initialize pH sensor
    
    Args:
        pin: ADC pin number (default: 35)
        
    Returns:
        PHSensor: Sensor object
    """
    global _sensor
    _sensor = PHSensor()
    _sensor.set_pin(pin)
    _sensor.begin()
    return _sensor

def get_ph_value(pin):
    """Get pH value
    
    Args:
        pin: ADC pin number
        
    Returns:
        float: pH value (0-14)
    """
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    return _sensor.get_ph_value()

def get_voltage(pin):
    """Get voltage reading
    
    Args:
        pin: ADC pin number
        
    Returns:
        float: Voltage in volts
    """
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    return _sensor.get_voltage()

def set_calibration(slope, intercept):
    """Set calibration parameters
    
    Args:
        slope: Slope (m)
        intercept: Intercept (c)
    """
    global _sensor
    if _sensor is None:
        init()
    _sensor.set_calibration(slope, intercept)

def get_calibration():
    """Get calibration parameters
    
    Returns:
        tuple: (slope, intercept)
    """
    global _sensor
    if _sensor is None:
        init()
    return _sensor.get_calibration()

def calibrate_two_point(pin, ph4_voltage, ph7_voltage):
    """Two-point calibration
    
    Args:
        pin: ADC pin number
        ph4_voltage: Voltage at pH 4.0
        ph7_voltage: Voltage at pH 7.0
    """
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    return _sensor.calibrate_two_point(ph4_voltage, ph7_voltage)

def print_readings(pin):
    """Print all sensor readings
    
    Args:
        pin: ADC pin number
    """
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    _sensor.print_info()

def read_all_values(pin):
    """Read all sensor values as dictionary
    
    Args:
        pin: ADC pin number
        
    Returns:
        dict: All sensor values
    """
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
print(f"pH: {ph}")


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
    
    print(f"Voltage: {voltage:.3f} V | pH: {ph:.2f}")
    time.sleep(1000)


#############################################
# Example 3: Two-Point Calibration
#############################################

import ph_sensor

# Initialize
sensor = ph_sensor.init(pin=35)

# Method 1: Manual calibration
# Put sensor in pH 4.0 buffer, read voltage
sensor.update()
ph4_voltage = sensor.get_voltage()
print(f"pH 4.0 voltage: {ph4_voltage}")

# Put sensor in pH 7.0 buffer, read voltage
sensor.update()
ph7_voltage = sensor.get_voltage()
print(f"pH 7.0 voltage: {ph7_voltage}")

# Calibrate
sensor.calibrate_two_point(ph4_voltage, ph7_voltage)

# Method 2: Interactive calibration (with prompts)
sensor.calibrate_interactive()


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
    
    print(f"pH: {ph:.2f}", end=" ")
    
    if ph < TARGET_PH_MIN:
        print("⚠️ pH too low - Add pH UP")
        pump_ph_up.on()
        time.sleep(2)
        pump_ph_up.off()
        
    elif ph > TARGET_PH_MAX:
        print("⚠️ pH too high - Add pH DOWN")
        pump_ph_down.on()
        time.sleep(2)
        pump_ph_down.off()
        
    else:
        print("✅ pH optimal")
    
    time.sleep(300)  # Check every 5 minutes


#############################################
# pH Ranges for Reference
#############################################

# Hydroponics:
# - Lettuce, Herbs: 5.5-6.5
# - Tomatoes: 5.5-6.5
# - Strawberries: 5.5-6.5
# - Most vegetables: 5.5-6.5

# Aquarium:
# - Freshwater fish: 6.5-7.5
# - Marine fish: 8.0-8.4
# - Plants: 6.5-7.0

# Drinking water:
# - Safe range: 6.5-8.5
# - Ideal: 7.0-8.0
"""