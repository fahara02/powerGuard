<template>
    <div>
        <!-- Report Selection Dropdown -->
        <div class="report-selector">
            <label for="report-id">Select Report:</label>
            <select id="report-id" v-model="formData.report.id" @change="onReportChange">
                <option value="" disabled>Select a Report</option>
                <option v-for="id in reportOptions" :key="id" :value="id">
                    Report {{ id }}
                </option>
            </select>
        </div>
        <div class="print-button-container">
            <button @click="printReport">Print Report</button>
        </div>
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-container">
            Loading report data...
        </div>

        <!-- Error or No Data -->
        <div v-else-if="!currentSelectedReport" class="error-container">
            <p>No report selected or available. Please select a valid report.</p>
        </div>

        <!-- Test Report Details -->
        <div v-else class="test-report-container" id="report-content">
            <!-- Common Test Information -->
            <div class="common-info">
                <h2>{{ currentSelectedReport.test_name }}</h2>
                <p><strong>Description:</strong> {{ currentSelectedReport.test_description }}</p>
                <p><strong>Test Result:</strong> {{ currentSelectedReport.test_result }}</p>
                <p><strong>Client Name:</strong> {{ currentSelectedReport.settings.client_name }}</p>
                <p><strong>Standard:</strong> {{ currentSelectedReport.settings.standard }}</p>
                <p><strong>UPS Model:</strong> {{ currentSelectedReport.settings.ups_model }}</p>
                <p><strong>UPS VA:</strong> {{ currentSelectedReport.spec.rating_va || 'N/A' }}</p>
                <p><strong>Phase:</strong> {{ currentSelectedReport.spec.phase || 'N/A' }}</p>
                <p><strong>Rated Voltage:</strong> {{ currentSelectedReport.spec.rated_voltage || 'N/A' }} V</p>
                <p><strong>Rated Current:</strong> {{ currentSelectedReport.spec.rated_current || 'N/A' }} A</p>
                <p><strong>Min Input Voltage:</strong> {{ currentSelectedReport.spec.min_input_voltage || 'N/A' }} V</p>
                <p><strong>Max Input Voltage:</strong> {{ currentSelectedReport.spec.max_input_voltage || 'N/A' }} V</p>
                <p><strong>Power Factor (Rated Current):</strong> {{ currentSelectedReport.spec.pf_rated_current ||
                    'N/A' }}</p>
                <p><strong>Max Continuous Amp:</strong> {{ currentSelectedReport.spec.max_continous_amp || 'N/A' }} A
                </p>
                <p><strong>Overload Amp:</strong> {{ currentSelectedReport.spec.overload_amp || 'N/A' }} A</p>
            </div>


            <!-- Common Measurement Information -->
            <div class="measurement-common-info">
                <h3>Measurement Overview</h3>
                <p><strong>Load Type:</strong> {{ measurementCommonData.load_type || "N/A" }}</p>
                <p><strong>Load Percentage:</strong> {{ measurementCommonData.load_percentage || 0 }}</p>
                <p><strong>Run Interval (s):</strong> {{ measurementCommonData.run_interval_sec || 0 }}</p>
                <p><strong>Phase Name:</strong> {{ measurementCommonData.phase_name || "Unknown" }}</p>
                <p><strong>Step ID:</strong> {{ measurementCommonData.step_id || "N/A" }}</p>
            </div>

            <!-- Measurement Table -->
            <!-- Measurement Table -->
            <div class="measurement-table-container"
                v-if="currentSelectedReport && currentSelectedReport.measurements.length">
                <h3>Measurements Table</h3>
                <table class="measurement-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Measurement Name</th>
                            <th>Type</th>
                            <th>Voltage (V)</th>
                            <th>Current (A)</th>
                            <th>Power (W)</th>
                            <th>Power Factor</th>
                            <th>Frequency (Hz)</th>
                            <th>Backup Time (s)</th>
                            <th>Load Percentage</th>
                            <th>Phase Name</th>
                            <th>Step ID</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="(measurement, index) in currentSelectedReport.measurements"
                            :key="measurement.m_unique_id">
                            <tr>
                                <!-- Display the first power measure -->
                                <td :rowspan="measurement.power_measures.length">{{ index + 1 }}</td>
                                <td :rowspan="measurement.power_measures.length">{{ measurement.name }}</td>
                                <td>{{ measurement.power_measures[0].type }}</td>
                                <td>{{ measurement.power_measures[0].voltage }}</td>
                                <td>{{ measurement.power_measures[0].current }}</td>
                                <td>{{ measurement.power_measures[0].power }}</td>
                                <td>{{ measurement.power_measures[0].pf }}</td>
                                <td>{{ measurement.power_measures[0].frequency }}</td>
                                <td :rowspan="measurement.power_measures.length">{{ measurement.backup_time_sec }}</td>
                                <td :rowspan="measurement.power_measures.length">{{ measurement.load_percentage }}</td>
                                <td :rowspan="measurement.power_measures.length">{{ measurement.phase_name }}</td>
                                <td :rowspan="measurement.power_measures.length">{{ measurement.step_id }}</td>
                            </tr>
                            <!-- Additional rows for remaining power measures -->
                            <tr v-for="(powerMeasure, pmIndex) in measurement.power_measures.slice(1)"
                                :key="measurement.m_unique_id + '-' + pmIndex">
                                <td>{{ powerMeasure.type }}</td>
                                <td>{{ powerMeasure.voltage }}</td>
                                <td>{{ powerMeasure.current }}</td>
                                <td>{{ powerMeasure.power }}</td>
                                <td>{{ powerMeasure.pf }}</td>
                                <td>{{ powerMeasure.frequency }}</td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>

            <!-- Error Handling -->
            <div v-else class="error-container">
                <p>No measurements available for the selected report.</p>
            </div>


        </div>
    </div>
