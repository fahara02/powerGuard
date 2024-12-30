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
        <label for="step-id">Step ID:</label>
        <input type="number" v-model.number="formData.stepId" id="step-id" required min="0" />
      </div>
      <div>
        <label for="load-percentage">Load Percentage:</label>
        <input type="number" v-model.number="formData.loadPercentage" id="load-percentage" required min="0" max="100" />
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
      latest_settings_id: 0,
      setting: [],
      loadTypes: {
        LINEAR: 0,
        NON_LINEAR: 1,
      },
      formData: {
        setting_id: 0,
        loadType: 0,
        stepId: 0,
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

    createPayload(overrides = {}) {
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
      this.send({ payload: this.createPayload() });

      try {
        await this.delay(2000);
        this.BackUpTestData.alarm_status = 0;
        this.send({ payload: this.createPayload() });

        this.BackUpTestData.sense_mains_input = 0;
        this.send({ payload: this.createPayload() });

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
          this.send({ payload: this.createPayload() });
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
        payload: this.createPayload({
          alarm_status: 0,
          cmd_mains_input: 1,
        }),
      });
      this.BackUpTestData = {
        ...this.BackUpTestData,
        alarm_status: 0,
        sense_mains_input: 1,
      };
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