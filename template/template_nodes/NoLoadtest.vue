<template>
    <div class="noload-test-ui">
        <h1>No Load Test</h1>
        <div>
            <div>
                <!-- Setting ID Dropdown -->
                <label for="setting_id">Report Settings ID:</label>
                <select v-model="formData.setting_id" id="setting_id" required>
                    <option v-for="id in settingOptions" :key="id" :value="id">{{ id }}</option>
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
                <label for="step-id">Step ID:</label>
                <input type="number" v-model.number="formData.stepId" id="step-id" required min="0" />
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
                <p><strong>UPS VA :</strong> {{ selectedSpec?.rating_va || 'N/A' }}</p>
                <p>Selected Spec: {{ selectedSpec }}</p>



            </div>
            <div class="buttons">
                <button type="button" @click="startNoLoadTest" :disabled="noLoadTestRunning">Start Test</button>
                <button type="button" @click="stopNoLoadTest" :disabled="!noLoadTestRunning">Stop Test</button>
                <button type="button" @click="captureMeasurement" :disabled="!noLoadTestRunning">Capture</button>
            </div>
        </div>

        <div v-if="noLoadTestRunning" class="test-status">
            <p>Noload Test running... Waiting for capture command.</p>
            <p>Test Duration: {{ test_duration }} seconds</p>
        </div>
        <div v-if="!noLoadTestRunning && measurements.length > 0" class="test-result">
            <h2>Captured Measurements</h2>
            <ul>
                <li v-for="(measurement, index) in measurements" :key="index">
                    Measurement {{ index + 1 }}: {{ measurement }}
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
            measurementIdCounter: 0,
            subreport_id: 0,
            first_measurement_taken: false,
            test_report: null,
            latest_settings_id: 0,
            test_type: 1, // For No Load Test
            setting: [],
            all_spec: [],
            TestType: {
                LIGHT_LOAD_AND_FUNCTION_TEST: 0,
                NO_LOAD_TEST: 1,
                FULL_LOAD_TEST: 2,
                AC_INPUT_FAILURE: 3,
                AC_INPUT_RETURN: 4,
                INPUT_POWER_FACTOR: 5,
                CHANGE_OPERATION_MODE: 6,
                STORED_ENERGY_TIME: 7,
                SwitchTest: 8,
                BackupTest: 9,
                EfficiencyTest: 10,
                SteadyState_InputVoltage_Test: 11,
                WaveformTest: 12,
                EFFICIENCY_NORMAL_MODE: 14,
                EFFICIENCY_STORAGE_MODE: 15,
                OVERLOAD_NORMAL_MODE: 16,
                OVERLOAD_STORAGE_MODE: 17,
            },
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
                spec_id: 0,
                loadType: "LINEAR",
                mode: "NORMAL_MODE",
                loadPercentage: 0,
                runInterval: 0,
                stepId: 0,
            },
            noLoadTestRunning: false,
            measurements: [],


            TestCMDS: {
                cmd_mains_input: 1,
                alarm_status: 0,
                noLoadTestRunning: false,
            },

            TestData: {

                inputPdata: {},
                outputPdata: {},
            },
            TestSense: {

                sense_mains_input: 1,
                sense_ups_output: 0,

            },
        };
    },
    computed: {
        settingOptions() {
            return this.setting.map((setting) => setting.id || 0).sort((a, b) => a - b);
        },
        selectedSetting() {
            return this.setting.find((setting) => setting.id === this.formData.setting_id) || null;
        },
        selectedSpec() {
            const specId = this.selectedSetting?.spec_id;
            return this.all_spec.find((spec) => spec.id === specId) || null;
        },
    },
    methods: {
        resetTestState() {
            this.measurements = [];
            this.test_duration = 0;
            this.first_measurement_taken = false;
            this.send({ topic: "info", payload: "data has been reset" });
        },
        createRunCmds(overrides = {}) {
            return {
                alarm_status: this.TestCMDS.alarm_status,
                cmd_mains_input: this.TestCMDS.cmd_mains_input,
                noLoadTestRunning: this.noLoadTestRunning,
                noLoadTestRunning: this.TestCMDS.noLoadTestRunning,

                additionalData: {
                    setting_id: this.formData.setting_id,
                    loadType: this.formData.loadType,
                    stepId: this.formData.stepId,
                    loadPercentage: this.formData.loadPercentage,
                },
                ...overrides,
            };
        },
        generateMeasurementId(testType, mainReportId) {
            this.measurementIdCounter += 1;
            if (this.measurementIdCounter > 99) {
                this.measurementIdCounter = 1;
            }
            const testTypePart = String(testType).padStart(2, "0");
            const reportPart = String(mainReportId).slice(-5);
            const counterPart = String(this.measurementIdCounter).padStart(2, "0");
            return Number(`${testTypePart}${reportPart}${counterPart}`);
        },
        generateMeasurement(testType, mainReportId) {
            const uniqueId = this.generateMeasurementId(testType, mainReportId);
            const timestamp = new Date();
            return {
                m_unique_id: uniqueId,
                time_stamp: timestamp.getTime(),
                name: "No Load Test Measurement",
                mode: this.formData.mode,
                load_type: this.formData.loadType,
                load_percentage: this.formData.loadPercentage,
                step_id: this.formData.stepId,
                run_interval_sec: this.formData.runInterval,
                // Additional fields...
            };
        },
        captureMeasurement() {
            if (this.noLoadTestRunning) {
                const mainReportId = this.selectedSetting?.report_id || 10000000;
                const measurement = this.generateMeasurement(1, mainReportId);
                this.measurements.push(measurement);
                console.log("Measurement captured:", measurement);
                this.send({ topic: "info", payload: "Measurement captured" });
            } else {
                console.warn("No Load Test is not running. Cannot capture measurement.");
            }
        },
        async startNoLoadTest() {

            // Reset test state before starting
            this.resetTestState();
            const mainReportId = this.selectedSetting?.report_id || 10000000; // Ensure fallback is valid
            this.subreport_id = this.generateMeasurementId(1, mainReportId);
            try {
                this.TestCMDS.alarm_status = 1;
                this.send({
                    topic: 'commands', payload: this.createRunCmds({
                        alarm_status: 1,
                    })
                });
                await this.delay(2000);
                this.TestCMDS.alarm_status = 0;
                this.send({
                    topic: 'commands', payload: this.createRunCmds({
                        alarm_status: 0
                    })
                });
                await this.delay(2000);
                this.send({
                    topic: 'commands', payload: this.createRunCmds()
                });

                const maxRetries = 100;
                let retryCount = 0;
                while (this.TestSense.sense_ups_output !== 1) {
                    await this.delay(100);
                    retryCount++;
                    if (retryCount > maxRetries) {
                        throw new Error("Timeout: sense_ups_output did not change to 1");
                    }
                    if (!this.noLoadTestRunning) throw new Error("Test stopped");
                }
                this.send({
                    topic: "info",
                    payload: "Starting No Load Test...",
                });


                this.send({
                    topic: 'reset', payload: false
                });
                this.noLoadTestRunning = true;
                this.send({
                    topic: 'commands', payload: this.createRunCmds({
                        noLoadTestRunning: true,
                    })
                });


                while (this.noLoadTestRunning) {
                    console.log("No Load Test is running...");
                    await this.delay(1000); // Simulate running test logic
                    this.test_duration++;

                    // Add any additional logic for test progress here if needed
                }
            } catch (error) {
                console.error("Error during No Load Test:", error.message);
            } finally {
                this.stopNoLoadTest();
            }
        },

        stopNoLoadTest() {
            this.noLoadTestRunning = false;
            this.send({
                topic: "info",
                payload: "Stopping No Load Test",
            });
            this.test_report = {
                settings: this.selectedSetting || {},
                measurements: this.measurements,
                subreport_id: this.subreport_id,
                test_name: "No Load Test",
                test_description: "No Load Test Report",
            };
            this.send({ topic: "report", payload: this.test_report });
        },
        async delay(ms) {
            return new Promise((resolve) => setTimeout(resolve, ms));
        },

        updateSettingData(payload) {
            if (payload && payload.SettingData && Array.isArray(payload.SettingData.settings)) {
                this.setting = payload.SettingData.settings;
                this.all_spec = payload.SettingData.spec || [];
            } else {
                console.warn("No valid settings data received in payload", payload);
            }
        },
        updateTestSense(payload) {
            if (payload && payload.TestSense) {
                const { TestSense } = payload;
                this.TestSense = {
                    sense_mains_input: TestSense.sense_mains_input ?? 1,
                    sense_ups_output: TestSense.sense_ups_output ?? 0,
                };

                console.log("Updated  TestSense:", this.TestSense);
            } else {
                console.warn("Invalid payload or missing  TestSense:", payload);
            }
        },

        updateTestData(payload) {
            if (payload && payload.BackUpTestData) {
                const { TestData } = payload;
                this.TestData = {

                    inputPdata: TestData.inputPdata || {},
                    outputPdata: TestData.outputPdata || {},
                };
                console.log("Updated BackUpTestData:", this.TestData);
            } else {
                console.warn("Invalid payload or missing TestData:", payload);
            }
        },
    },
    mounted() {
        this.$watch("msg", (newMsg) => {
            if (newMsg && newMsg.payload) {
                this.updateSettingData(newMsg.payload);
                this.updateTestSense(newMsg.payload);
                this.updateTestData(newMsg.payload);
            }
        });
    },
};
</script>

<style scoped>
.noload-test-ui {
    max-width: 450px;
    margin: 30px auto;
    font-family: 'Arial', sans-serif;
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h1 {
    font-size: 24px;
    color: #333;
    text-align: center;
}

label,
p {
    font-size: 14px;
    color: #555;
}

input,
select,
button {
    width: 100%;
    margin-bottom: 15px;
    padding: 10px;
    font-size: 14px;
    border-radius: 5px;
}

button {
    cursor: pointer;
    background-color: #007bff;
    color: white;
    border: none;
}

button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}
</style>
