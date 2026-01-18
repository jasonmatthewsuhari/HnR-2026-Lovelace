'use client'

import { useState, Suspense, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { Loader2 } from 'lucide-react'

// Dynamically import GLBViewerSimple to avoid SSR issues
const GLBViewerSimple = dynamic(
    () => import('./glb-viewer-simple').then((mod) => mod.GLBViewerSimple),
    {
        ssr: false,
        loading: () => (
            <div className="flex items-center justify-center h-full bg-transparent">
                <div className="text-center">
                    <Loader2 className="animate-spin h-8 w-8 text-white mx-auto mb-2" />
                    <p className="text-sm text-white/80">Loading 3D Viewer...</p>
                </div>
            </div>
        )
    }
)

interface GLBViewerWrapperProps {
    url: string
    width?: string
    height?: string
    className?: string
    autoRotate?: boolean
    enableControls?: boolean
    showAnimationControls?: boolean
    autoLoad?: boolean
    modelUrl?: string // Alternative prop name for compatibility
}

/**
 * SSR-safe GLB Viewer wrapper with optimized loading
 * - Preloads models for faster display
 * - Auto-loads by default in KYC flow
 * - Shows loading indicator
 */
export function GLBViewerWrapper({
    url,
    modelUrl,
    width = '100%',
    height = '400px',
    className = '',
    autoRotate = false,
    enableControls = true,
    showAnimationControls = true,
    autoLoad = true // Changed default to true for boyfriend selection
}: GLBViewerWrapperProps) {
    const [isLoaded, setIsLoaded] = useState(autoLoad)
    const [modelReady, setModelReady] = useState(false)

    // Use modelUrl if provided, otherwise use url
    const finalUrl = modelUrl || url

    // Auto-load after a short delay to prevent blocking
    useEffect(() => {
        if (!isLoaded && autoLoad) {
            const timer = setTimeout(() => {
                setIsLoaded(true)
            }, 100) // Small delay to prevent blocking UI
            return () => clearTimeout(timer)
        }
    }, [autoLoad, isLoaded])

    // Debug logging
    console.log('GLBViewerWrapper:', { url: finalUrl, autoLoad, isLoaded, modelReady })

    if (!isLoaded) {
        return (
            <div
                className={`flex items-center justify-center bg-transparent ${className}`}
                style={{ width, height }}
            >
                <div className="text-center">
                    <Loader2 className="animate-spin h-12 w-12 text-white mx-auto mb-4" />
                    <p className="text-white/80">Preparing 3D model...</p>
                </div>
            </div>
        )
    }

    return (
        <div className={className} style={{ width, height }}>
            <Suspense fallback={
                <div className="flex items-center justify-center h-full bg-transparent">
                    <div className="text-center">
                        <Loader2 className="animate-spin h-8 w-8 text-white mx-auto mb-2" />
                        <p className="text-sm text-white/80">Loading 3D model...</p>
                    </div>
                </div>
            }>
                <GLBViewerSimple
                    url={finalUrl}
                    width={width}
                    height={height}
                    autoRotate={autoRotate}
                />
            </Suspense>
        </div>
    )
}
