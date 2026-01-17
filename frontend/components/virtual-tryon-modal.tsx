"use client"

import { useState, useRef, useEffect } from "react"
import { X, Camera, Upload, Sparkles, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import type { ClothingItem } from "@/components/app/add-clothing-modal"

interface VirtualTryOnModalProps {
  isOpen: boolean
  onClose: () => void
}

export function VirtualTryOnModal({ isOpen, onClose }: VirtualTryOnModalProps) {
  const [step, setStep] = useState<"select-person" | "camera" | "select-clothing" | "processing" | "result">("select-person")
  const [personImage, setPersonImage] = useState<string | null>(null)
  const [clothingImage, setClothingImage] = useState<string | null>(null)
  const [resultImage, setResultImage] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [clothingSource, setClothingSource] = useState<"upload" | "wardrobe" | null>(null)
  const [wardrobeItems, setWardrobeItems] = useState<ClothingItem[]>([])

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const personFileInputRef = useRef<HTMLInputElement>(null)
  const clothingFileInputRef = useRef<HTMLInputElement>(null)

  // Load wardrobe items
  useEffect(() => {
    if (isOpen) {
      const saved = localStorage.getItem("lovelace-clothing")
      if (saved) {
        setWardrobeItems(JSON.parse(saved))
      }
    }
  }, [isOpen])

  // Cleanup camera on unmount or close
  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [])

  // Initialize camera for person image
  const startCamera = async () => {
    try {
      console.log("Requesting camera access...")
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user"
        },
        audio: false
      })
      console.log("Camera access granted!")
      setStream(mediaStream)
      setStep("camera") // Move to camera page

      // Wait a bit for the video element to be rendered
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream
          videoRef.current.play().catch(e => console.error("Error playing video:", e))
        }
      }, 100)
    } catch (error) {
      console.error("Error accessing camera:", error)
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          alert("Camera permission denied. Please allow camera access in your browser settings.")
        } else if (error.name === 'NotFoundError') {
          alert("No camera found on this device.")
        } else {
          alert(`Could not access camera: ${error.message}`)
        }
      }
    }
  }

  const stopCamera = () => {
    if (stream) {
      console.log("Stopping camera...")
      stream.getTracks().forEach(track => {
        track.stop()
        console.log("Track stopped:", track.kind)
      })
      setStream(null)
      if (videoRef.current) {
        videoRef.current.srcObject = null
      }
    }
    setStep("select-person") // Go back to selection page
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current

      // Make sure video has dimensions
      if (video.videoWidth === 0 || video.videoHeight === 0) {
        alert("Video not ready. Please wait a moment and try again.")
        return
      }

      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext("2d")
      if (ctx) {
        ctx.drawImage(video, 0, 0)
        const imageData = canvas.toDataURL("image/jpeg", 0.9)
        setPersonImage(imageData)
        stopCamera()
        setStep("select-clothing")
      }
    }
  }

  const handlePersonUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setPersonImage(reader.result as string)
        setStep("select-clothing")
      }
      reader.readAsDataURL(file)
    }
  }

  const handleClothingUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setClothingImage(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const selectClothingFromWardrobe = (item: ClothingItem) => {
    // Use the first image from the clothing item
    setClothingImage(item.images[0])
    setClothingSource("wardrobe")
  }

  const processVirtualTryOn = async () => {
    if (!personImage || !clothingImage) return

    setIsProcessing(true)
    setStep("processing")

    try {
      // Convert base64 to blob if needed
      const personBlob = await fetch(personImage).then(r => r.blob())
      const clothingBlob = await fetch(clothingImage).then(r => r.blob())

      const formData = new FormData()
      formData.append("person_image", personBlob, "person.jpg")
      formData.append("clothing_image", clothingBlob, "clothing.jpg")

      const response = await fetch("http://localhost:8000/api/virtual-tryon", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Virtual try-on failed")
      }

      const data = await response.json()
      setResultImage(data.image) // Backend returns base64 data URL in 'image' field
      setStep("result")
    } catch (error) {
      console.error("Error processing virtual try-on:", error)
      alert("Virtual try-on failed. Please try again.")
      setStep("select-clothing")
    } finally {
      setIsProcessing(false)
    }
  }

  const reset = () => {
    setStep("select-person")
    setPersonImage(null)
    setClothingImage(null)
    setResultImage(null)
    setClothingSource(null)
    stopCamera()
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="relative h-[90vh] w-full max-w-6xl overflow-hidden rounded-3xl bg-gradient-to-br from-pink-100 via-purple-50 to-pink-50 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-pink-200/50 bg-white/90 px-6 py-4 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-pink-300/80 via-purple-200/70 to-pink-200/60">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">Virtual Try-On</h2>
              <p className="text-sm text-gray-600">See how clothes look on you instantly</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClose}
            className="h-10 w-10 rounded-full hover:bg-pink-50"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="h-[calc(100%-80px)] overflow-y-auto p-6">
          {/* Step 1: Select Person Image */}
          {step === "select-person" && (
            <div className="flex h-full flex-col items-center justify-center">
              <h3 className="mb-3 text-2xl font-bold text-gray-800">Step 1: Your Photo</h3>
              <p className="mb-8 text-center text-gray-600">
                Choose how you'd like to add your photo
              </p>

              {/* Fitted Container with Two Options */}
              <div className="w-full max-w-md space-y-0">
                {/* Camera Option */}
                <button
                  onClick={startCamera}
                  className="group w-full rounded-t-3xl bg-gray-100 p-8 transition-all hover:bg-gray-150 active:scale-[0.98]"
                >
                  <div className="flex flex-col items-center gap-3">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-pink-300/80 via-purple-200/70 to-pink-200/60 transition-all group-hover:scale-110">
                      <Camera className="h-8 w-8 text-white" />
                    </div>
                    <span className="text-lg font-semibold text-gray-800">Snap a pic!</span>
                  </div>
                </button>

                {/* OR Divider */}
                <div className="relative py-4">
                  <div className="absolute inset-0 flex items-center px-8">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center">
                    <span className="bg-gradient-to-br from-pink-100 via-purple-50 to-pink-50 px-4 text-sm font-medium text-gray-500">
                      OR
                    </span>
                  </div>
                </div>

                {/* Gallery Option */}
                <button
                  onClick={() => personFileInputRef.current?.click()}
                  className="group w-full rounded-b-3xl bg-gray-100 p-8 transition-all hover:bg-gray-150 active:scale-[0.98]"
                >
                  <div className="flex flex-col items-center gap-3">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-pink-300/80 via-purple-200/70 to-pink-200/60 transition-all group-hover:scale-110">
                      <Upload className="h-8 w-8 text-white" />
                    </div>
                    <span className="text-lg font-semibold text-gray-800">Select from Gallery</span>
                  </div>
                </button>
              </div>

              <input
                ref={personFileInputRef}
                type="file"
                accept="image/*"
                onChange={handlePersonUpload}
                className="hidden"
              />
              <canvas ref={canvasRef} className="hidden" />
            </div>
          )}

          {/* Camera Page */}
          {step === "camera" && (
            <div className="flex h-full flex-col items-center justify-center">
              <h3 className="mb-3 text-2xl font-bold text-gray-800">Smile! 📸</h3>
              <p className="mb-6 text-center text-gray-600">
                Position yourself in the frame
              </p>

              <div className="w-full max-w-2xl space-y-4">
                <div className="relative overflow-hidden rounded-3xl bg-black shadow-2xl">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full"
                    style={{ transform: 'scaleX(-1)' }}
                  />
                </div>

                <div className="flex gap-3">
                  <Button
                    onClick={stopCamera}
                    variant="outline"
                    className="flex-1 rounded-full border-2 border-gray-300 bg-white hover:bg-gray-50"
                    size="lg"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={capturePhoto}
                    className="flex-1 rounded-full bg-gradient-to-r from-pink-300/90 via-purple-200/80 to-pink-200/70 text-gray-800 hover:from-pink-300 hover:via-purple-200 hover:to-pink-200"
                    size="lg"
                  >
                    <Camera className="mr-2 h-5 w-5" />
                    Capture Photo
                  </Button>
                </div>
              </div>

              <canvas ref={canvasRef} className="hidden" />
            </div>
          )}

          {/* Step 2: Select Clothing */}
          {step === "select-clothing" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold text-gray-800">Step 2: Choose Clothing</h3>
                  <p className="text-gray-600">Select from wardrobe or upload new</p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setStep("select-person")}
                  className="rounded-full border-2 border-pink-200 hover:bg-pink-50"
                >
                  Change Photo
                </Button>
              </div>

              <div className="grid gap-6 md:grid-cols-2">
                {/* Person Image Preview */}
                <div className="space-y-2">
                  <Label className="text-gray-700">Your Photo</Label>
                  <div className="overflow-hidden rounded-2xl border-2 border-pink-200 shadow-lg">
                    {personImage && (
                      <img src={personImage} alt="Person" className="h-64 w-full object-cover" />
                    )}
                  </div>
                </div>

                {/* Clothing Selection */}
                <div className="space-y-4">
                  <Label className="text-gray-700">Clothing Item</Label>

                  {!clothingImage ? (
                    <div className="space-y-4">
                      {/* Upload Clothing */}
                      <button
                        onClick={() => clothingFileInputRef.current?.click()}
                        className="group flex w-full flex-col items-center justify-center gap-4 rounded-2xl bg-gray-100 p-6 transition-all hover:bg-gray-150 active:scale-[0.98]"
                      >
                        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-pink-300/80 via-purple-200/70 to-pink-200/60 transition-all group-hover:scale-110">
                          <Upload className="h-6 w-6 text-white" />
                        </div>
                        <span className="font-semibold text-gray-800">Upload Clothing Photo</span>
                      </button>

                      <input
                        ref={clothingFileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleClothingUpload}
                        className="hidden"
                      />

                      {/* Or Select from Wardrobe */}
                      {wardrobeItems.length > 0 && (
                        <>
                          <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                              <span className="w-full border-t border-gray-300" />
                            </div>
                            <div className="relative flex justify-center">
                              <span className="bg-gradient-to-br from-pink-100 via-purple-50 to-pink-50 px-4 text-sm font-medium text-gray-500">
                                Or select from wardrobe
                              </span>
                            </div>
                          </div>

                          <div className="max-h-64 space-y-2 overflow-y-auto rounded-2xl border-2 border-pink-200/50 bg-white/50 p-3">
                            <div className="grid grid-cols-3 gap-2">
                              {wardrobeItems.map((item) => (
                                <button
                                  key={item.id}
                                  onClick={() => selectClothingFromWardrobe(item)}
                                  className="group relative overflow-hidden rounded-xl border-2 border-transparent transition-all hover:border-pink-300 hover:shadow-lg"
                                >
                                  <img
                                    src={item.images[0]}
                                    alt={item.name}
                                    className="aspect-square w-full object-cover"
                                  />
                                  <div className="absolute inset-0 bg-black/0 transition-all group-hover:bg-black/10" />
                                </button>
                              ))}
                            </div>
                          </div>
                        </>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="overflow-hidden rounded-2xl border-2 border-pink-200 shadow-lg">
                        <img src={clothingImage} alt="Clothing" className="h-64 w-full object-cover" />
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          onClick={() => setClothingImage(null)}
                          className="flex-1 rounded-full border-2 border-gray-300"
                        >
                          Change Clothing
                        </Button>
                        <Button
                          onClick={processVirtualTryOn}
                          className="flex-1 rounded-full bg-gradient-to-r from-pink-300/90 via-purple-200/80 to-pink-200/70 text-gray-800 hover:from-pink-300 hover:via-purple-200 hover:to-pink-200"
                        >
                          <Sparkles className="mr-2 h-4 w-4" />
                          Try It On!
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Processing */}
          {step === "processing" && (
            <div className="flex h-full flex-col items-center justify-center">
              <Loader2 className="mb-6 h-16 w-16 animate-spin text-pink-300" />
              <h3 className="mb-2 text-2xl font-bold text-gray-800">Creating Your Virtual Try-On...</h3>
              <p className="text-center text-gray-600">
                This usually takes 10-30 seconds ✨
              </p>
            </div>
          )}

          {/* Step 4: Result */}
          {step === "result" && resultImage && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold text-gray-800">Your Virtual Try-On Result! 🎉</h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={reset}
                    className="rounded-full border-2 border-pink-200 hover:bg-pink-50"
                  >
                    Try Another
                  </Button>
                  <Button
                    className="rounded-full bg-gradient-to-r from-pink-300/90 via-purple-200/80 to-pink-200/70 text-gray-800 hover:from-pink-300 hover:via-purple-200 hover:to-pink-200"
                    onClick={() => {
                      const a = document.createElement("a")
                      a.href = resultImage
                      a.download = "virtual-tryon-result.png"
                      a.click()
                    }}
                  >
                    Download Result
                  </Button>
                </div>
              </div>

              <div className="grid gap-6 md:grid-cols-3">
                <div className="space-y-2">
                  <Label className="text-gray-700">Original Photo</Label>
                  <div className="overflow-hidden rounded-2xl border-2 border-pink-200/50">
                    {personImage && (
                      <img src={personImage} alt="Original" className="w-full object-cover" />
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-gray-700">Clothing Item</Label>
                  <div className="overflow-hidden rounded-2xl border-2 border-pink-200/50">
                    {clothingImage && (
                      <img src={clothingImage} alt="Clothing" className="w-full object-cover" />
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-gray-700">✨ Virtual Try-On Result</Label>
                  <div className="overflow-hidden rounded-2xl border-4 border-pink-300 shadow-2xl">
                    <img src={resultImage} alt="Result" className="w-full object-cover" />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
