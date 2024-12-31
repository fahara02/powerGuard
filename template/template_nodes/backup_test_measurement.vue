<template>
    <div class="backup-test-ui">
        <h1>Backup Test Control</h1>
        <div>
            <div>
                <!-- Setting ID Dropdown -->
                <label for="setting_id">Report Settings ID:</label>
                <select v-model="formData.setting_id" id="setting_id" required>
                    <option v-for="id in settingOptions" :key="id" :value="id">{{ id }}</option>
                </select>

                <label for="load-type">Load Type:</label>
                <select v-model="formData.loadType" id="load-type" required>
                    <option v-for="(value, key) in loadTypes" :key="key" :value="value">
                        {{ key }}
                    </option>
                </select>
            </div>
            <div>
                <!-- MODE -->
                <label for="mode">Mode:</label>
                <select v-model="formData.mode" id="mode" required>
                    <option v-for="(value, key) in MODE" :key="value" :value="value">
                        {{ key }}
                    </option>
                </select>
            </div>

            <div>
                <label for="load-percentage">Load Percentage:</label>
                <input type="number" v-model.number="formData.loadPercentage" id="load-percentage" required min="0"
                    max="100" />
            </div>

            <!-- Display Setting Data -->
            <div v-if="selectedSetting">
                <h3>Setting Details:</h3>
                <p><strong>Report Id:</strong> {{ selectedSetting.report_id }}</p>
                <p><strong>Standard:</strong> {{ selectedSetting.standard }}</p>
                <p><strong>UPS Model:</strong> {{ selectedSetting.ups_model }}</p>
                <p><strong>Client Name:</strong> {{ selectedSetting.client_name }}</p>
                <p><strong>Brand Name:</strong> {{ selectedSetting.brand_name }}</p>
                <p><strong>Test Engineer Name:</strong> {{ selectedSetting.test_engineer_name }}</p>
                <p><strong>Test Approval Name:</strong> {{ selectedSetting.test_approval_name }}</p>
                <p><strong>UPS SPEC ID:</strong> {{ selectedSetting.spec_id }}</p>
            </div>

            <div class="buttons">
                <button type="button" @click="startBackupTest" :disabled="backupTestRunning">Start Test</button>

                <button type="button" @click="stopBackupTest" :disabled="!backupTestRunning">Stop Test</button>
            </div>
        </div>

        <div v-if="backupTestRunning" class="test-status">
            <p>Test running... Backup time: {{ BackUpTestData.BackupTime }} seconds</p>
        </div>
        <div v-if="!backupTestRunning && BackUpTestData.BackupTime > 0" class="test-result">
            <h2>Test Result</h2>
            <p>Total Backup Time: {{ BackUpTestData.BackupTime }} seconds</p>
            <ul>
                <li v-for="(value, key) in BackUpTestData" :key="key">
                    {{ key }}: {{ value }}
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            test_duration: 0,
            test_report: null,
            latest_settings_id: 0,
            setting: [],
            TestResult: {
                TEST_FAILED: 0,
                TEST_PENDING: 1,
                TEST_SUCCESSFUL: 2,
                USER_OBSERVATION: 3,
            },
            loadTypes: {
                LINEAR: 0,
                NON_LINEAR: 1,
            },
            MODE: {
                NORMAL_MODE: 0,
                STORAGE_MODE: 1,
                FAULT_MODE: 2,
                ALARM_MODE: 4,
            },
            formData: {
                setting_id: 0,
                loadType: 0,
                mode: 0,
                loadPercentage: 0,
            },
            backupTestRunning: false,
            cmd_mains_input: 1,
            BackUpTestData: {
                BackupTime: 0,
                sense_mains_input: 1,
                sense_ups_output: 0,
                alarm_status: 0,
                inputPdata: {},
                outputPdata: {},
            },

            measurements: [],
        };
    },
    computed: {
        settingOptions() {
            return this.setting.map((setting) => setting.id || 0).sort((a, b) => a - b);
        },
        selectedSetting() {
            return this.setting.find((setting) => setting.id === this.formData.setting_id) || null;
        },
    },
    methods: {

        // updateBackUpTestData(payload) {
        //     if (payload && payload.BackUpTestData) {
        //       this.BackUpTestData = { ...this.BackUpTestData, ...payload.BackUpTestData };
        //     }
        //   },

        generateMeasurement() {
            const uniqueId = Math.floor(Math.random() * 9000000000) + 1000000000;
            const timestamp = new Date();

            return {
                m_unique_id: uniqueId,
                time_stamp: {
                    seconds: Math.floor(timestamp.getTime() / 1000),
                    nanos: timestamp.getMilliseconds() * 1000000,
                },
                name: "Measurement Backup test",
                mode: this.formData.mode,
                phase_name: "Phase A",
                load_type: this.formData.loadType,
                step_id: 0,
                load_percentage: this.formData.loadPercentage,
                power_measures: [this.BackUpTestData.inputPdata, this.BackUpTestData.outputPdata],
                steady_state_voltage_tol: 0,
                voltage_dc_component: 0,
                load_pf_deviation: 0,
                switch_time_ms: 0,
                run_interval_sec: 10,
                backup_time_sec: 0,
                overload_time_sec: 0,
                temperature_1: 0,
                temperature_2: 0,
            };
        },
        createTestReport() {
            const report = {
                settings: this.selectedSetting || {}, // Use the currently selected settings
                test_name: 9, // BackupTest enum value
                test_description: "Backup Test Report",
                measurements: this.measurements, // Use collected measurements
                test_result: 3, // USER OBSERVATION
            };

            // Log the report for debugging or send it to the server
            console.log("Generated Test Report:", report);

            // Emit the report via socket (if required)
            this.$socket.emit('test-report', { report });

            return report;
        },


        updateBackUpTestData(payload) {
            if (payload && payload.BackUpTestData) {
                const { BackUpTestData } = payload;

                // Ensure all properties are updated or set to defaults if undefined
                this.BackUpTestData = {
                    BackupTime: BackUpTestData.BackupTime ?? 0,
                    sense_mains_input: BackUpTestData.sense_mains_input ?? 1,
                    sense_ups_output: BackUpTestData.sense_ups_output ?? 0,
                    alarm_status: BackUpTestData.alarm_status ?? 0,
                    inputPdata: BackUpTestData.inputPdata || {},
                    outputPdata: BackUpTestData.outputPdata || {},
                };

                // Log to ensure data was updated properly
                console.log("Updated BackUpTestData:", this.BackUpTestData);
            } else {
                console.warn("Invalid payload or missing BackUpTestData:", payload);
            }
        },
        updateSettingData(payload) {
            if (payload && payload.SettingData && Array.isArray(payload.SettingData.settings)) {
                this.setting = payload.SettingData.settings;
            } else {
                console.warn("No valid settings data received in payload", payload);
                this.setting = [];
            }
        },

        createRunCmds(overrides = {}) {
            return {
                alarm_status: this.BackUpTestData.alarm_status,
                cmd_mains_input: this.cmd_mains_input,
                backupTestRunning: this.backupTestRunning,
                BackupTime: this.BackUpTestData.BackupTime,
                additionalData: {
                    setting_id: this.formData.setting_id,
                    loadType: this.formData.loadType,
                    stepId: this.formData.stepId,
                    loadPercentage: this.formData.loadPercentage,
                },
                ...overrides,
            };
        },
        sendMessage(payload) {
            // Emit a message to Node-RED using socket
            this.$socket.emit('msg-output:' + this.id, { payload });
        },
        async delay(ms) {
            return new Promise((resolve) => setTimeout(resolve, ms));
        },
        async startBackupTest() {
            this.backupTestRunning = true;
            this.BackUpTestData.alarm_status = 1;
            this.send({ topic: 'commands', payload: this.createRunCmds() });

            try {
                await this.delay(2000);
                this.BackUpTestData.alarm_status = 0;
                this.send({
                    topic: 'commands', payload: this.createRunCmds({
                        alarm_status: 1

                    })
                });
                await this.delay(2000);
                this.send({
                    topic: 'commands', payload: this.createRunCmds({
                        alarm_status: 0,
                        cmd_mains_input: 0,
                    })
                });
                await this.delay(2000);
                while (this.BackUpTestData.sense_mains_input !== 0) {
                    await this.delay(100);
                    if (!this.backupTestRunning) throw new Error("Test stopped");
                }

                while (this.BackUpTestData.sense_ups_output !== 1) {
                    await this.delay(100);
                    if (!this.backupTestRunning) throw new Error("Test stopped");
                }

                while (this.BackUpTestData.sense_ups_output === 1) {
                    await this.delay(1000);
                    this.BackUpTestData.BackupTime++;
                    this.test_duration++;
                    if (this.test_duration > 10) {
                        this.test_duration = 0;
                        const measurement = this.generateMeasurement();
                        this.measurements.push(measurement);
                    }

                    this.send({ topic: 'commands', payload: this.createRunCmds() });
                }
            } catch (error) {
                console.error(error.message);
            } finally {
                this.stopBackupTest();
            }
        },
        stopBackupTest() {
            this.backupTestRunning = false;
            this.send({
                payload: this.createRunCmds({
                    alarm_status: 0,
                    cmd_mains_input: 1,
                }),
            });
            this.BackUpTestData = {
                ...this.BackUpTestData,
                alarm_status: 0,
                sense_mains_input: 1,
            };
            this.testReport = this.createTestReport();
            this.send({ topic: 'report', payload: this.testReport });
        },
    },
    mounted() {
        this.$watch("msg", (newMsg) => {
            if (newMsg && newMsg.payload) {
                this.updateBackUpTestData(newMsg.payload);
                this.updateSettingData(newMsg.payload);
            }
        });
    },
};
</script>


<style scoped>
.backup-test-ui {
    max-width: 450px;
    margin: 30px auto;
    font-family: 'Arial', sans-serif;
    background-color: #f4f6f9;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h1 {
    font-size: 24px;
    color: #333;
    margin-bottom: 20px;
    text-align: center;
}

label {
    font-size: 14px;
    color: #555;
    display: block;
    margin-bottom: 5px;
}

input,
select {
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    border-radius: 5px;
    border: 1px solid #ccc;
    font-size: 14px;
    background-color: #fff;
    transition: border-color 0.3s, box-shadow 0.3s;
}

input:focus,
select:focus {
    border-color: #007bff;
    box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

.buttons {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    margin-top: 20px;
}

button {
    padding: 12px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.3s;
}

button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

button:hover {
    background-color: #0056b3;
    transform: scale(1.05);
}

button:active {
    background-color: #004085;
}

.test-status,
.test-result {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
}

.test-status p,
.test-result p {
    font-size: 16px;
    color: #333;
}

.test-result h2 {
    font-size: 20px;
    color: #007bff;
    margin-bottom: 10px;
}

ul {
    list-style-type: none;
    padding-left: 0;
}

li {
    font-size: 14px;
    color: #555;
    margin-bottom: 8px;
}
</style>