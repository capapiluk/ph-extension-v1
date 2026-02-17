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
        # Default สำหรับ pH 4.01 และ pH 6.86 buffer
        self._slope = -3.5        # Slope ที่เหมาะสมสำหรับ pH 4.01-6.86
        self._intercept = 18.5    # Intercept ที่เหมาะสมสำหรับ pH buffer มาตรฐาน
        
        # pH value
        self._ph_value = 0.0
        self._voltage = 0.0
        
        # Error detection
        self._sensor_status = "unknown"
        self._error_message = ""
        
        # Voltage thresholds for error detection
        # หาก pH buffer 4.0 ให้แรงดันสูงเกิน 3.3V 
        # สามารถหมุนตัวต้านทาน (potentiometer) ลงเพื่อลดแรงดันได้
        # *** สำคัญ: หลังปรับตัวต้านทานแล้ว ต้อง calibrate ใหม่เสมอ ***
        self._max_valid_voltage = 3.3   # ESP32 VREF = 3.3V, above this = sensor dry
        
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
        """Read average analog value from multiple samples with basic error detection"""
        total = 0
        
        # Take multiple samples
        for _ in range(self.SAMPLE_COUNT):
            raw = self._adc.read()
            total += raw
            time.sleep_ms(10)
        
        # Calculate average
        avg = total / self.SAMPLE_COUNT
        
        # Convert to voltage
        voltage = avg * self._aref / self._adc_range
        
        # Simple sensor check
        self._check_sensor_status(voltage)
        
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
    
    def calibrate_two_point(self, ph401_voltage, ph686_voltage):
        """Calibrate using two-point calibration with standard pH buffers
        
        Uses standard pH buffer values: 4.01 and 6.86
        More accurate and stable than older buffer combinations
        
        Args:
            ph401_voltage: Voltage reading at pH 4.01 buffer
            ph686_voltage: Voltage reading at pH 6.86 buffer
        """
        # Check for same voltage (would cause division by zero)
        if ph686_voltage == ph401_voltage:
            print("Error: Same voltage for both points!")
            return False
        
        # Calculate slope using standard pH values
        self._slope = (6.86 - 4.01) / (ph686_voltage - ph401_voltage)
        
        # Calculate intercept
        self._intercept = 4.01 - self._slope * ph401_voltage
        
        # Save calibration
        self._save_calibration()
        
        print("=" * 50)
        print("Two-Point Calibration Complete!")
        print("=" * 50)
        print("pH 4.01 voltage:  " + str(round(ph401_voltage, 3)) + " V")
        print("pH 6.86 voltage:  " + str(round(ph686_voltage, 3)) + " V")
        print("New Slope (m):    " + str(round(self._slope, 4)))
        print("New Intercept (c): " + str(round(self._intercept, 4)))
        print("=" * 50)
        
        return True
    
    def calibrate_three_point(self, ph1_voltage, ph2_voltage, ph3_voltage, 
                            ph1_value=4.01, ph2_value=6.86, ph3_value=9.18):
        """Calibrate using three-point calibration (best fit line)
        
        Uses least squares method to find best slope and intercept
        Uses standard pH buffer values: 4.01, 6.86, 9.18
        
        Args:
            ph1_voltage: Voltage reading at pH 4.01 buffer
            ph2_voltage: Voltage reading at pH 6.86 buffer  
            ph3_voltage: Voltage reading at pH 9.18 buffer
            ph1_value: Actual pH value of first buffer (default: 4.01)
            ph2_value: Actual pH value of second buffer (default: 6.86)
            ph3_value: Actual pH value of third buffer (default: 9.18)
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
                self._slope = data.get('slope', -3.5)
                self._intercept = data.get('intercept', 18.5)
                print("Loaded calibration: m=" + str(round(self._slope, 2)) + ", c=" + str(round(self._intercept, 2)))
        except:
            print("No calibration file found, using default values")
            # Default สำหรับ pH buffer มาตรฐาน 4.01 และ 6.86
            self._slope = -3.5
            self._intercept = 18.5
    
    def reset_calibration(self):
        """Reset to default calibration for standard pH buffers"""
        self._slope = -3.5
        self._intercept = 18.5
        self._save_calibration()
        print("Calibration reset to default (optimized for pH 4.01 & 6.86 buffers)")
    
    def _check_sensor_status(self, voltage):
        """Simple sensor status check"""
        # Check if sensor is dry (not in solution)
        if voltage > self._max_valid_voltage:
            self._sensor_status = "error"
            self._error_message = "Sensor not in solution (" + str(round(voltage, 2)) + "V) - Please submerge electrode"
        else:
            # Sensor looks OK
            self._sensor_status = "ok"
            self._error_message = ""
    
    def get_sensor_status(self):
        """Get sensor status and error message"""
        return (self._sensor_status, self._error_message)
    
    def is_sensor_ok(self):
        """Check if sensor is working properly"""
        return self._sensor_status == "ok"
    
    def print_info(self):
        """Print sensor information with status"""
        print("=" * 50)
        print("pH Sensor Readings")
        print("=" * 50)
        print("Pin:              GPIO " + str(self._pin))
        print("Voltage:          " + str(round(self._voltage, 3)) + " V")
        print("pH:               " + str(round(self._ph_value, 2)))
        print("Status:           " + self._sensor_status.upper())
        if self._error_message:
            print("Message:          " + self._error_message)
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

def calibrate_two_point(pin, ph401_voltage, ph686_voltage):
    """Two-point calibration with standard pH buffers"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    return _sensor.calibrate_two_point(ph401_voltage, ph686_voltage)

def calibrate_three_point(pin, ph401_voltage, ph686_voltage, ph918_voltage):
    """Three-point calibration with standard pH buffers"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    return _sensor.calibrate_three_point(ph401_voltage, ph686_voltage, ph918_voltage)

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

def is_sensor_ok(pin):
    """Check if sensor is working properly"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    return _sensor.is_sensor_ok()

def get_sensor_status(pin):
    """Get sensor status and error message"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    status, message = _sensor.get_sensor_status()
    return {
        'status': status,
        'message': message
    }

def check_sensor(pin):
    """Check sensor and print status"""
    global _sensor
    if _sensor is None or _sensor._pin != pin:
        init(pin)
    
    _sensor.update()
    status, message = _sensor.get_sensor_status()
    
    if status == "ok":
        print("✅ Sensor OK - pH: " + str(round(_sensor.get_ph_value(), 2)))
    elif status == "warning":  
        print("⚠️  Warning: " + message)
    else:  # error
        print("❌ Error: " + message)
    
    return status == "ok"