<template>
    <div class="backup-test-ui">
      <h1>Backup Test Control</h1>
      <form @submit.prevent="startBackupTest">
        <div>
              <!-- Setting  ID Dropdown -->
        <label for="setting_id">Report Settings ID:</label>
        <select v-model="formData.setting_id" id="setting_id" required>
          <option v-for="id in settingOptions" :key="id" :value="id">{{ id }}</option>
        </select>
          <label for="load-type">Load Type:</label>
          <select v-model="loadType" id="load-type" required>
            <option v-for="(value, key) in loadTypes" :key="key" :value="value">
              {{ key }}
            </option>
          </select>
        </div>
        <div>
          <label for="step-id">Step ID:</label>
          <input type="number" v-model.number="stepId" id="step-id" required min="0" />
        </div>
        <div>
          <label for="load-percentage">Load Percentage:</label>
          <input type="number" v-model.number="loadPercentage" id="load-percentage" required min="0" max="100" />
        </div>

         <!-- Display Spec Data -->
         <div v-if="selectedSetting">
          <h3>Setting Details:</h3>
          <p><strong>Report Id:</strong> {{ selectedSetting.report_id }}</p>
          <p><strong>Standard:</strong> {{ selectedSetting.standard }}</p>
          <p><strong>UPS_Model:</strong> {{ selectedSetting.ups_model }}</p>
          <p><strong>Client Name:</strong> {{ selectedSetting.client_name }}</p>
          <p><strong>Brand Name:</strong> {{ selectedSetting.brand_name }}</p>
          <p><strong>Test Engineer Name:</strong> {{ selectedSetting.test_engineer_name }}</p>
          <p><strong>Test Approval Name:</strong> {{ selectedSetting.test_approval_name }}</p>
          <p><strong>UPS_SPEC_ID:</strong> {{ selectedSetting.spec_id }}</p>
     
         </div>

        <div class="buttons">
          <button type="submit" :disabled="backupTestRunning">Start Test</button>
          <button type="button" @click="stopBackupTest" :disabled="!backupTestRunning">Stop Test</button>
        </div>
      </form>
      <div v-if="backupTestRunning" class="test-status">
        <p>Test running... Backup time: {{ backupTime }} seconds</p>
      </div>
      <div v-if="!backupTestRunning && backupTime > 0" class="test-result">
        <h2>Test Result</h2>
        <p>Total Backup Time: {{ backupTime }} seconds</p>
        <ul>
          <li v-for="(value, key) in finalOutputData" :key="key">
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
        latest_settings_id:0,
        setting:[],
        loadTypes: {
        LINEAR: 0,
        NON_LINEAR: 1,
      },
      formData: {
         setting_id:0,
         loadType: 0,
         stepId: 0,
         loadPercentage: 0,
        },




       
        
        backupTime: 0,
        finalOutputData: {},
        backupTestRunning: false,
        BackUpTestData:{
           BackupTime:0,
           sense_mains_input:0,
           sense_ups_output:0,
           alarm_status:0,
           inputPdata:{},
           outputPdata:{},          
           backupTestRunning:false 
          }

      };
    },
    computed: {
      settingOptions() {
        return this.setting.map((setting) => setting.id).sort((a, b) => a - b);
      },
      selectedSetting() {
        return this.setting.find((setting) => setting.id === this.formData.setting_id) || null;
      },
    },





    methods: {
        updateBackUpTestData(payload) {
        if (payload.latest_settings_id !== undefined) {
          this.BackUpTestData.latest_spec_id = payload.latest_spec_id;
        }
        if (payload.spec && Array.isArray(payload.spec)) {
          this.spec = payload.spec;
        } else {
          console.error("Spec data is not properly formatted:", payload.spec);
        }
  
       
      },
      updateSettingData(payload){

        if (payload.SettingData.latest_setting_id !== undefined) {
          this.latest_setting_id = payload.SettingData.latest_setting_id;
        }
        if (payload.SettingData && Array.isArray(payload.SettingData.setting)) {
          this.setting = payload.SettingData.setting;
        } else {
          console.error("Setting data is not properly formatted:", payload.SettingData.setting);
        }
  
        const latestSetting = this.setting.find((setting) => setting.id === this.setting.latest_setting_id - 1);
        if (!this.formData.setting_id && latestSetting ) {
          this.formData.setting_id = latestSetting.id;
        }


      },


      async startBackupTest() {
        this.backupTestRunning = true;
        this.backupTime = 0;
        const msg:{payload: true,
          load_type: this.loadType,
          step_id: this.stepId,
          load_percentage: this.loadPercentage};
          this.send(msg);
      
  
        // Simulate monitoring the backup time
        const interval = setInterval(() => {
          this.backupTime++;
          if (!this.backupTestRunning) clearInterval(interval);
        }, 1000);
      },
      stopBackupTest() {
        this.backupTestRunning = false;
  
        const msg:{payload: false
          };
          this.send(msg);
  
        // Simulate fetching final data
        this.finalOutputData = {
          Voltage: 220,
          Current: 10,
          Power: 2.2,
          Efficiency: 0.9,
          Temperature: 45,
        };
      },
    },
    mounted() {
      this.$watch('msg', (newMsg) => {
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
    max-width: 400px;
    margin: 0 auto;
  }
  .buttons {
    display: flex;
    gap: 10px;
  }
  .test-status,
  .test-result {
    margin-top: 20px;
  }
  </style>
  