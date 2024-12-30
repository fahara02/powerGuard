<template>
    <div class="backup-test-ui">
      <h1>Backup Test Control</h1>
      <div>
        <!-- Setting ID Dropdown -->
        <div>
          <label for="setting_id">Report Settings ID:</label>
          <select v-model="formData.setting_id" id="setting_id" required>
            <option v-for="id in settingOptions" :key="id" :value="id">{{ id }}</option>
          </select>
        </div>
  
        <div>
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
  
        <!-- Display Selected Setting Details -->
        <div v-if="selectedSetting">
          <h3>Setting Details:</h3>
          <p><strong>Report ID:</strong> {{ selectedSetting.report_id }}</p>
          <p><strong>Standard:</strong> {{ selectedSetting.standard }}</p>
          <p><strong>UPS Model:</strong> {{ selectedSetting.ups_model }}</p>
          <p><strong>Client Name:</strong> {{ selectedSetting.client_name }}</p>
          <p><strong>Brand Name:</strong> {{ selectedSetting.brand_name }}</p>
          <p><strong>Test Engineer Name:</strong> {{ selectedSetting.test_engineer_name }}</p>
          <p><strong>Test Approval Name:</strong> {{ selectedSetting.test_approval_name }}</p>
          <p><strong>UPS SPEC ID:</strong> {{ selectedSetting.spec_id }}</p>
        </div>
  
        <!-- Test Controls -->
        <div class="buttons">
          <button type="button" @click="startBackupTest" :disabled="backupTestRunning">
            Start Test
          </button>
          <button type="button" @click="stopBackupTest" :disabled="!backupTestRunning">
            Stop Test
          </button>
        </div>
      </div>
  
      <!-- Test Status and Results -->
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
        setting: [], // Will be populated from `msg.payload`
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
        return this.setting.map((setting) => setting.id||0).sort((a, b) => a - b);
      },
      selectedSetting() {
        return this.setting.find((setting) => setting.id === this.formData.setting_id) || null;
      },
    },
    methods: {
      createPayload(overrides = {}) {
        return {
          alarm_status: this.BackUpTestData.alarm_status,
          cmd_mains_input: this.BackUpTestData.sense_mains_input,
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
      startBackupTest() {
        this.backupTestRunning = true;
        this.BackUpTestData.alarm_status = 1;
        this.send({ payload: this.createPayload() });
      },
      stopBackupTest() {
        this.backupTestRunning = false;
        this.BackUpTestData = {
          ...this.BackUpTestData,
          alarm_status: 0,
          sense_mains_input: 1,
        };
        this.send({ payload: this.createPayload() });
      },
      updateBackUpTestData(payload) {
        if (payload && payload.BackUpTestData) {
          this.BackUpTestData = { ...this.BackUpTestData, ...payload.BackUpTestData };
        }
      },
      updateSettingData(payload) {
      if (payload && payload.SettingData && Array.isArray(payload.SettingData.settings)) {
       this.setting = payload.SettingData.settings;
       } else {
        console.warn("No valid settings data received in payload", payload);
        this.setting = [];
              }
          }

    },
    watch: {
      msg(newMsg) {
        if (newMsg && newMsg.payload) {
          this.updateBackUpTestData(newMsg.payload);
          this.updateSettingData(newMsg.payload);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .backup-test-ui {
    max-width: 500px;
    margin: 0 auto;
  }
  .buttons {
    display: flex;
    gap: 10px;
    margin-top: 20px;
  }
  .test-status,
  .test-result {
    margin-top: 20px;
  }
  </style>
  