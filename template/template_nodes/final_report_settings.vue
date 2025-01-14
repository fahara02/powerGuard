<template>
  <div class="form-container">
    <h2>Report Settings</h2>
    <form @submit.prevent="submitForm">
      <!-- Report ID -->
      <label for="report_id">Report ID:</label>
      <div class="report-id-container">
        <input type="number" v-model="formData.report_id" id="report_id" required readonly />
        <button type="button" @click="generateReportID">Generate</button>
      </div>

      <!-- Standard -->
      <label for="standard">Standard:</label>
      <select v-model="formData.standard" id="standard" required>
        <option v-for="(value, key) in TestStandard" :key="value" :value="value">
          {{ key }}
        </option>
      </select>

      <!-- UPS Model -->
      <label for="ups_model">UPS Model:</label>
      <input type="text" v-model="formData.ups_model" id="ups_model" required />

      <!-- Client Name -->
      <label for="client_name">Client Name:</label>
      <input type="text" v-model="formData.client_name" id="client_name" />

      <!-- Brand Name -->
      <label for="brand_name">Brand Name:</label>
      <input type="text" v-model="formData.brand_name" id="brand_name" />

      <!-- Test Engineer Name -->
      <label for="test_engineer_name">Test Engineer Name:</label>
      <input type="text" v-model="formData.test_engineer_name" id="test_engineer_name" />

      <!-- Test Approval Name -->
      <label for="test_approval_name">Test Approval Name:</label>
      <input type="text" v-model="formData.test_approval_name" id="test_approval_name" />

      <!-- Spec ID Dropdown -->
      <label for="spec_id">Specification ID:</label>
      <select v-model="formData.spec_id" id="spec_id" required>
        <option v-for="id in specOptions" :key="id" :value="id">{{ id }}</option>
      </select>

      <!-- Display Spec Data -->
      <div v-if="selectedSpec">
        <h3>Spec Details:</h3>
        <p><strong>Phase:</strong> {{ selectedSpec.phase }}</p>
        <p><strong>Rated VA:</strong> {{ selectedSpec.rating_va }}</p>
        <p><strong>Rated Voltage:</strong> {{ selectedSpec.rated_voltage }}</p>
        <p><strong>Rated Current:</strong> {{ selectedSpec.rated_current }}</p>
        <p><strong>Power Factor Rated Current:</strong> {{ selectedSpec.pf_rated_current }}</p>
        <p><strong>Max Continuous Amp:</strong> {{ selectedSpec.max_continous_amp }}</p>
        <p><strong>Overload Amp:</strong> {{ selectedSpec.overload_amp }}</p>
        <p><strong>Average Switch Time (ms):</strong> {{ selectedSpec.avg_switch_time_ms }}</p>
        <p><strong>Average Backup Time (ms):</strong> {{ selectedSpec.avg_backup_time_ms }}</p>
      </div>

      <button type="submit">Submit</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      latest_spec_id: 0,
      specs: [], // Initially empty
      formData: {
        report_id: 44042913,
        standard: "IEC_62040_1",
        ups_model: "UVA-123",
        client_name: 'Walton',
        brand_name: 'Walton',
        test_engineer_name: "Engr Atik",
        test_approval_name: "Engr Jhon",
        spec_id: null, // Selected spec_id
        spec: null,
      },
      TestStandard: {
        IEC_62040_1: "IEC_62040_1",
        IEC_62040_2: "IEC_62040_2",
        IEC_62040_3: "IEC_62040_3",
        IEC_62040_4: "IEC_62040_4",
        IEC_62040_5: "IEC_62040_5",
      },
    };
  },
  computed: {
    specOptions() {
      return this.specs.map((spec) => spec.id).sort((a, b) => a - b);
    },
    selectedSpec() {
      return this.specs.find((spec) => spec.id === this.formData.spec_id) || null;
    },
  },
  methods: {
    submitForm() {
      const msg = { payload: this.formData };
      console.log("Form submitted:", msg);
      this.send(msg); // Replace with your actual submission logic
    },
    updateSpecData(payload) {
      if (payload.latest_spec_id !== undefined) {
        this.latest_spec_id = payload.latest_spec_id;
      }
      if (payload.spec && Array.isArray(payload.spec)) {
        this.specs = payload.spec;
      } else {
        console.error("Spec data is not properly formatted:", payload.spec);
      }

      const latestSpec = this.specs.find((spec) => spec.id === this.latest_spec_id - 1) || this.specs[0];
      if (!this.formData.spec_id && latestSpec) {
        this.formData.spec_id = latestSpec.id;
        this.formData.spec = latestSpec;
      }
    },
    generateReportID() {
      this.formData.report_id = Math.floor(10000000 + Math.random() * 90000000);
    },
  },
  watch: {
    'formData.spec_id': function (newSpecID) {
      this.formData.spec = this.specs.find((spec) => spec.id === newSpecID) || null;
    },
    msg(newMsg) {
      console.log("New message received:", newMsg);
      if (newMsg && newMsg.payload) {
        this.updateSpecData(newMsg.payload);
      }
    },
  },
};
</script>

<style scoped>
.form-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f4f4f9;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

label {
  font-weight: bold;
}

input,
select,
button {
  padding: 10px;
  font-size: 1rem;
  border-radius: 5px;
  border: 1px solid #ccc;
}

button {
  background-color: #007bff;
  color: white;
  cursor: pointer;
  border: none;
}

button:hover {
  background-color: #0056b3;
}

h3 {
  margin-top: 20px;
}

.report-id-container {
  display: flex;
  gap: 10px;
}
</style>
