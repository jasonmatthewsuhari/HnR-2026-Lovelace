"use client"

import { useState, useEffect } from "react"
import { ChevronLeft, ChevronRight, Upload, Camera, X, Heart, Plus, Loader2, Check, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { GLBViewerWrapper } from "@/components/glb-viewer-wrapper"
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel"

interface BoyfriendOption {
  id: string
  name: string
  modelUrl: string
  description: string
  personality: string
}

interface BoyfriendSelectionStepProps {
  selectedBoyfriend?: BoyfriendOption
  onBoyfriendSelect: (boyfriend: BoyfriendOption | null) => void
  onImageUpload?: (file: File | null) => void
  onNext: () => void
  onBack: () => void
}

// Get backend URL for GLB models
const getBackendUrl = () => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  return API_BASE_URL
}

const BOYFRIEND_OPTIONS: BoyfriendOption[] = [
  {
    id: "alex",
    name: "Alex",
    modelUrl: `${getBackendUrl()}/3d/models/boyfriends/alex`,
    description: "The charming gentleman",
    personality: "Elegant, sophisticated, and always knows the right thing to say"
  },
  {
    id: "mike",
    name: "Mike",
    modelUrl: `${getBackendUrl()}/3d/models/boyfriends/mike`,
    description: "The athletic adventurer",
    personality: "Energetic, outgoing, and loves outdoor activities"
  },
  {
    id: "ryan",
    name: "Ryan",
    modelUrl: `${getBackendUrl()}/3d/models/boyfriends/ryan`,
    description: "The creative artist",
    personality: "Imaginative, artistic, and appreciates beauty in all forms"
  }
]

