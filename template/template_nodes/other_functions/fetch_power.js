// Retrieve all_power_data from flow context
const allPowerData = flow.get("all_power_data");

if (!allPowerData || !Array.isArray(allPowerData)) {
    node.warn("No power data available or data is not an array.");
    return null;
}

// Function to send data one by one with a delay
async function sendDataWithDelay(dataArray) {
    for (const item of dataArray) {
        node.send({ payload: item }); // Send the data
        await new Promise(resolve => setTimeout(resolve, 1000)); // 1-second delay
    }
}

// Start the async process
sendDataWithDelay(allPowerData)
    .then(() => node.done()) // Mark node as done after sending all data
    .catch(err => node.error("Error sending data: " + err));
