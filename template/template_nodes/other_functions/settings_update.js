let saved_settings = msg.payload;

// Validate input: Ensure msg.payload is an array of objects
if (!Array.isArray(saved_settings) || !saved_settings.every(item => typeof item.id === "number")) {
    node.error("Invalid input: msg.payload must be an array of objects with numeric 'id' fields", msg);
    return null;
}

// Load global settings and the latest setting ID
let settings = global.get("settings") || [];
let latest_setting_id = global.get("latest_setting_id") || 0;

// Merge new settings into the existing ones
let existingIds = new Set(settings.map(s => s.id)); // Track existing IDs for duplicates
let newSettings = saved_settings.filter(setting => !existingIds.has(setting.id)); // Only add unique settings
settings.push(...newSettings); // Merge new settings into the existing array

// Update the latest setting ID if applicable
if (newSettings.length > 0) {
    latest_setting_id = Math.max(latest_setting_id, ...newSettings.map(s => s.id));
}

// Save updated settings and latest_setting_id globally
global.set("settings", settings);
global.set("latest_setting_id", latest_setting_id);

// Debugging logs
node.warn(`Updated settings: ${JSON.stringify(settings)}`);
node.warn(`Latest setting ID: ${latest_setting_id}`);

// Output updated settings and latest setting ID
return {
    payload: {
        settings: settings,
        latest_setting_id: latest_setting_id
    }
};