</template>



<script>
export default {
    props: {
        selectedReport: {
            type: Object,
            required: false, // Optional, now handled via computed property
        },
    },
    data: function () {
        return {
            reports: [], // Holds full report data
            reportIDs: [], // Holds the list of report IDs (DB row IDs)

            formData: {
                report: {
                    id: null, // Selected report ID (DB row ID)
                },
            },
            isLoading: false,
            responseTimeout: 10000, // Timeout for waiting for DB response in ms
        };
    },
    computed: {
        // Dropdown options (based on DB row IDs)
        reportOptions() {
            return this.reportIDs.sort((a, b) => a - b); // Sort IDs numerically
        },


        currentSelectedReport() {
            return this.reports.find(
                (report) => report.id === this.formData.report.id
            ) || null;
        },
        measurementCommonData() {
            if (!this.currentSelectedReport || !this.currentSelectedReport.measurements.length) {
                return {};
            }

            const firstMeasurement = this.currentSelectedReport.measurements[0];
            return {
                load_type: firstMeasurement.load_type,
                load_percentage: firstMeasurement.load_percentage,
                run_interval_sec: firstMeasurement.run_interval_sec,
                phase_name: firstMeasurement.phase_name,
                step_id: firstMeasurement.step_id,
            };
        },
    },
    methods: {
        printReport() {
            const printContent = document.getElementById("report-content");
            if (!printContent) {
                console.error("No report content found to print.");
                return;
            }

            // Save the current HTML and styles
            const originalContent = document.body.innerHTML;
            const originalStyles = document.head.innerHTML;

            // Replace body content with the report content
            document.body.innerHTML = printContent.outerHTML;

            // Trigger print dialog
            window.print();

            // Restore original content and styles
            document.body.innerHTML = originalContent;
            document.head.innerHTML = originalStyles;
            window.location.reload(); // Reload the page to reinitialize the dashboard
        },

        onReportChange() {
            if (!this.formData.report.id) return;

            this.isLoading = true;
            this.fetchReport()
                .then(() => (this.isLoading = false))
                .catch((error) => {
                    console.error("Error fetching report:", error);
                    this.isLoading = false;
                });
        },


        // Update all report IDs from incoming data
        updateAllReportID(payload) {
            if (Array.isArray(payload)) {
                this.reportIDs = payload; // Populate the dropdown with DB row IDs
            } else {
                console.error("Invalid payload format for report IDs. Expected an array.");
            }
        },

        // Update or add a report in the `reports` array
        updateAllReport(payload) {
            if (payload && payload.test_report_id) {
                const report = {
                    id: payload.test_report_id, // Use the DB row ID as `id`
                    subreport_id: payload.sub_report_id, // Keep subreport_id separate
                    test_name: payload.test_name,
                    test_description: payload.test_description,
                    test_result: payload.test_result,
                    settings: payload.settings,
                    spec: payload.spec,
                    measurements: payload.measurements,
                };

                // Find index of the report with the same DB row ID
                const index = this.reports.findIndex((r) => r.id === report.id);
                if (index >= 0) {
                    this.$set(this.reports, index, report); // Update existing report
                } else {
                    this.reports.push(report); // Add new report
                }

                // Log update
                this.send({
                    topic: "info",
                    payload: `Report updated: ${report.id}`,
                });
            } else {
                console.error("Invalid payload format for reports.");
                this.send({
                    topic: "error",
                    payload: "Invalid payload format for reports.",
                });
            }
        },

        // Wait for the database response
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

        // Fetch the selected report from the database
        async fetchReport() {
            const selectedId = this.formData.report.id;

            if (!selectedId) {
                console.error("No Report ID selected.");
                this.send({
                    topic: "error",
                    payload: "No Report ID selected.",
                });
                return;
            }

            this.send({
                topic: "info",
                payload: `Fetching test report for report ID: ${selectedId}`,
            });

            const query = `
    SELECT 
        TestReport.id AS test_report_id, -- Row ID
        TestReport.sub_report_id, -- Subreport ID
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
        Measurement.load_percentage AS load_percentage,
        Measurement.step_id AS step_id,
        Measurement.run_interval_sec AS run_interval_sec,
        Measurement.backup_time_sec AS backup_time_sec,
        PowerMeasure.type AS power_measure_type,
        PowerMeasure.voltage AS power_measure_voltage,
        PowerMeasure.current AS power_measure_current,
        PowerMeasure.power AS power_measure_power,
        PowerMeasure.energy AS power_measure_energy,
        PowerMeasure.pf AS power_measure_pf,
        PowerMeasure.frequency AS power_measure_frequency,
        spec.phase AS phase,
        spec.rating_va AS rating_va,
        spec.rated_voltage AS rated_voltage,
        spec.rated_current AS rated_current,
        spec.min_input_voltage AS min_input_voltage,
        spec.max_input_voltage AS max_input_voltage,
        spec.pf_rated_current AS pf_rated_current,
        spec.max_continous_amp AS max_continous_amp,
        spec.overload_amp AS overload_amp
    FROM TestReport
    JOIN ReportSettings ON TestReport.settings_id = ReportSettings.id
    JOIN spec ON ReportSettings.spec_id = spec.id
    LEFT JOIN Measurement ON Measurement.test_report_id = TestReport.id
    LEFT JOIN PowerMeasure ON PowerMeasure.measurement_id = Measurement.id
    WHERE TestReport.id = '${selectedId}'
    ORDER BY Measurement.id, PowerMeasure.id
`;


            this.send({ topic: query });

            try {
                const result = await this.waitForResponse();
                if (result && result.payload) {
                    this.updateAllReport(result.payload);
                } else {
                    console.error("Failed to fetch report data or no data returned.");
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
    mounted() {
        this.$watch(
            "msg",
            function (newMsg) {
                if (newMsg && newMsg.payload) {
                    if (Array.isArray(newMsg.payload)) {
                        this.updateAllReportID(newMsg.payload); // Update report IDs
                    }
                }
            },
            { deep: true }
        );
    },
};
</script>


<style scoped>
/* General Styling */
body {
    font-family: 'Roboto', Arial, sans-serif;
    color: #333;
    margin: 0;
    padding: 0;
    background-color: #f4f6f9;
}

/* Container Styling */
.test-report-container {
    padding: 20px 30px;
    background-color: #ffffff;
    border-radius: 12px;
    max-width: 1000px;
    margin: 30px auto;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

/* Section Titles */
.common-info h2,
.measurement-common-info h3 {
    font-size: 1.8rem;
    color: #004085;
    margin-bottom: 10px;
    border-left: 4px solid #007bff;
    padding-left: 10px;
}

/* Paragraph Styling */
.common-info p,
.measurement-common-info p {
    font-size: 1rem;
    color: #555;
    margin: 8px 0;
    line-height: 1.6;
}

/* Dropdown Styling */
.report-selector {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.report-selector label {
    font-weight: bold;
    color: #555;
}

.report-selector select {
    padding: 8px 12px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 1rem;
    color: #495057;
    background-color: #ffffff;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.075);
}

/* Buttons */
.print-button-container {
    text-align: right;
    margin-bottom: 20px;
}

button {
    background-color: #007bff;
    color: #fff;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s, box-shadow 0.3s;
}

button:hover {
    background-color: #0056b3;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

button:active {
    background-color: #004085;
}

/* Loading and Error Containers */
.loading-container,
.error-container {
    padding: 20px;
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    margin-top: 10px;
    font-size: 1rem;
    text-align: center;
}

/* Measurement Table */
.measurement-table-container {
    margin-top: 30px;
}

.measurement-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.measurement-table th,
.measurement-table td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: center;
}

.measurement-table th {
    background-color: #343a40;
    color: #ffffff;
    font-weight: bold;

}

.measurement-table tbody tr:nth-child(even) {
    background-color: #f8f9fa;
}

.measurement-table tbody tr:hover {
    background-color: #eaf2f8;
}

/* Responsive Design */
@media (max-width: 768px) {
    .test-report-container {
        padding: 15px;
    }

    .measurement-table th,
    .measurement-table td {
        padding: 10px;
        font-size: 0.85rem;
    }
}
</style>
