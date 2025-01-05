// Ensure msg.payload contains the ID from the query result
if (!msg.payload || !msg.payload[0] || !msg.payload[0]['last_insert_rowid()']) {
    node.error("Invalid input: msg.payload must contain the result of last_insert_rowid().");
    return null;
}

// Extract the last inserted row ID
let lastInsertId = msg.payload[0]['last_insert_rowid()'];

// Retrieve the existing array from flow context or initialize it
let allMeasurementIds = flow.get("all_measurement_id") || [];
let latest_measurement=flow.get("latest_measurement");
let all_measurement_in_db=flow.get("all_measurement_in_db")||[];

let measurement_in_db={
    m_unique_id:null,
    m_db_row_id:null,
}
measurement_in_db.m_unique_id=latest_measurement.m_unique_id;
measurement_in_db.m_db_row_id=lastInsertId;

// Add the new ID to the array
allMeasurementIds.push(lastInsertId);
all_measurement_in_db.push(measurement_in_db);

// Save the updated array back to the flow context
flow.set("all_measurement_id", allMeasurementIds);
flow.set("all_measurement_in_db",all_measurement_in_db);

// Log the updated array for debugging (optional)
node.warn(`Updated all_measurement_id: ${JSON.stringify(allMeasurementIds)}`);
node.warn(`Updated all_measurement_in_db: ${JSON.stringify(all_measurement_in_db)} where the latest unique id ${latest_measurement.m_unique_id} maps to row id ${lastInsertId}` );
return msg;