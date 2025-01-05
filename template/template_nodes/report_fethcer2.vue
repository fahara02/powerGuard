<template>
    <div class="report-container">
        <!-- Dropdown for selecting sub-report ID -->
        <div class="dropdown-container">
            <label for="subreport-dropdown">Select Sub-Report ID:</label>
            <select id="subreport-dropdown" v-model="formData.report.id">
                <option value="" disabled>Select a Sub-Report</option>
                <option v-for="id in reportOptions" :key="id" :value="id">{{ id }}</option>
            </select>
        </div>

        <!-- Button to fetch the selected report -->
        <div class="button-container">
            <button @click="fetchReport">Fetch Report</button>
        </div>

        <!-- Display selected report details -->
        <div v-if="selectedReport" class="report-display">
            <h2>Test Report: {{ selectedReport.test_name }}</h2>
            <div class="report-section">
                <h3>Test Details</h3>
                <p><strong>Description:</strong> {{ selectedReport.test_description }}</p>
                <p><strong>Result:</strong> {{ selectedReport.test_result }}</p>
            </div>
            <div class="report-section">
                <h3>Client Information</h3>
                <p><strong>Client Name:</strong> {{ selectedReport.settings.client_name }}</p>
                <p><strong>Standard:</strong> {{ selectedReport.settings.standard }}</p>
                <p><strong>UPS Model:</strong> {{ selectedReport.settings.ups_model }}</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data: function () {
        return {
            reports: [], // Holds full report data
            reportIDs: [], // Holds the list of report IDs
            formData: {
                report: {
                    id: null, // Currently selected report ID
                },
            },
            responseTimeout: 10000, // Timeout for waiting for DB response in ms
        };
    },
    computed: {
        // Extract subreport_id for dropdown options
        reportOptions: function () {
            return this.reportIDs.sort((a, b) => a - b); // Sort IDs numerically
        },

        // Find the selected report object based on subreport_id
        selectedReport: function () {
            return this.reports.find(
                (report) => report.id === this.formData.report.id
            ) || null;
        },
    },
    methods: {
        // Update all report IDs from incoming data
        updateAllReportID: function (payload) {
            if (Array.isArray(payload)) {
                this.reportIDs = payload; // Update the list of report IDs
            } else {
                console.error("Invalid payload format for report IDs. Expected an array.");
            }
        },

        // Update all report data from incoming data
        updateAllReport: function (payload) {
            if (payload && payload.subreport_id) {
                // Transform payload into a report object and update the reports array
                const report = {
                    id: payload.subreport_id,
                    test_name: payload.test_name,
                    test_description: payload.test_description,
                    test_result: payload.test_result,
                    settings: payload.settings,
                    measurements: payload.measurements,
                };

                // Update the reports array
                this.reports = [report];

                // Log received report information
                this.send({
                    topic: "info",
                    payload: `Received report for reportid: ${report.id} for test ${report.test_name}`,
                });
            } else {
                console.error("Invalid payload format for reports.");
                this.send({
                    topic: "error",
                    payload: "Invalid payload format for reports.",
                });
            }
        },

        // Wait for response from the database
        waitForResponse() {
            return new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error("Timeout while waiting for database response."));
                }, this.responseTimeout);

                this.$watch(
                    "msg",
                    function (newMsg) {
                        if (newMsg && newMsg.topic === "db_reply") {
                            clearTimeout(timeout);
                            resolve(newMsg);
                        }
                    },
                    { immediate: false, deep: true }
                );
            });
        },

        async fetchReport() {
            const selectedId = this.formData.report.id; // Get selected report ID

            if (!selectedId) {
                console.error("No Sub-Report ID selected.");
                this.send({
                    topic: "error",
                    payload: "No Sub-Report ID selected.",
                });
                return;
            }

            // Debug: Inform Node-RED of the selected report ID
            this.send({
                topic: "info",
                payload: `Fetching test report for reportid: ${selectedId}`,
            });

            // Prepare the query for SQLite
            const query = `
        SELECT 
            TestReport.id AS test_report_id,
            TestReport.sub_report_id,
            TestReport.test_name,
            TestReport.test_description,
            TestReport.test_result,
            ReportSettings.client_name,
            ReportSettings.standard,
            ReportSettings.ups_model,
            Measurement.m_unique_id AS measurement_unique_id,
            Measurement.name AS measurement_name,
            Measurement.timestamp AS measurement_timestamp,
            Measurement.mode AS mode,
            Measurement.phase_name AS phase_name,
            Measurement.load_type AS load_type,
            Measurement.load_percentage AS load_percentage ,
            Measurement.step_id AS step_id,
            Measurement.load_type AS load_type,
            Measurement.run_interval_sec AS run_interval_sec,
            Measurement.backup_time_sec AS backup_time_sec,
            PowerMeasure.type AS power_measure_type,
            PowerMeasure.voltage AS power_measure_voltage,
            PowerMeasure.current AS power_measure_current,
            PowerMeasure.power AS power_measure_power,
            PowerMeasure.energy AS power_measure_energy,
            PowerMeasure.pf AS power_measure_pf,
            PowerMeasure.frequency AS power_measure_frequency
        FROM TestReport
        JOIN ReportSettings ON TestReport.settings_id = ReportSettings.id
        LEFT JOIN Measurement ON Measurement.test_report_id = TestReport.id
        LEFT JOIN PowerMeasure ON PowerMeasure.measurement_id = Measurement.id
        WHERE TestReport.id = '${selectedId}'
        ORDER BY Measurement.id, PowerMeasure.id
    `;


            this.send({ topic: query });

            try {
                // Wait for the database response
                const result = await this.waitForResponse();
                if (result && result.payload) {
                    // Pass the payload to updateAllReport
                    this.updateAllReport(result.payload);
                } else {
                    console.error("Failed to fetch report data or no data returned.", result);
                    this.send({
                        topic: "error",
                        payload: "Failed to fetch report data.",
                    });
                }
            } catch (err) {
                console.error("Error while fetching report:", err);
                this.send({
                    topic: "error",
                    payload: `Error while fetching report: ${err.message}`,
                });
            }

        },
    },
    mounted: function () {
        // Watch for incoming messages to update report data
        this.$watch(
            "msg",
            function (newMsg) {
                if (newMsg && newMsg.payload) {
                    if (Array.isArray(newMsg.payload)) {
                        this.updateAllReportID(newMsg.payload); // Handle ID array
                    } else if (newMsg.topic === "db_reply") {
                        this.updateAllReport([newMsg.payload]); // Handle report data
                    }
                }
            },
            { deep: true }
        );
    },
};
</script>


<style scoped>
.report-container {
    padding: 20px;
    background: #f4f4f9;
    border-radius: 10px;
    max-width: 800px;
    margin: auto;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

.dropdown-container {
    margin-bottom: 20px;
}

.dropdown-container label {
    margin-right: 10px;
}

#subreport-dropdown {
    padding: 8px;
    font-size: 16px;
}

.button-container {
    margin-bottom: 20px;
}

button {
    padding: 10px 20px;
    font-size: 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

.report-display h2 {
    font-size: 1.5rem;
    margin-bottom: 20px;
}

.report-section {
    margin-bottom: 20px;
}

.report-section h3 {
    font-size: 1.2rem;
    margin-bottom: 10px;
}

.report-section p {
    margin: 5px 0;
    line-height: 1.5;
}
</style>