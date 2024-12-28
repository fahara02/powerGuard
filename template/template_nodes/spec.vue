<template>
  <div class="form-container">
    <h2>UPS Specification Form</h2>
    <form @submit.prevent="submitForm">
      <!-- Phase Selection -->
      <label for="phase">Phase:</label>
      <select v-model="formData.phase" id="phase">
        <option :value="0">Single Phase</option>
        <option :value="1">Three Phase</option>
      </select>

      <!-- Rated VA -->
      <label for="rated_va">Rated VA:</label>
      <input type="number" v-model="formData.rated_va" id="rated_va" />

      <!-- Rated Voltage -->
      <label for="rated_voltage">Rated Voltage:</label>
      <input type="number" v-model="formData.rated_voltage" id="rated_voltage" />

      <!-- Rated Current -->
      <label for="rated_current">Rated Current:</label>
      <input type="number" v-model="formData.rated_current" id="rated_current" />

      <!-- Minimum Input Voltage -->
      <label for="min_input_voltage">Minimum Input Voltage:</label>
      <input type="number" v-model="formData.min_input_voltage" id="min_input_voltage" />

      <!-- Maximum Input Voltage -->
      <label for="max_input_voltage">Maximum Input Voltage:</label>
      <input type="number" v-model="formData.max_input_voltage" id="max_input_voltage" />

      <!-- PF Rated Current -->
<label for="pf_rated_current">Power Factor Rated Current (0-1):</label>
<input 
  type="number" 
  v-model="formData.pf_rated_current" 
  id="pf_rated_current" 
  step="0.01" 
  min="0" 
  max="1" 
/>


      <!-- Max Continuous Amp -->
      <label for="max_continous_amp">Max Continuous Amp:</label>
      <input type="number" v-model="formData.max_continous_amp" id="max_continous_amp" />

      <!-- Overload Amp -->
      <label for="overload_amp">Overload Amp:</label>
      <input type="number" v-model="formData.overload_amp" id="overload_amp" />

      <!-- Overload Long -->
      <h3>Overload Long</h3>
      <label for="long_load_percentage">Load Percentage:</label>
      <input type="number" v-model="formData.overload_long.load_percentage" id="long_load_percentage" />

      <label for="long_overload_time">Overload Time (min):</label>
      <input type="number" v-model="formData.overload_long.overload_time_min" id="long_overload_time" />

      <!-- Overload Medium -->
      <h3>Overload Medium</h3>
      <label for="medium_load_percentage">Load Percentage:</label>
      <input type="number" v-model="formData.overload_medium.load_percentage" id="medium_load_percentage" />

      <label for="medium_overload_time">Overload Time (min):</label>
      <input type="number" v-model="formData.overload_medium.overload_time_min" id="medium_overload_time" />

      <!-- Overload Short -->
      <h3>Overload Short</h3>
      <label for="short_load_percentage">Load Percentage:</label>
      <input type="number" v-model="formData.overload_short.load_percentage" id="short_load_percentage" />

      <label for="short_overload_time">Overload Time (min):</label>
      <input type="number" v-model="formData.overload_short.overload_time_min" id="short_overload_time" />

      <!-- Average Switch Time -->
      <label for="avg_switch_time">Average Switch Time (ms):</label>
      <input type="number" v-model="formData.avg_switch_time_ms" id="avg_switch_time" />

      <!-- Average Backup Time -->
      <label for="avg_backup_time">Average Backup Time (ms):</label>
      <input type="number" v-model="formData.avg_backup_time_ms" id="avg_backup_time" />

      <button type="submit">Submit</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      formData: {
        phase: 0,
        rated_va: 1000,
        rated_voltage: 230,
        rated_current: 10,
        min_input_voltage: 180,
        max_input_voltage: 260,
        pf_rated_current: 0.9,
        max_continous_amp: 15,
        overload_amp: 20,
        overload_long: {
          load_percentage: 110,
          overload_time_min: 30,
        },
        overload_medium: {
          load_percentage: 125,
          overload_time_min: 10,
        },
        overload_short: {
          load_percentage: 150,
          overload_time_min: 1,
        },
        avg_switch_time_ms: 5,
        avg_backup_time_ms: 300000,
      },
    };
  },
  methods: {
    submitForm() {
      const msg = { payload: this.formData };
      this.send(msg);

    },
  },
};
</script>


<style scoped>
  .form-container {
    max-width: 900px;
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

  input, select, button {
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
    margin-bottom: 5px;
  }
</style>
