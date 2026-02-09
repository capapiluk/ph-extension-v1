({
    name: "pH Sensor",
    description: "Analog pH Sensor with Two-Point Calibration (pH 4.0 & 7.0)",
    author: "Cap_Apiluk",
    category: "Sensor",
    version: "1.0.0",
    icon: "/static/icon.png",
    color: "#E74C3C",
    blocks: [
        // Block 1: อ่านค่า pH
        {
            xml: `
                <block type="ph_read_value">
                    <value name="pin">
                        <shadow type="math_number">
                            <field name="NUM">35</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        // Block 2: อ่านแรงดัน
        {
            xml: `
                <block type="ph_read_voltage">
                    <value name="pin">
                        <shadow type="math_number">
                            <field name="NUM">35</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        // Block 3: ตั้งค่า Calibration
        {
            xml: `
                <block type="ph_set_calibration">
                    <value name="slope">
                        <shadow type="math_number">
                            <field name="NUM">-6.80</field>
                        </shadow>
                    </value>
                    <value name="intercept">
                        <shadow type="math_number">
                            <field name="NUM">25.85</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        // Block 4: Calibrate แบบ 3 จุด (แม่นยำสูงสุด)
        {
            xml: `
                <block type="ph_calibrate_three_point">
                    <value name="pin">
                        <shadow type="math_number">
                            <field name="NUM">35</field>
                        </shadow>
                    </value>
                    <value name="ph4_voltage">
                        <shadow type="math_number">
                            <field name="NUM">2.5</field>
                        </shadow>
                    </value>
                    <value name="ph7_voltage">
                        <shadow type="math_number">
                            <field name="NUM">2.0</field>
                        </shadow>
                    </value>
                    <value name="ph9_voltage">
                        <shadow type="math_number">
                            <field name="NUM">1.5</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        // Block 5: Calibrate แบบ 2 จุด
        {
            xml: `
                <block type="ph_calibrate_two_point">
                    <value name="pin">
                        <shadow type="math_number">
                            <field name="NUM">35</field>
                        </shadow>
                    </value>
                    <value name="ph4_voltage">
                        <shadow type="math_number">
                            <field name="NUM">2.5</field>
                        </shadow>
                    </value>
                    <value name="ph7_voltage">
                        <shadow type="math_number">
                            <field name="NUM">2.0</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        // Block 6: Calibrate แบบ Offset (ง่ายที่สุด)
        {
            xml: `
                <block type="ph_calibrate_offset">
                    <value name="pin">
                        <shadow type="math_number">
                            <field name="NUM">35</field>
                        </shadow>
                    </value>
                    <value name="measured_ph">
                        <shadow type="math_number">
                            <field name="NUM">6.5</field>
                        </shadow>
                    </value>
                    <value name="actual_ph">
                        <shadow type="math_number">
                            <field name="NUM">7.0</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        // Block 7: ดูค่า Calibration
        {
            xml: `
                <block type="ph_get_calibration"></block>
            `
        },
        // Block 8: อ่านค่าทั้งหมด
        {
            xml: `
                <block type="ph_read_all_values">
                    <value name="pin">
                        <shadow type="math_number">
                            <field name="NUM">35</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        // Block 9: แสดงค่า pH
        {
            xml: `
                <block type="ph_print_readings">
                    <value name="pin">
                        <shadow type="math_number">
                            <field name="NUM">35</field>
                        </shadow>
                    </value>
                </block>
            `
        },
        // Block 10: เช็คระดับ pH
        {
            xml: `
                <block type="ph_check_level">
                    <value name="ph">
                        <shadow type="math_number">
                            <field name="NUM">7.0</field>
                        </shadow>
                    </value>
                </block>
            `
        }
    ],
    // JavaScript files
    js: [
        "/blocks.js",
        "/generators.js"
    ],
    // Python module
    modules: [
        {
            name: "ph_sensor",
            path: "/modules/ph_sensor.py"
        }
    ]
});