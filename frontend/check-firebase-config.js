/**
 * Firebase Configuration Validator
 * Run this in the browser console on http://localhost:3000 to check your config
 */

console.log("=== Firebase Configuration Check ===");
console.log("");

const config = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

let hasErrors = false;

// Check API Key
if (!config.apiKey || config.apiKey === "your-api-key-here") {
  console.error("❌ API Key is missing or still has placeholder value");
  hasErrors = true;
} else if (!config.apiKey.startsWith("AIza")) {
  console.warn("⚠️ API Key doesn't look right (should start with 'AIza')");
  hasErrors = true;
} else {
  console.log("✅ API Key looks good");
}

// Check Auth Domain
if (config.authDomain === "lovelace-b8ef5.firebaseapp.com") {
  console.log("✅ Auth Domain is correct");
} else {
  console.error("❌ Auth Domain is incorrect");
  hasErrors = true;
}

// Check Project ID
if (config.projectId === "lovelace-b8ef5") {
  console.log("✅ Project ID is correct");
} else {
  console.error("❌ Project ID is incorrect");
  hasErrors = true;
}

// Check App ID
if (!config.appId || config.appId === "your-app-id-here") {
  console.error("❌ App ID is missing or still has placeholder value");
  hasErrors = true;
} else if (!config.appId.includes(":web:")) {
  console.warn("⚠️ App ID doesn't look right (should contain ':web:')");
  hasErrors = true;
} else {
  console.log("✅ App ID looks good");
}

// Check Messaging Sender ID
if (!config.messagingSenderId || config.messagingSenderId === "your-sender-id-here") {
  console.error("❌ Messaging Sender ID is missing or still has placeholder value");
  hasErrors = true;
} else {
  console.log("✅ Messaging Sender ID looks good");
}

console.log("");
if (hasErrors) {
  console.error("❌ Configuration has errors! Please update frontend/.env.local");
  console.log("");
  console.log("Get your config from:");
  console.log("https://console.firebase.google.com/project/lovelace-b8ef5/settings/general");
} else {
  console.log("✅ Configuration looks good! You should be able to authenticate.");
}
console.log("");
console.log("Current config (masked):");
console.log({
  apiKey: config.apiKey?.substring(0, 10) + "...",
  authDomain: config.authDomain,
  projectId: config.projectId,
  appId: config.appId?.substring(0, 20) + "...",
});