export function BoyfriendSelectionStep({
  selectedBoyfriend,
  onBoyfriendSelect,
  onImageUpload,
  onNext,
  onBack
}: BoyfriendSelectionStepProps) {
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)
  const [isCustomSelected, setIsCustomSelected] = useState(false)
  const [boyfriendOptions, setBoyfriendOptions] = useState<BoyfriendOption[]>(BOYFRIEND_OPTIONS)
  const [isLoadingBoyfriends, setIsLoadingBoyfriends] = useState(false)
  const [currentBoyfriendIndex, setCurrentBoyfriendIndex] = useState(0)
  const [modelLoading, setModelLoading] = useState(false)

  // Custom boyfriend generation states
  const [isGeneratingCustom, setIsGeneratingCustom] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [generationStage, setGenerationStage] = useState("")
  const [customJobId, setCustomJobId] = useState<string | null>(null)
  const [generationError, setGenerationError] = useState<string | null>(null)
  const [customBoyfriend, setCustomBoyfriend] = useState<BoyfriendOption | null>(null)

  const isViewingCustomOption = currentBoyfriendIndex >= boyfriendOptions.length
  const currentBoyfriend = isViewingCustomOption ? null : boyfriendOptions[currentBoyfriendIndex]

  // Handle model loading state
  useEffect(() => {
    if (currentBoyfriend) {
      setModelLoading(true)
      // Simulate model load time - in reality this would be from the GLB viewer
      const timer = setTimeout(() => setModelLoading(false), 1500)
      return () => clearTimeout(timer)
    }
  }, [currentBoyfriend?.id])

  // Poll custom boyfriend generation status
  useEffect(() => {
    if (!customJobId || !isGeneratingCustom) return

    const pollStatus = async () => {
      try {
        const response = await fetch(`${getBackendUrl()}/3d/status/${customJobId}`)
        if (!response.ok) throw new Error("Failed to fetch status")

        const data = await response.json()

        setGenerationProgress(data.progress || 0)
        setGenerationStage(data.stage || "Processing...")

        if (data.status === "completed" && data.model_url) {
          // Success! Create boyfriend object
          const newBoyfriend: BoyfriendOption = {
            id: data.boyfriend_id || customJobId,
            name: "Your Custom Boyfriend",
            modelUrl: `${getBackendUrl()}${data.model_url}`,
            description: "Your personalized virtual companion",
            personality: "Designed just for you"
          }

          setCustomBoyfriend(newBoyfriend)
          setIsGeneratingCustom(false)
          setGenerationError(null)

          // Auto-select the custom boyfriend
          onBoyfriendSelect(newBoyfriend)
          setIsCustomSelected(true)

        } else if (data.status === "failed") {
          setGenerationError(data.error || "Generation failed")
          setIsGeneratingCustom(false)
        }

      } catch (error) {
        console.error("Error polling status:", error)
        setGenerationError("Failed to check generation status")
        setIsGeneratingCustom(false)
      }
    }

    // Poll every 3 seconds
    const intervalId = setInterval(pollStatus, 3000)

    // Initial poll
    pollStatus()

    return () => clearInterval(intervalId)
  }, [customJobId, isGeneratingCustom, onBoyfriendSelect])

  // Handle custom boyfriend generation
  const handleGenerateCustomBoyfriend = async () => {
    if (!uploadedImage) return

    setIsGeneratingCustom(true)
    setGenerationError(null)
    setGenerationProgress(0)
    setGenerationStage("Uploading image...")

    try {
      const formData = new FormData()
      formData.append("image", uploadedImage)
      formData.append("boyfriend_name", "Custom Boyfriend")
      formData.append("async_mode", "true")

      const response = await fetch(`${getBackendUrl()}/3d/boyfriends/custom/generate`, {
        method: "POST",
        body: formData
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Generation failed")
      }

      const data = await response.json()

      if (data.success && data.job_id) {
        setCustomJobId(data.job_id)
        setGenerationStage(data.message || "Processing...")
        // Polling will start via useEffect
      } else {
        throw new Error("Invalid response from server")
      }

    } catch (error) {
      console.error("Error generating custom boyfriend:", error)
      setGenerationError(error instanceof Error ? error.message : "Failed to generate boyfriend")
      setIsGeneratingCustom(false)
    }
  }

  const handleReject = () => {
    if (currentBoyfriendIndex === boyfriendOptions.length - 1) {
      setCurrentBoyfriendIndex(boyfriendOptions.length)
    } else if (currentBoyfriendIndex < boyfriendOptions.length) {
      setCurrentBoyfriendIndex((prev) => prev + 1)
    }
  }

  const handleLike = () => {
    if (customBoyfriend) {
      // Custom boyfriend already selected
      onBoyfriendSelect(customBoyfriend)
      setIsCustomSelected(true)
    } else if (currentBoyfriend) {
      onBoyfriendSelect(currentBoyfriend)
      setUploadedImage(null)
    } else if (isViewingCustomOption && uploadedImage && !isGeneratingCustom) {
      // Trigger generation
      handleGenerateCustomBoyfriend()
    }
  }

  const renderMainContent = () => {
    if (isLoadingBoyfriends) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-white">
            <Loader2 className="animate-spin h-12 w-12 mx-auto mb-4" />
            <p className="text-lg">Loading your perfect match...</p>
          </div>
        </div>
      )
    }

    if (currentBoyfriend) {
      return (
        <div className="absolute inset-0">
          <GLBViewerWrapper
            url={currentBoyfriend.modelUrl}
            height="100%"
            width="100%"
            autoRotate={true}
            autoLoad={true}
            className="opacity-100"
          />
        </div>
      )
    }

    if (isViewingCustomOption) {
      // Show generation progress if generating
      if (isGeneratingCustom) {
        return (
          <div className="flex items-center justify-center h-full px-4">
            <div className="bg-white/95 backdrop-blur-sm rounded-3xl p-8 max-w-md mx-auto shadow-2xl">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Loader2 className="w-8 h-8 text-white animate-spin" />
                </div>
                <h3 className="text-2xl font-bold mb-2">Creating Your Boyfriend</h3>
                <p className="text-gray-600 text-sm">{generationStage}</p>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                <div
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${generationProgress}%` }}
                />
              </div>

              <p className="text-center text-sm text-gray-500">
                {generationProgress}% Complete • This may take 3-8 minutes
              </p>

              {/* Stages */}
              <div className="mt-6 space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Check className={`w-4 h-4 ${generationProgress > 10 ? 'text-green-500' : 'text-gray-300'}`} />
                  <span className={generationProgress > 10 ? 'text-gray-900' : 'text-gray-400'}>Image uploaded</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  {generationProgress > 50 ? <Check className="w-4 h-4 text-green-500" /> : <Loader2 className="w-4 h-4 animate-spin text-purple-500" />}
                  <span className={generationProgress > 50 ? 'text-gray-900' : 'text-gray-400'}>3D model generated</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  {generationProgress > 90 ? <Check className="w-4 h-4 text-green-500" /> : <Loader2 className="w-4 h-4 animate-spin text-purple-500" />}
                  <span className={generationProgress > 90 ? 'text-gray-900' : 'text-gray-400'}>Auto-rigged for animation</span>
                </div>
              </div>
            </div>
          </div>
        )
      }

      // Show custom boyfriend if generated
      if (customBoyfriend) {
        return (
          <div className="absolute inset-0">
            <GLBViewerWrapper
              url={customBoyfriend.modelUrl}
              height="100%"
              width="100%"
              autoRotate={true}
              autoLoad={true}
              className="opacity-100"
            />
            <div className="absolute top-24 left-1/2 -translate-x-1/2 z-20">
              <div className="bg-green-500 backdrop-blur-sm rounded-full px-6 py-3 flex items-center gap-2 shadow-xl">
                <Check className="w-5 h-5 text-white" />
                <span className="text-white font-medium">Custom boyfriend ready!</span>
              </div>
            </div>
          </div>
        )
      }

      // Show upload interface
      return (
        <div className="flex items-center justify-center h-full px-4">
          <div className="bg-white/95 backdrop-blur-sm rounded-3xl p-8 max-w-md mx-auto shadow-2xl">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Camera className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-2">Create Custom Boyfriend</h3>
              <p className="text-gray-600 text-sm">Upload a photo to generate your perfect companion using AI</p>
            </div>

            <label className="flex flex-col items-center justify-center w-full px-6 py-8 bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-dashed border-purple-300 rounded-2xl cursor-pointer hover:border-purple-400 transition-colors">
              <Upload className="w-12 h-12 text-purple-500 mb-3" />
              <span className="text-sm font-medium text-purple-600">Choose Image</span>
              <span className="text-xs text-gray-500 mt-1">JPG, PNG up to 10MB</span>
              <input
                type="file"
                className="hidden"
                accept="image/*"
                onChange={(e) => {
                  setUploadedImage(e.target.files?.[0] || null)
                  setGenerationError(null)
                }}
              />
            </label>

            {uploadedImage && (
              <>
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-xl">
                  <p className="text-sm text-green-700 font-medium">✓ {uploadedImage.name}</p>
                </div>

                <Button
                  onClick={handleGenerateCustomBoyfriend}
                  className="w-full mt-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                >
                  Generate 3D Model
                </Button>
              </>
            )}

            {generationError && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{generationError}</p>
              </div>
            )}

            <p className="text-xs text-gray-500 mt-4 text-center">
              🤖 Powered by Tripo3D AI • Takes 3-8 minutes
            </p>
          </div>
        </div>
      )
    }

    return null
  }

  return (
    <div className="h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 overflow-hidden flex flex-col relative">
      {/* Top Header - Minimal */}
      <div className="absolute top-0 left-0 right-0 z-30 bg-gradient-to-b from-black/50 to-transparent backdrop-blur-sm">
        <div className="p-6 text-center">
          <h1 className="text-3xl font-bold text-white drop-shadow-lg">Choose Your Virtual Boyfriend</h1>
          <p className="text-white/80 text-sm mt-2">Swipe through and find your perfect match</p>
        </div>
      </div>

      {/* 3D Model - Full Screen, no overlays */}
      <div className="flex-1 relative">
        {renderMainContent()}

        {/* Loading Indicator - Non-blocking */}
        {modelLoading && currentBoyfriend && (
          <div className="absolute top-24 right-6 z-20">
            <div className="bg-black/60 backdrop-blur-sm rounded-full px-4 py-2 flex items-center gap-2">
              <Loader2 className="animate-spin h-4 w-4 text-white" />
              <span className="text-white text-sm">Loading model...</span>
            </div>
          </div>
        )}
      </div>

      {/* Character Info - Bottom Left, No Overlap */}
      {(currentBoyfriend || customBoyfriend) && (
        <div className="absolute bottom-28 left-6 z-20 max-w-xs">
          <div className="bg-white/95 backdrop-blur-md rounded-2xl p-5 shadow-xl">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">
              {customBoyfriend?.name || currentBoyfriend?.name}
            </h2>
            <p className="text-sm text-gray-600 mb-2">
              {customBoyfriend?.description || currentBoyfriend?.description}
            </p>
            <p className="text-xs text-gray-500 italic">
              {customBoyfriend?.personality || currentBoyfriend?.personality}
            </p>
          </div>
        </div>
      )}

      {/* Action Buttons - Bottom Right */}
      <div className="absolute bottom-28 right-6 z-20 flex gap-4">
        <button
          onClick={handleReject}
          className="w-16 h-16 bg-gradient-to-br from-red-500 to-pink-500 rounded-full flex items-center justify-center shadow-xl hover:scale-110 transition-transform active:scale-95"
        >
          <X className="w-8 h-8 text-white" />
        </button>
        <button
          onClick={handleLike}
          className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center shadow-xl hover:scale-110 transition-transform active:scale-95"
        >
          <Heart className="w-8 h-8 text-white" />
        </button>
      </div>

      {/* Progress Indicator - Bottom Center */}
      {!isViewingCustomOption && (
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex gap-2">
          {boyfriendOptions.map((_, idx) => (
            <div
              key={idx}
              className={`w-2 h-2 rounded-full transition-all ${idx === currentBoyfriendIndex
                ? 'bg-white w-8'
                : 'bg-white/40'
                }`}
            />
          ))}
          <div className={`w-2 h-2 rounded-full ${isViewingCustomOption ? 'bg-white w-8' : 'bg-white/40'
            }`} />
        </div>
      )}

      {/* Navigation - Bottom Right Corner */}
      <div className="absolute bottom-6 right-6 z-20 flex gap-3">
        <Button
          variant="secondary"
          onClick={onBack}
          className="backdrop-blur-sm bg-white/90 hover:bg-white"
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Back
        </Button>
        <Button
          onClick={onNext}
          disabled={!selectedBoyfriend && !isCustomSelected}
          className="bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 shadow-lg"
        >
          Continue
          <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
    </div>
  )
}