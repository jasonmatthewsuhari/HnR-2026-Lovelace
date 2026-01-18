'use client'

import React, { Suspense, useRef, useState, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, useGLTF } from '@react-three/drei'
import { Group, Box3, Vector3 } from 'three'

interface GLBViewerSimpleProps {
    url: string
    width?: string
    height?: string
    className?: string
    autoRotate?: boolean
}

// Component to handle GLB loading and basic rotation
function SimpleGLBModel({ url, autoRotate = false }: { url: string; autoRotate: boolean }) {
    const groupRef = useRef<Group>(null)
    const [isPositioned, setIsPositioned] = useState(false)

    // Load GLB model
    const { scene } = useGLTF(url)

    // Log loading status
    console.log('Loading GLB model:', url, 'Scene loaded:', !!scene)

    if (!scene) {
        console.warn('GLB scene not loaded yet:', url)
        return null
    }

    // Clone the scene to avoid sharing geometry
    const clonedScene = scene.clone()

    // Auto-center and scale the model on first load
    useEffect(() => {
        if (groupRef.current && !isPositioned) {
            const group = groupRef.current

            console.log('Group reference:', group)
            console.log('Group children:', group.children)

            // Compute bounding box
            const box = new Box3().setFromObject(group)
            const size = box.getSize(new Vector3())
            const center = box.getCenter(new Vector3())

            console.log('Bounding box:', {
                min: box.min,
                max: box.max,
                size: { x: size.x, y: size.y, z: size.z },
                center: { x: center.x, y: center.y, z: center.z }
            })

            // Center the model
            group.position.x = -center.x
            group.position.y = -center.y
            group.position.z = -center.z

            // Scale to fit (target size of 2 units)
            const maxDim = Math.max(size.x, size.y, size.z)
            const scale = maxDim > 0 ? 2 / maxDim : 1
            group.scale.setScalar(scale)

            console.log('Model positioned:', {
                position: { x: group.position.x, y: group.position.y, z: group.position.z },
                scale: scale
            })
            setIsPositioned(true)
        }
    }, [isPositioned])

    // Handle rotation
    useFrame(() => {
        if (autoRotate && groupRef.current) {
            groupRef.current.rotation.y += 0.01
        }
    })

    return (
        <group ref={groupRef}>
            <primitive object={clonedScene} />
        </group>
    )
}

// Simple GLB Viewer Component
export function GLBViewerSimple({
    url,
    width = '100%',
    height = '400px',
    className = '',
    autoRotate = false
}: GLBViewerSimpleProps) {
    const [hasError, setHasError] = useState(false)

    // Reset loading state when URL changes
    useEffect(() => {
        setHasError(false)
    }, [url])

    if (hasError) {
        return (
            <div className={`relative ${className}`} style={{ width, height }}>
                <div className="flex items-center justify-center h-full bg-red-50 rounded-lg border border-red-200">
                    <div className="text-center">
                        <div className="text-red-500 mb-2">❌</div>
                        <p className="text-sm text-red-700 font-medium">Failed to load 3D model</p>
                        <p className="text-xs text-red-600 mt-1">URL: {url.split('/').pop()}</p>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className={`relative ${className}`} style={{ width, height }}>
            <Suspense fallback={
                <div className="flex items-center justify-center h-full bg-gray-100 rounded-lg">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
                        <p className="text-sm text-gray-600">Loading 3D Model...</p>
                        <p className="text-xs text-gray-500 mt-1">{url.split('/').pop()}</p>
                    </div>
                </div>
            }>
                <Canvas
                    camera={{ position: [0, 0, 5], fov: 50 }}
                    style={{ background: 'transparent' }}
                    gl={{ alpha: true, antialias: true }}
                    onCreated={({ gl }) => {
                        console.log('Canvas created, WebGL context:', gl)
                    }}
                >
                    {/* Improved lighting setup */}
                    <ambientLight intensity={0.8} />
                    <directionalLight position={[5, 5, 5]} intensity={1.2} castShadow />
                    <directionalLight position={[-5, 5, -5]} intensity={0.6} />
                    <pointLight position={[0, 10, 0]} intensity={0.8} />
                    <hemisphereLight args={['#ffffff', '#60a5fa', 0.5]} />

                    {/* Debug: Add a red cube at origin to verify rendering */}
                    <mesh position={[0, 0, 0]}>
                        <boxGeometry args={[0.1, 0.1, 0.1]} />
                        <meshStandardMaterial color="red" />
                    </mesh>

                    <SimpleGLBModel url={url} autoRotate={autoRotate} />

                    <OrbitControls
                        enablePan={true}
                        enableZoom={true}
                        enableRotate={true}
                        minDistance={2}
                        maxDistance={10}
                    />
                </Canvas>
            </Suspense>

        </div>
    )
}