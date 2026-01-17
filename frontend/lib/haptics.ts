/**
 * Haptic Feedback Utility
 * Provides haptic feedback across different platforms:
 * - Native mobile (iOS/Android) via Vibration API
 * - Web browsers with Vibration API support
 * - Graceful fallback for unsupported platforms
 */

export type HapticStyle =
    | 'light'      // Subtle feedback for UI interactions
    | 'medium'     // Standard feedback for buttons
    | 'heavy'      // Strong feedback for important actions
    | 'success'    // Positive feedback pattern
    | 'warning'    // Attention-grabbing pattern
    | 'error'      // Error indication pattern
    | 'selection'  // Quick tap for selections
    | 'impact';    // Physical impact simulation

interface HapticPattern {
    pattern: number[];
    description: string;
}

const HAPTIC_PATTERNS: Record<HapticStyle, HapticPattern> = {
    light: {
        pattern: [10],
        description: 'Light tap'
    },
    medium: {
        pattern: [20],
        description: 'Medium tap'
    },
    heavy: {
        pattern: [40],
        description: 'Heavy tap'
    },
    success: {
        pattern: [10, 50, 10],
        description: 'Success double-tap'
    },
    warning: {
        pattern: [20, 100, 20, 100, 20],
        description: 'Warning triple-tap'
    },
    error: {
        pattern: [50, 100, 50],
        description: 'Error strong double-tap'
    },
    selection: {
        pattern: [5],
        description: 'Quick selection tap'
    },
    impact: {
        pattern: [30],
        description: 'Impact feedback'
    }
};

class HapticsManager {
    private isSupported: boolean = false;
    private isEnabled: boolean = true;

    constructor() {
        // Check if Vibration API is supported
        this.isSupported = 'vibrate' in navigator;

        // Load user preference from localStorage
        const savedPreference = localStorage.getItem('haptics-enabled');
        if (savedPreference !== null) {
            this.isEnabled = savedPreference === 'true';
        }
    }

    /**
     * Check if haptics are supported on this device
     */
    public isHapticsSupported(): boolean {
        return this.isSupported;
    }

    /**
     * Check if haptics are currently enabled
     */
    public isHapticsEnabled(): boolean {
        return this.isEnabled;
    }

    /**
     * Enable or disable haptic feedback
     */
    public setEnabled(enabled: boolean): void {
        this.isEnabled = enabled;
        localStorage.setItem('haptics-enabled', enabled.toString());
    }

    /**
     * Trigger haptic feedback with a specific style
     */
    public trigger(style: HapticStyle = 'medium'): void {
        if (!this.isSupported || !this.isEnabled) {
            return;
        }

        const haptic = HAPTIC_PATTERNS[style];

        try {
            navigator.vibrate(haptic.pattern);
        } catch (error) {
            console.warn('Haptic feedback failed:', error);
        }
    }

    /**
     * Trigger a custom vibration pattern
     * @param pattern Array of vibration durations in milliseconds
     */
    public triggerCustom(pattern: number[]): void {
        if (!this.isSupported || !this.isEnabled) {
            return;
        }

        try {
            navigator.vibrate(pattern);
        } catch (error) {
            console.warn('Custom haptic feedback failed:', error);
        }
    }

    /**
     * Stop any ongoing vibration
     */
    public stop(): void {
        if (!this.isSupported) {
            return;
        }

        try {
            navigator.vibrate(0);
        } catch (error) {
            console.warn('Failed to stop haptic feedback:', error);
        }
    }

    /**
     * Trigger haptic feedback for button press
     */
    public buttonPress(): void {
        this.trigger('medium');
    }

    /**
     * Trigger haptic feedback for toggle/switch
     */
    public toggle(): void {
        this.trigger('light');
    }

    /**
     * Trigger haptic feedback for selection change
     */
    public selectionChange(): void {
        this.trigger('selection');
    }

    /**
     * Trigger haptic feedback for successful action
     */
    public success(): void {
        this.trigger('success');
    }

    /**
     * Trigger haptic feedback for warning
     */
    public warning(): void {
        this.trigger('warning');
    }

    /**
     * Trigger haptic feedback for error
     */
    public error(): void {
        this.trigger('error');
    }

    /**
     * Trigger haptic feedback for impact (e.g., drag and drop)
     */
    public impact(): void {
        this.trigger('impact');
    }

    /**
     * Trigger haptic feedback for notification
     */
    public notification(): void {
        this.triggerCustom([10, 50, 10, 50, 10]);
    }

    /**
     * Trigger haptic feedback for heartbeat pattern (for romantic moments!)
     */
    public heartbeat(): void {
        this.triggerCustom([30, 100, 50, 500, 30, 100, 50]);
    }
}

// Create singleton instance
const haptics = new HapticsManager();

// Export singleton and types
export { haptics };
export default haptics;
