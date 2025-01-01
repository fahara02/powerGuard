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
                TEST_FAILED: "TEST_FAILED",
                TEST_PENDING: "TEST_PENDING",
                TEST_SUCCESSFUL: "TEST_SUCCESSFUL",
                USER_OBSERVATION: "USER_OBSERVATION",
            },
            loadTypes: {
                LINEAR: "LINEAR",
                NON_LINEAR: "NON_LINEAR",
            },
            MODE: {
                NORMAL_MODE: "NORMAL_MODE",
                STORAGE_MODE: "STORAGE_MODE",
                FAULT_MODE: "FAULT_MODE",
                ALARM_MODE: "ALARM_MODE",
            },
            formData: {
                setting_id: 0,
                loadType: "LINEAR",  // default load type as string
                mode: "NORMAL_MODE", // default mode as string
                loadPercentage: 0,
            },
            backupTestRunning: false,

            BackUpTestCMDS: {
                cmd_mains_input: 1,
                alarm_status: 0,
                backupTestRunning: false,
            },

            BackUpTestData: {
                BackupTime: 0,
                inputPdata: {},
                outputPdata: {},
            },
            BackUpTestSense: {

                sense_mains_input: 1,
                sense_ups_output: 0,

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

        resetTestState() {
            this.BackUpTestData = {
                BackupTime: 0,
                inputPdata: {},
                outputPdata: {},
            };
            this.test_duration = 0;
            this.measurements = [];
            this.send({ topic: 'info', payload: "data has been reset" });
        },

        generateMeasurement() {
            const uniqueId = Math.floor(Math.random() * 9000000000) + 1000000000;
            const timestamp = new Date();

            return {
                m_unique_id: uniqueId,
                time_stamp: timestamp.getTime(),
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
                backup_time_sec: this.BackUpTestData.BackupTime,
                overload_time_sec: 0,
                temperature_1: 0,
                temperature_2: 0,
            };
        },
        createTestReport() {
            const report = {
                settings: this.selectedSetting || {}, // Use the currently selected settings
                test_name: "BackupTest", // BackupTest as string
                test_description: "Backup Test Report",
                measurements: this.measurements, // Use collected measurements
                test_result: "USER_OBSERVATION", // USER_OBSERVATION as string
            };

            // Log the report for debugging or send it to the server
            console.log("Generated Test Report:", report);
            return report;
        },

        updateBackUptestSense(payload) {
            if (payload && payload.BackUpTestSense) {
                const { BackUpTestSense } = payload;

                // Ensure all properties are updated or set to defaults if undefined
                this.BackUpTestSense = {

                    sense_mains_input: BackUpTestSense.sense_mains_input ?? 1,
                    sense_ups_output: BackUpTestSense.sense_ups_output ?? 0,

                };

                // Log to ensure data was updated properly
                console.log("Updated  BackUpTestSense:", this.BackUpTestSense);
            } else {
                console.warn("Invalid payload or missing  BackUpTestSense:", payload);
            }
        },

        updateBackUpTestData(payload) {
            if (payload && payload.BackUpTestData) {
                const { BackUpTestData } = payload;

                // Ensure all properties are updated or set to defaults if undefined
                this.BackUpTestData = {
                    BackupTime: BackUpTestData.BackupTime ?? 0,
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
                alarm_status: this.BackUpTestCMDS.alarm_status,
                cmd_mains_input: this.BackUpTestCMDS.cmd_mains_input,
                backupTestRunning: this.backupTestRunning,
                backupTestRunning: this.BackUpTestCMDS.backupTestRunning,
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
            this.resetTestState();
            this.send({
                topic: 'commands', payload: this.createRunCmds()
            });
            await this.delay(1000);
            this.send({
                topic: 'info', payload: "starting backup Test"
            });

            this.backupTestRunning = true;
            this.BackUpTestCMDS.backupTestRunning = true;
            this.send({
                topic: 'commands', payload: this.createRunCmds({
                    backupTestRunning: true,
                })
            });

            try {
                await this.delay(2000);
                this.BackUpTestCMDS.alarm_status = 1;
                this.send({
                    topic: 'commands', payload: this.createRunCmds({
                        alarm_status: 1,
                    })
                });
                await this.delay(2000);
                this.BackUpTestCMDS.alarm_status = 0;
                this.send({
                    topic: 'commands', payload: this.createRunCmds({
                        alarm_status: 0
                    })
                });
                await this.delay(2000);

                this.BackUpTestCMDS.cmd_mains_input = 0;
                this.send({
                    topic: 'commands', payload: this.createRunCmds({
                        cmd_mains_input: 0
                    })
                });
                await this.delay(2000);
                const maxRetries = 100;
                let retryCount = 0;

                while (this.BackUpTestSense.sense_mains_input !== 0) {
                    await this.delay(100);
                    retryCount++;
                    if (retryCount > maxRetries) {
                        throw new Error("Timeout: sense_mains_input did not change to 0");
                    }
                    if (!this.backupTestRunning) throw new Error("Test stopped");
                }

                retryCount = 0; // Reset for next loop
                while (this.BackUpTestSense.sense_ups_output !== 1) {
                    await this.delay(100);
                    retryCount++;
                    if (retryCount > maxRetries) {
                        throw new Error("Timeout: sense_ups_output did not change to 1");
                    }
                    if (!this.backupTestRunning) throw new Error("Test stopped");
                }

                // Start main backup test loop
                while (this.BackUpTestSense.sense_ups_output === 1 && this.BackUpTestSense.sense_mains_input === 0) {
                    if (!this.backupTestRunning) {
                        this.send({ topic: 'info', payload: "Stop cmd during run" });
                        throw new Error("Test stopped during main loop");
                    }

                    this.send({ topic: 'info', payload: "running backup Test" });
                    await this.delay(1000);

                    this.BackUpTestData.BackupTime++; // Increment backup time
                    this.test_duration++;

                    // Record measurement every 10 seconds without duplication
                    if (this.test_duration % 10 === 0) {
                        const measurement = this.generateMeasurement();
                        if (this.measurements.length > 1000) {
                            this.measurements.shift();
                        }
                        this.measurements.push(measurement);
                        this.send({ topic: 'info', payload: "new measurement recorded" });
                    }

                    this.send({ topic: 'commands', payload: this.createRunCmds() });

                    // Check for sense_ups_output changing from 1 to 0
                    if (this.BackUpTestSense.sense_ups_output === 0) {
                        this.send({
                            topic: 'info',
                            payload: `UPS output stopped. Recording final backup time: ${this.BackUpTestData.BackupTime} seconds`,
                        });

                        // Generate and record the final measurement
                        const finalMeasurement = this.generateMeasurement();
                        if (this.measurements.length === 0 ||
                            this.measurements[this.measurements.length - 1].backup_time_sec !== finalMeasurement.backup_time_sec) {
                            this.measurements.push(finalMeasurement);
                        }

                        this.send({
                            topic: 'info',
                            payload: "Final measurement recorded",
                        });
                        break; // Exit loop after recording the final measurement
                    }
                }
            } catch (error) {
                console.error(error.message);
            } finally {
                this.stopBackupTest();
            }
        },

        async stopBackupTest() {
            this.send({
                topic: 'info', payload: "stopping backup Test "
            });

            // Ensure proper states are set
            this.backupTestRunning = false;
            this.BackUpTestCMDS.backupTestRunning = false;

            // Send command to set cmd_mains_input to 1
            this.BackUpTestCMDS.cmd_mains_input = 1;
            await this.send({
                topic: 'commands',
                payload: this.createRunCmds({
                    alarm_status: 0,
                    cmd_mains_input: 1,
                    backupTestRunning: false
                }),
            });

            // Update internal state to reflect changes
            this.BackUpTestCMDS = {
                ...this.BackUpTestCMDS,
                alarm_status: 0,
                cmd_mains_input: 1,
                backupTestRunning: false,
            };

            // Generate and send the test report
            this.testReport = this.createTestReport();
            this.send({ topic: 'report', payload: this.testReport });

            // Log for debugging
            console.log("Backup test stopped. CMD mains input set to 1:", this.BackUpTestCMDS);
        }

    },
    mounted() {
        this.$watch("msg", (newMsg) => {
            if (newMsg && newMsg.payload) {
                this.updateSettingData(newMsg.payload);
                this.updateBackUptestSense(newMsg.payload);
                this.updateBackUpTestData(newMsg.payload);


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