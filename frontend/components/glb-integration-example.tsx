/**
 * GLB Integration Examples
 *
 * This file shows different ways to integrate GLB viewing into your Lovelace app
 */

'use client'

import { GLBViewer } from './glb-viewer'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

// Example 1: Simple GLB viewer in a wardrobe item card
export function WardrobeItem3D({ itemId, glbUrl }: { itemId: string; glbUrl?: string }) {
    const [show3D, setShow3D] = useState(false)

    if (!glbUrl) {
        return (
            <div className="p-4 border rounded-lg">
                <p className="text-sm text-muted-foreground">No 3D model available</p>
            </div>
        )
    }

    return (
        <div className="space-y-4">
            <Button
                variant="outline"
                onClick={() => setShow3D(!show3D)}
                className="w-full"
            >
                {show3D ? 'Hide 3D View' : 'View in 3D'}
            </Button>

            {show3D && (
                <GLBViewer
                    url={glbUrl}
                    height="300px"
                    autoRotate={true}
                    showAnimationControls={false}
                    enableControls={true}
                />
            )}
        </div>
    )
}

// Example 2: Virtual try-on with GLB clothing model
export function VirtualTryOnClothing({ clothingGlbUrl }: { clothingGlbUrl: string }) {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
                <h3 className="text-lg font-semibold mb-4">Your Avatar</h3>
                {/* Avatar viewer would go here */}
                <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                    <p className="text-muted-foreground">Avatar View</p>
                </div>
            </div>

            <div>
                <h3 className="text-lg font-semibold mb-4">Clothing Preview</h3>
                <GLBViewer
                    url={clothingGlbUrl}
                    height="400px"
                    autoRotate={true}
                    showAnimationControls={true}
                    enableControls={true}
                />
            </div>
        </div>
    )
}

// Example 3: Product showcase with multiple viewing options
export function ProductShowcase({ product }: { product: { id: string; name: string; glbUrl?: string; imageUrl: string } }) {
    const [viewMode, setViewMode] = useState<'image' | '3d'>('image')

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold">{product.name}</h2>
                <div className="flex space-x-2">
                    <Button
                        variant={viewMode === 'image' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setViewMode('image')}
                    >
                        Photo
                    </Button>
                    <Button
                        variant={viewMode === '3d' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setViewMode('3d')}
                        disabled={!product.glbUrl}
                    >
                        3D View
                    </Button>
                </div>
            </div>

            <div className="aspect-square border rounded-lg overflow-hidden">
                {viewMode === 'image' ? (
                    <img
                        src={product.imageUrl}
                        alt={product.name}
                        className="w-full h-full object-cover"
                    />
                ) : product.glbUrl ? (
                    <GLBViewer
                        url={product.glbUrl}
                        width="100%"
                        height="100%"
                        autoRotate={true}
                        showAnimationControls={true}
                        enableControls={true}
                    />
                ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                        <p>3D model not available</p>
                    </div>
                )}
            </div>
        </div>
    )
}

// Example 4: Animated model gallery
export function ModelGallery({ models }: { models: Array<{ id: string; name: string; glbUrl: string; hasAnimations: boolean }> }) {
    const [selectedModel, setSelectedModel] = useState<string | null>(null)

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {models.map((model) => (
                    <div
                        key={model.id}
                        className={`border rounded-lg p-3 cursor-pointer transition-colors ${selectedModel === model.id ? 'border-primary bg-primary/5' : 'hover:border-primary/50'
                            }`}
                        onClick={() => setSelectedModel(model.id)}
                    >
                        <div className="aspect-square bg-muted rounded mb-2 flex items-center justify-center text-xs">
                            <span className="text-muted-foreground">3D</span>
                        </div>
                        <p className="text-sm font-medium truncate">{model.name}</p>
                        {model.hasAnimations && (
                            <span className="text-xs text-primary">Animated</span>
                        )}
                    </div>
                ))}
            </div>

            {selectedModel && (
                <div className="border-t pt-6">
                    <GLBViewer
                        url={models.find(m => m.id === selectedModel)?.glbUrl || ''}
                        height="500px"
                        showAnimationControls={true}
                        enableControls={true}
                    />
                </div>
            )}
        </div>
    )
}