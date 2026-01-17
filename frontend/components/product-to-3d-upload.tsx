/**
 * Product-to-3D Upload Component
 * 
 * Example React component for uploading product images and displaying 3D models
 * Integrate this into your Lovelace app's wardrobe or product discovery pages
 */

'use client'

import { useState, useRef } from 'react'
import { Upload, Loader2, Check, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_3D_API_URL || 'http://localhost:8000'

type QualityLevel = 'preview' | 'standard' | 'high' | 'premium'

interface GenerationResult {
  success: boolean
  job_id: string
  message: string
  model_url?: string
  generation_time?: number
  provider?: string
  format?: string
  error?: string
}

export function ProductTo3DUpload() {
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [quality, setQuality] = useState<QualityLevel>('standard')
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Show image preview
    const reader = new FileReader()
    reader.onload = (e) => setPreviewUrl(e.target?.result as string)
    reader.readAsDataURL(file)

    // Upload and generate 3D
    await generate3DModel(file)
  }

  const generate3DModel = async (file: File) => {
    setUploading(true)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('quality', quality)
      formData.append('output_format', 'glb')
      formData.append('remove_background', 'true')
      formData.append('async_mode', 'false') // Sync for demo, use async in production

      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: GenerationResult = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Generation failed:', error)
      setResult({
        success: false,
        job_id: '',
        message: 'Failed to generate 3D model',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      // Trigger file input
      if (fileInputRef.current) {
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        fileInputRef.current.files = dataTransfer.files
        fileInputRef.current.dispatchEvent(new Event('change', { bubbles: true }))
      }
    }
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Convert Product Image to 3D</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Quality Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Quality Level</label>
            <Select value={quality} onValueChange={(v) => setQuality(v as QualityLevel)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="preview">Preview (~5s)</SelectItem>
                <SelectItem value="standard">Standard (~30s)</SelectItem>
                <SelectItem value="high">High (~2min)</SelectItem>
                <SelectItem value="premium">Premium (~5min)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Upload Area */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-primary transition-colors"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />

            {previewUrl ? (
              <div className="space-y-4">
                <img src={previewUrl} alt="Preview" className="max-h-48 mx-auto rounded" />
                <p className="text-sm text-muted-foreground">
                  Click or drag to replace image
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">Click to upload or drag and drop</p>
                  <p className="text-xs text-muted-foreground">PNG, JPG up to 10MB</p>
                </div>
              </div>
            )}
          </div>

          {/* Status */}
          {uploading && (
            <div className="flex items-center justify-center space-x-2 text-primary">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Generating 3D model...</span>
            </div>
          )}

          {result && !uploading && (
            <div className={`p-4 rounded-lg ${result.success ? 'bg-green-50 dark:bg-green-950' : 'bg-red-50 dark:bg-red-950'}`}>
              <div className="flex items-start space-x-2">
                {result.success ? (
                  <Check className="h-5 w-5 text-green-600 mt-0.5" />
                ) : (
                  <X className="h-5 w-5 text-red-600 mt-0.5" />
                )}
                <div className="flex-1">
                  <p className="font-medium">{result.message}</p>
                  {result.success && (
                    <div className="mt-2 text-sm space-y-1">
                      <p>Generated in {result.generation_time?.toFixed(2)}s</p>
                      <p>Provider: {result.provider}</p>
                      <p>Format: {result.format?.toUpperCase()}</p>
                    </div>
                  )}
                  {result.error && (
                    <p className="mt-2 text-sm text-red-600">{result.error}</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 3D Model Viewer */}
      {result?.success && result.model_url && (
        <Card>
          <CardHeader>
            <CardTitle>3D Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
              {/* Using model-viewer web component (add script to layout.tsx) */}
              {/* Or use Three.js, React Three Fiber, etc. */}
              <model-viewer
                src={`${API_BASE_URL}${result.model_url}`}
                alt="Generated 3D model"
                auto-rotate
                camera-controls
                style={{ width: '100%', height: '100%' }}
              />
            </div>

            <div className="mt-4 flex space-x-2">
              <Button
                onClick={() => window.open(`${API_BASE_URL}${result.model_url}`, '_blank')}
                variant="outline"
              >
                Download Model
              </Button>
              <Button>
                Add to Wardrobe
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Add to layout.tsx or _app.tsx:
// <Script src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js" type="module" />

// TypeScript declaration for model-viewer (add to global.d.ts)
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'model-viewer': any
    }
  }
}
