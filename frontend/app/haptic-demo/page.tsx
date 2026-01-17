"use client"

import { HapticSettings } from '@/components/haptic-settings';
import { useHaptics } from '@/hooks/use-haptics';
import { HapticButton } from '@/components/ui/haptic-button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Heart, ShoppingBag, Camera, Video, Star } from 'lucide-react';

/**
 * Haptic Demo Page
 * Demonstrates haptic feedback in various scenarios
 */
export default function HapticDemoPage() {
    const haptics = useHaptics();

    return (
        <div className="container max-w-4xl py-8 space-y-8">
            <div>
                <h1 className="text-4xl font-bold mb-2">Haptic Feedback Demo</h1>
                <p className="text-muted-foreground">
                    Experience the tactile feedback on your mobile device
                </p>
            </div>

            {/* Settings */}
            <HapticSettings />

            {/* Demo Scenarios */}
            <Card>
                <CardHeader>
                    <CardTitle>Interactive Scenarios</CardTitle>
                    <CardDescription>
                        Try these buttons to feel different haptic patterns in context
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {/* Romantic Interaction */}
                    <div className="space-y-2">
                        <h3 className="font-semibold flex items-center gap-2">
                            <Heart className="h-4 w-4 text-pink-500" />
                            Romantic Moments
                        </h3>
                        <div className="flex gap-2">
                            <HapticButton
                                hapticStyle="success"
                                variant="default"
                                className="bg-gradient-to-r from-purple-300/90 via-pink-200/80 to-blue-200/70 text-foreground hover:from-purple-300 hover:via-pink-200 hover:to-blue-200"
                                onHapticClick={() => {
                                    setTimeout(() => haptics.heartbeat(), 200);
                                }}
                            >
                                💕 Send Love
                            </HapticButton>
                            <HapticButton
                                hapticStyle="light"
                                variant="outline"
                                onHapticClick={() => console.log('Favorited!')}
                            >
                                ⭐ Add to Favorites
                            </HapticButton>
                        </div>
                    </div>

                    {/* Shopping Actions */}
                    <div className="space-y-2">
                        <h3 className="font-semibold flex items-center gap-2">
                            <ShoppingBag className="h-4 w-4 text-blue-500" />
                            Shopping Experience
                        </h3>
                        <div className="flex gap-2">
                            <HapticButton
                                hapticStyle="medium"
                                variant="default"
                            >
                                🛒 Add to Cart
                            </HapticButton>
                            <HapticButton
                                hapticStyle="heavy"
                                variant="default"
                                className="bg-green-600 hover:bg-green-700"
                            >
                                💳 Purchase Now
                            </HapticButton>
                        </div>
                    </div>

                    {/* Media Actions */}
                    <div className="space-y-2">
                        <h3 className="font-semibold flex items-center gap-2">
                            <Camera className="h-4 w-4 text-purple-500" />
                            Media Interactions
                        </h3>
                        <div className="flex gap-2">
                            <HapticButton
                                hapticStyle="impact"
                                variant="outline"
                            >
                                📸 Take Photo
                            </HapticButton>
                            <HapticButton
                                hapticStyle="medium"
                                variant="outline"
                            >
                                <Video className="h-4 w-4" />
                                Start Video Call
                            </HapticButton>
                        </div>
                    </div>

                    {/* Feedback Actions */}
                    <div className="space-y-2">
                        <h3 className="font-semibold flex items-center gap-2">
                            <Star className="h-4 w-4 text-yellow-500" />
                            Outfit Judging
                        </h3>
                        <div className="flex gap-2">
                            <HapticButton
                                hapticStyle="success"
                                variant="default"
                                className="bg-green-600 hover:bg-green-700"
                            >
                                ✅ Love It!
                            </HapticButton>
                            <HapticButton
                                hapticStyle="warning"
                                variant="default"
                                className="bg-yellow-600 hover:bg-yellow-700"
                            >
                                ⚠️ Not Sure
                            </HapticButton>
                            <HapticButton
                                hapticStyle="error"
                                variant="destructive"
                            >
                                ❌ Not For You
                            </HapticButton>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Info Card */}
            <Card className="border-blue-200 bg-blue-50/50 dark:bg-blue-950/20">
                <CardContent className="pt-6">
                    <p className="text-sm text-muted-foreground">
                        <strong>💡 Tip:</strong> For the best experience, use this demo on an Android device with Chrome.
                        iOS has limited haptic support through the web browser. Each button demonstrates a different
                        haptic pattern that matches the action's importance and context.
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
