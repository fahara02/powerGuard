<template>
  <div class="meter-container">
    <!-- Dynamic Header -->
    <div class="meter-header">
      <h2>{{ headerText }}</h2>
    </div>
    <!-- Multi-function Meter -->
    <div class="meter-display">
      <div class="meter-row">
        <div class="meter-item">
          <h3>Voltage</h3>
          <h1>{{ data.voltage }} V</h1>
        </div>
        <div class="meter-item">
          <h3>Current</h3>
          <h1>{{ data.current }} A</h1>
        </div>
      </div>
      <div class="meter-row">
        <div class="meter-item">
          <h3>Power</h3>
          <h1>{{ data.power }} W</h1>
        </div>
        <div class="meter-item">
          <h3>Energy</h3>
          <h1>{{ data.energy }} kWh</h1>
        </div>
      </div>
      <div class="meter-row">
        <div class="meter-item">
          <h3>Power Factor</h3>
          <h1>{{ data.pf }}</h1>
        </div>
        <div class="meter-item">
          <h3>Frequency</h3>
          <h1>{{ data.frequency }} Hz</h1>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      data: {
        type: 0, // Default to INPUT_POWER
        voltage: 0,
        current: 0,
        power: 0,
        energy: 0,
        pf: 0,
        frequency: 0,

      },
      dataType: {
        INPUT_POWER: 0,
        OUTPUT_POWER: 1,
      },
    };
  },
  computed: {
    // Determine header text based on data type
    headerText() {
      return this.data.type === this.dataType.INPUT_POWER
        ? "Input Power"
        : "Output Power";
    },
  },
  methods: {
    updatePowerData(payload) {
      if (payload) {
        this.data = { ...this.data, ...payload }; // Merge new data with existing data
      } else {
        console.error("Invalid payload:", payload);
      }
    },
  },
  mounted() {
    this.$watch(
      "msg",
      (newMsg) => {
        if (newMsg && newMsg.payload) {
          this.updatePowerData(newMsg.payload);
        }
      },
      { deep: true }
    );
  },
};
</script>

<style scoped>
/* Outer Container */
.meter-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background-color: #222;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5);
  max-width: 600px;
  margin: auto;
}

/* Header Styling */
.meter-header {
  margin-bottom: 15px;
  text-align: center;
}

.meter-header h2 {
  color: #fff;
  font-family: "Courier New", Courier, monospace;
  font-size: 1.5rem;
  margin: 0;
}

/* Inner Display */
.meter-display {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-family: "Courier New", Courier, monospace;
  color: #fff;
}

/* Rows for Data */
.meter-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

/* Individual Items */
.meter-item {
  background-color: #333;
  flex: 1;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.7);
}

/* Heading and Value Styling */
.meter-item h3 {
  margin: 0;
  font-size: 1rem;
  color: #aaa;
}

.meter-item h1 {
  margin: 5px 0 0;
  font-size: 1.5rem;
  color: #fff;
}
</style>
