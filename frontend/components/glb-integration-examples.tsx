'use client'

import { useState } from 'react'
import { GLBViewerWrapper } from './glb-viewer-wrapper'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

/**
 * Example: Simple GLB viewer for wardrobe items
 */
export function WardrobeGLBViewer({ glbUrl, itemName }: { glbUrl?: string; itemName: string }) {
    const [isExpanded, setIsExpanded] = useState(false)

    if (!glbUrl) {
        return (
            <Card>
                <CardContent className="p-4">
                    <p className="text-sm text-muted-foreground text-center">
                        No 3D model available for {itemName}
                    </p>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    {itemName}
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsExpanded(!isExpanded)}
                    >
                        {isExpanded ? 'Hide 3D' : 'View 3D'}
                    </Button>
                </CardTitle>
            </CardHeader>
            {isExpanded && (
                <CardContent>
                    <GLBViewerWrapper
                        url={glbUrl}
                        height="300px"
                        autoRotate={true}
                        showAnimationControls={false}
                    />
                </CardContent>
            )}
        </Card>
    )
}

/**
 * Example: Product showcase with 2D/3D toggle
 */
export function ProductShowcase({
    product
}: {
    product: {
        id: string
        name: string
        imageUrl: string
        glbUrl?: string
    }
}) {
    const [viewMode, setViewMode] = useState<'image' | '3d'>('image')

    return (
        <Card>
            <CardHeader>
                <CardTitle>{product.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex gap-2">
                    <Button
                        variant={viewMode === 'image' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setViewMode('image')}
                    >
                        Photo View
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

                <div className="aspect-square bg-muted rounded-lg overflow-hidden">
                    {viewMode === 'image' ? (
                        <img
                            src={product.imageUrl}
                            alt={product.name}
                            className="w-full h-full object-cover"
                        />
                    ) : product.glbUrl ? (
                        <GLBViewerWrapper
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
            </CardContent>
        </Card>
    )
}

/**
 * Example: Virtual try-on with clothing model
 */
export function VirtualTryOn({
    clothingGlbUrl,
    userPhotoUrl
}: {
    clothingGlbUrl: string
    userPhotoUrl?: string
}) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
                <CardHeader>
                    <CardTitle>Your Photo</CardTitle>
                </CardHeader>
                <CardContent>
                    {userPhotoUrl ? (
                        <img
                            src={userPhotoUrl}
                            alt="Your photo"
                            className="w-full aspect-square object-cover rounded-lg"
                        />
                    ) : (
                        <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                            <p className="text-muted-foreground">Upload your photo</p>
                        </div>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Clothing Preview</CardTitle>
                </CardHeader>
                <CardContent>
                    <GLBViewerWrapper
                        url={clothingGlbUrl}
                        height="400px"
                        autoRotate={true}
                        showAnimationControls={true}
                        enableControls={true}
                    />
                </CardContent>
            </Card>
        </div>
    )
}

/**
 * Example: Model gallery with multiple GLB files
 */
export function GLBModelGallery({
    models
}: {
    models: Array<{
        id: string
        name: string
        glbUrl: string
        thumbnail?: string
    }>
}) {
    const [selectedModel, setSelectedModel] = useState<string | null>(null)

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {models.map((model) => (
                    <Card
                        key={model.id}
                        className={`cursor-pointer transition-colors ${selectedModel === model.id ? 'ring-2 ring-primary' : ''
                            }`}
                        onClick={() => setSelectedModel(model.id)}
                    >
                        <CardContent className="p-4">
                            {model.thumbnail ? (
                                <img
                                    src={model.thumbnail}
                                    alt={model.name}
                                    className="w-full aspect-square object-cover rounded mb-2"
                                />
                            ) : (
                                <div className="w-full aspect-square bg-muted rounded mb-2 flex items-center justify-center">
                                    <span className="text-2xl">📦</span>
                                </div>
                            )}
                            <p className="text-sm font-medium text-center">{model.name}</p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {selectedModel && (
                <Card>
                    <CardHeader>
                        <CardTitle>
                            {models.find(m => m.id === selectedModel)?.name}
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <GLBViewerWrapper
                            url={models.find(m => m.id === selectedModel)?.glbUrl || ''}
                            height="500px"
                            showAnimationControls={true}
                            enableControls={true}
                        />
                    </CardContent>
                </Card>
            )}
        </div>
    )
}