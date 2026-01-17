// ============================================
// HAPTIC FEEDBACK - QUICK REFERENCE
// ============================================

// 1. IMPORT THE HOOK
import { useHaptics } from '@/hooks/use-haptics';

// 2. USE IN COMPONENT
function MyComponent() {
    const haptics = useHaptics();

    // Basic usage
    haptics.buttonPress();        // Medium haptic
    haptics.success();            // Success pattern
    haptics.error();              // Error pattern
    haptics.heartbeat();          // Romantic heartbeat 💜

    // All available methods:
    haptics.trigger('light');     // Trigger specific pattern
    haptics.buttonPress();        // Medium press
    haptics.toggle();             // Light toggle
    haptics.selectionChange();    // Quick selection
    haptics.success();            // Success double-tap
    haptics.warning();            // Warning triple-tap
    haptics.error();              // Error strong double-tap
    haptics.impact();             // Impact feedback
    haptics.notification();       // Notification pattern
    haptics.heartbeat();          // Heartbeat pattern

    // Custom pattern
    haptics.triggerCustom([50, 100, 50]); // [vibrate, pause, vibrate]

    // Control
    haptics.stop();               // Stop vibration
    haptics.setEnabled(false);    // Disable haptics
    haptics.toggleEnabled();      // Toggle on/off

    // Check status
    haptics.isSupported;          // Is device supported?
    haptics.isEnabled;            // Is haptics enabled?
}

// ============================================
// HAPTIC BUTTON COMPONENT
// ============================================

import { HapticButton } from '@/components/ui/haptic-button';

<HapticButton
    hapticStyle="medium"          // Pattern to use
    onClick={handleClick}
>
    Click Me!
</HapticButton>

// ============================================
// HAPTIC CLICK HOOK
// ============================================

import { useHapticClick } from '@/hooks/use-haptics';

const handleClick = useHapticClick(() => {
    console.log('Clicked with haptic!');
}, 'medium');

<button onClick={handleClick}>Click</button>

// ============================================
// HAPTIC PATTERNS
// ============================================

'light'      // 10ms    - Minor interactions
'medium'     // 20ms    - Button presses
'heavy'      // 40ms    - Important actions
'success'    // Pattern - Positive feedback
'warning'    // Pattern - Attention needed
'error'      // Pattern - Failed operation
'selection'  // 5ms     - Quick selections
'impact'     // 30ms    - Physical feedback

// ============================================
// SETTINGS COMPONENT
// ============================================

import { HapticSettings } from '@/components/haptic-settings';

<HapticSettings />  // Complete settings UI

// ============================================
// COMMON PATTERNS
// ============================================

// Button click
onClick = {() => haptics.buttonPress()}

// Success action
onSuccess = {() => haptics.success()}

// Error handling
onError = {() => haptics.error()}

// Toggle switch
onToggle = {() => haptics.toggle()}

// Selection change
onChange = {() => haptics.selectionChange()}

// Romantic moment
onLove = {() => {
    haptics.success();
    setTimeout(() => haptics.heartbeat(), 300);
}}

// Purchase
onPurchase = {() => haptics.trigger('heavy')}

// Camera shutter
onCapture = {() => haptics.impact()}

// ============================================
// DEVICE SUPPORT CHECK
// ============================================

const haptics = useHaptics();

if (haptics.isSupported) {
    // Show haptic settings
} else {
    // Hide haptic options
}

// ============================================
// TESTING
// ============================================

// Visit /haptic-demo for interactive testing
// Or test in console:
const haptics = useHaptics();
haptics.heartbeat(); // Test romantic pattern!
