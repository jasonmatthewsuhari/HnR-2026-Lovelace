"use client"

import { useHaptics } from '@/hooks/use-haptics';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Smartphone, Vibrate } from 'lucide-react';
import { Button } from '@/components/ui/button';

/**
 * Haptic Settings Component
 * Allows users to toggle haptic feedback and test different patterns
 */
export function HapticSettings() {
    const haptics = useHaptics();

    const testPatterns = [
        { name: 'Light', style: 'light' as const, description: 'Subtle tap' },
        { name: 'Medium', style: 'medium' as const, description: 'Standard button press' },
        { name: 'Heavy', style: 'heavy' as const, description: 'Strong feedback' },
        { name: 'Success', style: 'success' as const, description: 'Double-tap success' },
        { name: 'Error', style: 'error' as const, description: 'Error pattern' },
        { name: 'Heartbeat', style: 'heartbeat' as const, description: 'Romantic heartbeat 💜' },
    ];

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Vibrate className="h-5 w-5" />
                    <CardTitle>Haptic Feedback</CardTitle>
                </div>
                <CardDescription>
                    {haptics.isSupported
                        ? 'Customize vibration feedback for a more immersive experience'
                        : 'Haptic feedback is not supported on this device'}
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
                {/* Enable/Disable Toggle */}
                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label htmlFor="haptics-toggle" className="text-base">
                            Enable Haptics
                        </Label>
                        <p className="text-sm text-muted-foreground">
                            Feel vibrations when interacting with the app
                        </p>
                    </div>
                    <Switch
                        id="haptics-toggle"
                        checked={haptics.isEnabled}
                        onCheckedChange={(checked) => {
                            haptics.setEnabled(checked);
                            if (checked) {
                                haptics.success();
                            }
                        }}
                        disabled={!haptics.isSupported}
                    />
                </div>

                {/* Test Patterns */}
                {haptics.isSupported && haptics.isEnabled && (
                    <div className="space-y-3">
                        <Label className="text-base">Test Haptic Patterns</Label>
                        <div className="grid grid-cols-2 gap-2">
                            {testPatterns.map((pattern) => (
                                <Button
                                    key={pattern.name}
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                        if (pattern.style === 'heartbeat') {
                                            haptics.heartbeat();
                                        } else {
                                            haptics.trigger(pattern.style);
                                        }
                                    }}
                                    className="justify-start"
                                >
                                    <div className="text-left">
                                        <div className="font-medium">{pattern.name}</div>
                                        <div className="text-xs text-muted-foreground">
                                            {pattern.description}
                                        </div>
                                    </div>
                                </Button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Device Info */}
                <div className="rounded-lg bg-muted p-3 text-sm">
                    <div className="flex items-start gap-2">
                        <Smartphone className="h-4 w-4 mt-0.5 text-muted-foreground" />
                        <div className="space-y-1">
                            <p className="font-medium">Device Support</p>
                            <p className="text-muted-foreground">
                                {haptics.isSupported
                                    ? '✅ Your device supports haptic feedback'
                                    : '❌ Haptic feedback requires a mobile device with vibration support (Android recommended)'}
                            </p>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
