// ========================================
// pH Sensor Blocks Definition
// ========================================

// Block 1: อ่านค่า pH
Blockly.Blocks['ph_read_value'] = {
  init: function() {
    this.appendValueInput("pin")
        .setCheck("Number")
        .appendField("อ่านค่า pH ขา");
    this.setOutput(true, "Number");
    this.setColour("#E74C3C"); // สีแดง (pH indicator color)
    this.setTooltip("อ่านค่า pH (0-14)");
    this.setHelpUrl("");
  }
};

// Block 2: อ่านค่าแรงดัน
Blockly.Blocks['ph_read_voltage'] = {
  init: function() {
    this.appendValueInput("pin")
        .setCheck("Number")
        .appendField("อ่านแรงดัน pH Sensor ขา");
    this.setOutput(true, "Number");
    this.setColour("#9B59B6"); // สีม่วง
    this.setTooltip("อ่านแรงดันไฟฟ้าจากเซ็นเซอร์ pH (V)");
    this.setHelpUrl("");
  }
};

// Block 3: ตั้งค่า Calibration
Blockly.Blocks['ph_set_calibration'] = {
  init: function() {
    this.appendValueInput("slope")
        .setCheck("Number")
        .appendField("ตั้งค่า pH Calibration Slope (m)");
    this.appendValueInput("intercept")
        .setCheck("Number")
        .appendField("Intercept (c)");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#E67E22"); // สีส้ม
    this.setTooltip("ตั้งค่าสมการ pH: pH = m*V + c");
    this.setHelpUrl("");
  }
};

// Block 4: Calibrate แบบ 2 จุด
Blockly.Blocks['ph_calibrate_two_point'] = {
  init: function() {
    this.appendValueInput("pin")
        .setCheck("Number")
        .appendField("Calibrate pH ขา");
    this.appendValueInput("ph4_voltage")
        .setCheck("Number")
        .appendField("แรงดัน pH 4.0 (V)");
    this.appendValueInput("ph7_voltage")
        .setCheck("Number")
        .appendField("แรงดัน pH 7.0 (V)");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#27AE60"); // สีเขียว
    this.setTooltip("Calibrate pH sensor ด้วยสารละลาย pH 4.0 และ pH 7.0");
    this.setHelpUrl("");
  }
};

// Block 5: ดูค่า Calibration
Blockly.Blocks['ph_get_calibration'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("ดูค่า pH Calibration");
    this.setOutput(true, "Array");
    this.setColour("#95A5A6"); // สีเทา
    this.setTooltip("คืนค่า [slope, intercept]");
    this.setHelpUrl("");
  }
};

// Block 6: อ่านค่าทั้งหมด
Blockly.Blocks['ph_read_all_values'] = {
  init: function() {
    this.appendValueInput("pin")
        .setCheck("Number")
        .appendField("อ่านค่า pH ทั้งหมด (Dict) ขา");
    this.setOutput(true, "Dictionary");
    this.setColour("#3498DB"); // สีฟ้า
    this.setTooltip("อ่านค่า pH, Voltage, Slope, Intercept พร้อมกัน");
    this.setHelpUrl("");
  }
};

// Block 7: แสดงค่า pH
Blockly.Blocks['ph_print_readings'] = {
  init: function() {
    this.appendValueInput("pin")
        .setCheck("Number")
        .appendField("แสดงค่า pH Sensor ขา");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#34495E"); // สีน้ำเงินเข้ม
    this.setTooltip("แสดงค่าทั้งหมดแบบสวยงาม");
    this.setHelpUrl("");
  }
};

// Block 8: เช็คระดับ pH
Blockly.Blocks['ph_check_level'] = {
  init: function() {
    this.appendValueInput("ph")
        .setCheck("Number")
        .appendField("ตรวจสอบระดับ pH");
    this.setOutput(true, "String");
    this.setColour("#16A085"); // สีเขียวน้ำทะเล
    this.setTooltip("คืนค่า: 'กรด', 'กลาง', หรือ 'ด่าง'");
    this.setHelpUrl("");
  }
};