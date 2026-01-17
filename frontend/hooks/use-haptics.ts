import { useCallback, useEffect, useState } from 'react';
import haptics, { HapticStyle } from '@/lib/haptics';

/**
 * React hook for haptic feedback
 * Provides easy access to haptic functions and state
 */
export function useHaptics() {
    const [isSupported, setIsSupported] = useState(false);
    const [isEnabled, setIsEnabled] = useState(true);

    useEffect(() => {
        setIsSupported(haptics.isHapticsSupported());
        setIsEnabled(haptics.isHapticsEnabled());
    }, []);

    const trigger = useCallback((style: HapticStyle = 'medium') => {
        haptics.trigger(style);
    }, []);

    const triggerCustom = useCallback((pattern: number[]) => {
        haptics.triggerCustom(pattern);
    }, []);

    const toggleEnabled = useCallback(() => {
        const newState = !isEnabled;
        haptics.setEnabled(newState);
        setIsEnabled(newState);
    }, [isEnabled]);

    const setEnabled = useCallback((enabled: boolean) => {
        haptics.setEnabled(enabled);
        setIsEnabled(enabled);
    }, []);

    return {
        // State
        isSupported,
        isEnabled,

        // Controls
        trigger,
        triggerCustom,
        setEnabled,
        toggleEnabled,

        // Convenience methods
        buttonPress: haptics.buttonPress.bind(haptics),
        toggle: haptics.toggle.bind(haptics),
        selectionChange: haptics.selectionChange.bind(haptics),
        success: haptics.success.bind(haptics),
        warning: haptics.warning.bind(haptics),
        error: haptics.error.bind(haptics),
        impact: haptics.impact.bind(haptics),
        notification: haptics.notification.bind(haptics),
        heartbeat: haptics.heartbeat.bind(haptics),
        stop: haptics.stop.bind(haptics),
    };
}

/**
 * Hook to add haptic feedback to button clicks
 * Usage: const handleClick = useHapticClick(() => { ... }, 'medium');
 */
export function useHapticClick(
    onClick?: () => void,
    style: HapticStyle = 'medium'
) {
    return useCallback(() => {
        haptics.trigger(style);
        onClick?.();
    }, [onClick, style]);
}

/**
 * Hook to add haptic feedback to any event handler
 */
export function useHapticHandler<T extends (...args: any[]) => any>(
    handler: T,
    style: HapticStyle = 'medium'
): T {
    return useCallback((...args: Parameters<T>) => {
        haptics.trigger(style);
        return handler(...args);
    }, [handler, style]) as T;
}
