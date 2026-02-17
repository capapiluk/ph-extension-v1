// ========================================
// pH Sensor Python Generators
// ========================================

// Generator 1: อ่านค่า pH
Blockly.Python['ph_read_value'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_ATOMIC) || '35';
    
    var code = 'ph_sensor.get_ph_value(' + pin + ')';
    return [code, Blockly.Python.ORDER_ATOMIC];
};

// Generator 2: อ่านแรงดัน
Blockly.Python['ph_read_voltage'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_ATOMIC) || '35';
    
    var code = 'ph_sensor.get_voltage(' + pin + ')';
    return [code, Blockly.Python.ORDER_ATOMIC];
};

// Generator 3: ตั้งค่า Calibration
Blockly.Python['ph_set_calibration'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var slope = Blockly.Python.valueToCode(block, 'slope', Blockly.Python.ORDER_ATOMIC) || '-3.5';
    var intercept = Blockly.Python.valueToCode(block, 'intercept', Blockly.Python.ORDER_ATOMIC) || '18.5';
    
    var code = 'ph_sensor.set_calibration(' + slope + ', ' + intercept + ')\n';
    return code; 
};

// Generator 4: Calibrate แบบ 3 จุด
Blockly.Python['ph_calibrate_three_point'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_ATOMIC) || '35';
    var ph401_voltage = Blockly.Python.valueToCode(block, 'ph401_voltage', Blockly.Python.ORDER_ATOMIC) || '2.8';
    var ph686_voltage = Blockly.Python.valueToCode(block, 'ph686_voltage', Blockly.Python.ORDER_ATOMIC) || '2.1';
    var ph918_voltage = Blockly.Python.valueToCode(block, 'ph918_voltage', Blockly.Python.ORDER_ATOMIC) || '1.4';
    
    var code = 'ph_sensor.calibrate_three_point(' + pin + ', ' + ph401_voltage + ', ' + ph686_voltage + ', ' + ph918_voltage + ')\n';
    return code;
};

// Generator 5: Calibrate แบบ 2 จุด
Blockly.Python['ph_calibrate_two_point'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_ATOMIC) || '35';
    var ph401_voltage = Blockly.Python.valueToCode(block, 'ph401_voltage', Blockly.Python.ORDER_ATOMIC) || '2.8';
    var ph686_voltage = Blockly.Python.valueToCode(block, 'ph686_voltage', Blockly.Python.ORDER_ATOMIC) || '2.1';
    
    var code = 'ph_sensor.calibrate_two_point(' + pin + ', ' + ph401_voltage + ', ' + ph686_voltage + ')\n';
    return code;
};

// Generator 6: Calibrate แบบ Offset
Blockly.Python['ph_calibrate_offset'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_ATOMIC) || '35';
    var measured_ph = Blockly.Python.valueToCode(block, 'measured_ph', Blockly.Python.ORDER_ATOMIC) || '6.5';
    var actual_ph = Blockly.Python.valueToCode(block, 'actual_ph', Blockly.Python.ORDER_ATOMIC) || '7.0';
    
    var code = 'ph_sensor.calibrate_offset(' + pin + ', ' + measured_ph + ', ' + actual_ph + ')\n';
    return code;
};

// Generator 7: ดูค่า Calibration
Blockly.Python['ph_get_calibration'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    
    var code = 'ph_sensor.get_calibration()';
    return [code, Blockly.Python.ORDER_ATOMIC];
};

// Generator 8: อ่านค่าทั้งหมด
Blockly.Python['ph_read_all_values'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_ATOMIC) || '35';
    
    var code = 'ph_sensor.read_all_values(' + pin + ')';
    return [code, Blockly.Python.ORDER_ATOMIC];
};

// Generator 9: แสดงค่า pH
Blockly.Python['ph_print_readings'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_ATOMIC) || '35';
    
    var code = 'ph_sensor.print_readings(' + pin + ')\n';
    return code;
};

// Generator 10: เช็คระดับ pH
Blockly.Python['ph_check_level'] = function(block) {
    var ph = Blockly.Python.valueToCode(block, 'ph', Blockly.Python.ORDER_ATOMIC) || '7.0';
    
    var code = '("กรด" if ' + ph + ' < 7.0 else "กลาง" if ' + ph + ' == 7.0 else "ด่าง")';
    return [code, Blockly.Python.ORDER_CONDITIONAL];
};

// Generator 11: ตรวจสอบสถานะ Sensor
Blockly.Python['ph_check_sensor'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_ATOMIC) || '35';
    
    var code = 'ph_sensor.is_sensor_ok(' + pin + ')';
    return [code, Blockly.Python.ORDER_ATOMIC];
};

// Generator 12: แสดงสถานะ Sensor
Blockly.Python['ph_show_sensor_status'] = function(block) {
    Blockly.Python.definitions_['import_ph_sensor'] = 'import ph_sensor';
    var pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_ATOMIC) || '35';
    
    var code = 'ph_sensor.check_sensor(' + pin + ')\n';
    return code;
};