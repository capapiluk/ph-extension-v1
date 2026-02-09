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
        // Block 4: Calibrate แบบ 2 จุด
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
        // Block 5: ดูค่า Calibration
        {
            xml: `
                <block type="ph_get_calibration"></block>
            `
        },
        // Block 6: อ่านค่าทั้งหมด
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
        // Block 7: แสดงค่า pH
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
        // Block 8: เช็คระดับ pH
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
        "/blocks/blocks.js",
        "/blocks/generators.js"
    ],
    // Python module
    modules: [
        {
            name: "ph_sensor",
            path: "/modules/ph_sensor.py"
        }
    ]
});