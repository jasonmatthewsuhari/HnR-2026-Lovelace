"use client"

import { useState, useRef, useEffect } from "react"
import { Camera, RotateCw, X, Download, Sparkles, RefreshCw, Plus, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface PhotoboothProps {
  isOpen: boolean
  onClose: () => void
  avatarUrl?: string
}

interface CapturedPhoto {
  id: string
  url: string
  backgroundName: string
  backgroundUrl: string
}

export function PhotoboothModal({ isOpen, onClose, avatarUrl }: PhotoboothProps) {
  const [step, setStep] = useState<"describe" | "capture" | "results">("describe")
  const [currentBackground, setCurrentBackground] = useState<{ id: string; url: string; name: string } | null>(null)
  const [backgroundDescription, setBackgroundDescription] = useState("")
  const [poseDescription, setPoseDescription] = useState("") // New state for boyfriend's pose
  const [isGenerating, setIsGenerating] = useState(false)
  const [savedBackgrounds, setSavedBackgrounds] = useState<{ id: string; url: string; name: string }[]>([])
  const [countdown, setCountdown] = useState<number | null>(null)
  const [capturedPhotos, setCapturedPhotos] = useState<CapturedPhoto[]>([])
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [showFlash, setShowFlash] = useState(false) // New state for camera flash
  const [isCameraReady, setIsCameraReady] = useState(false) // New state for camera ready check

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const previewCanvasRef = useRef<HTMLCanvasElement>(null)

  // Load saved backgrounds on mount
  useEffect(() => {
    fetchSavedBackgrounds()
  }, [])

  // Initialize camera
  useEffect(() => {
    if (isOpen && step === "capture") {
      startCamera()
    }
    return () => {
      stopCamera()
    }
  }, [isOpen, step])

  const fetchSavedBackgrounds = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/photobooth/saved-backgrounds")
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setSavedBackgrounds(data.backgrounds)
        }
      }
    } catch (error) {
      console.error("Error fetching saved backgrounds:", error)
    }
  }

  // Live background removal preview
  useEffect(() => {
    if (!videoRef.current || !previewCanvasRef.current || step !== "capture") return

    const video = videoRef.current
    const canvas = previewCanvasRef.current
    let animationId: number

    const renderPreview = () => {
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        const ctx = canvas.getContext("2d", { willReadFrequently: true })
        if (ctx) {
          // Sync canvas size with video
          if (canvas.width !== video.videoWidth) canvas.width = video.videoWidth
          if (canvas.height !== video.videoHeight) canvas.height = video.videoHeight

          // Draw video frame
          ctx.drawImage(video, 0, 0)

          // Apply background removal effect (visual only)
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
          const data = imageData.data

          // Advanced background separation (Holographic Effect)
          // We'll use a slightly smarter approach: 
          // 1. Calculate the background color by sampling the corners
          const sampleSize = 10;
          let bgR = 0, bgG = 0, bgB = 0;

          // Sample 4 corners
          const corners = [
            [0, 0], [canvas.width - 1, 0],
            [0, canvas.height - 1], [canvas.width - 1, canvas.height - 1]
          ];

          corners.forEach(([x, y]) => {
            const idx = (y * canvas.width + x) * 4;
            bgR += data[idx];
            bgG += data[idx + 1];
            bgB += data[idx + 2];
          });
          bgR /= 4; bgG /= 4; bgB /= 4;

          // Performance optimization: only process every 2nd pixel if we're slow?
          // For now, let's just make the loop as tight as possible.
          for (let i = 0; i < data.length; i += 4) {
            const r = data[i]
            const g = data[i + 1]
            const b = data[i + 2]

            // Fast color distance (Manhattan distance for speed)
            const dist = Math.abs(r - bgR) + Math.abs(g - bgG) + Math.abs(b - bgB);

            // If it's too close to background color or extremely bright/dark
            if (dist < 80 || (r + g + b) > 740 || (r + g + b) < 40) {
              data[i + 3] = 45; // Transparentish
            } else {
              // User area: keep it visible but add holographic tint
              data[i] = Math.min(255, r + 15);
              data[i + 2] = Math.min(255, b + 30);
              data[i + 3] = 255;
            }
          }
          ctx.putImageData(imageData, 0, 0)

          // Add a subtle scanline effect layer
          ctx.fillStyle = "rgba(0, 255, 255, 0.03)";
          for (let y = 0; y < canvas.height; y += 4) {
            ctx.fillRect(0, y, canvas.width, 1);
          }

          // Ensure video is playing
          if (video.paused) video.play().catch(() => { })
        }
      }
      animationId = requestAnimationFrame(renderPreview)
    }

    renderPreview()

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
    }
  }, [step])

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: "user" }
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (error) {
      console.error("Error accessing camera:", error)
      alert("Could not access camera. Please check permissions.")
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }

  const generateBackground = async () => {
    if (!backgroundDescription.trim()) {
      alert("Please describe the background you want!")
      return
    }

    setIsGenerating(true)
    try {
      const avatarBlob = await fetch(avatarUrl || "/placeholder-user.jpg").then(r => r.blob())
      const formData = new FormData()
      formData.append("avatar", avatarBlob, "avatar.jpg")
      formData.append("description", backgroundDescription)
      formData.append("pose", poseDescription) // Send pose description

      const response = await fetch("http://localhost:8000/api/photobooth/generate-background", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Failed to generate background")
      }

      const data = await response.json()

      if (data.success && data.background) {
        const newBg = {
          id: data.background.id,
          url: `http://localhost:8000${data.background.url}`,
          name: data.background.name
        }
        setCurrentBackground(newBg)
        setStep("capture")

        // Add to "recent" if not already there
        setSavedBackgrounds(prev => {
          if (prev.find(bg => bg.id === newBg.id)) return prev
          return [newBg, ...prev]
        })
      } else {
        throw new Error("Invalid response from server")
      }
    } catch (error) {
      console.error("Error generating background:", error)
      alert("Failed to generate background. Make sure the backend is running on http://localhost:8000")
    } finally {
      setIsGenerating(false)
    }
  }

  const regenerateCurrentBackground = async () => {
    if (!currentBackground) return

    setIsGenerating(true)
    try {
      const avatarBlob = await fetch(avatarUrl || "/placeholder-user.jpg").then(r => r.blob())
      const formData = new FormData()
      formData.append("avatar", avatarBlob, "avatar.jpg")
      formData.append("description", backgroundDescription)

      const response = await fetch("http://localhost:8000/api/photobooth/generate-background", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Failed to regenerate background")
      }

      const data = await response.json()

      if (data.success && data.background) {
        setCurrentBackground({
          id: data.background.id,
          url: `http://localhost:8000${data.background.url}`,
          name: data.background.name,
        })
      }
    } catch (error) {
      console.error("Error regenerating background:", error)
      alert("Failed to regenerate background")
    } finally {
      setIsGenerating(false)
    }
  }

  const startCountdown = () => {
    setCountdown(5)
    const interval = setInterval(() => {
      setCountdown(prev => {
        if (prev === null || prev <= 1) {
          clearInterval(interval)
          // Camera Flash Effect
          setTimeout(() => {
            setShowFlash(true)
            setTimeout(() => setShowFlash(false), 150)
          }, 0)
          capturePhoto()
          return null
        }
        return prev - 1
      })
    }, 1000)
  }

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current || !currentBackground) return

    setIsProcessing(true)
    const canvas = canvasRef.current
    const video = videoRef.current

    // Ensure dimensions are valid
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      console.error("Video dimensions are 0")
      setIsProcessing(false)
      return
    }

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext("2d")
    if (ctx) {
      // Draw video frame to canvas
      ctx.drawImage(video, 0, 0)

      // Get image as blob
      canvas.toBlob(async (blob) => {
        if (!blob) return

        try {
          // Remove background using backend
          const formData = new FormData()
          formData.append("image", blob, "capture.png")

          const bgRemoveResponse = await fetch("http://localhost:8000/api/photobooth/remove-background", {
            method: "POST",
            body: formData,
          })

          if (!bgRemoveResponse.ok) {
            throw new Error("Failed to remove background")
          }

          const bgRemoveData = await bgRemoveResponse.json()
          const userImageNoBg = bgRemoveData.image

          // Create composite with background
          const compositeFormData = new FormData()

          // Convert base64 to blob
          const base64Response = await fetch(userImageNoBg)
          const userBlob = await base64Response.blob()
          compositeFormData.append("user_image", userBlob, "user.png")
          compositeFormData.append("background_url", currentBackground.url)

          const compositeResponse = await fetch("http://localhost:8000/api/photobooth/composite", {
            method: "POST",
            body: compositeFormData,
          })

          if (!compositeResponse.ok) {
            throw new Error("Failed to create composite")
          }

          const compositeData = await compositeResponse.json()
          const finalPhoto = compositeData.image

          // Save the photo
          const newPhoto: CapturedPhoto = {
            id: `photo_${Date.now()}`,
            url: finalPhoto,
            backgroundName: currentBackground.name,
            backgroundUrl: currentBackground.url
          }

          setCapturedPhotos(prev => [...prev, newPhoto])
          setStep("results")
          stopCamera()
        } catch (error) {
          console.error("Error processing photo:", error)
          alert("Failed to process photo. Try again or check backend connection.")
        } finally {
          setIsProcessing(false)
        }
      }, "image/png")
    }
  }

  const downloadPhoto = (photoUrl: string, photoName: string) => {
    const link = document.createElement("a")
    link.href = photoUrl
    link.download = `photobooth_${photoName.toLowerCase().replace(/\s/g, "_")}.png`
    link.click()
  }

  const takeAnother = () => {
    setStep("describe")
    setCurrentBackground(null)
    setBackgroundDescription("")
    setCountdown(null)
  }

  const reset = () => {
    setStep("describe")
    setCurrentBackground(null)
    setBackgroundDescription("")
    setCapturedPhotos([])
    setCountdown(null)
  }

  if (!isOpen) return null

  // Ensure camera visibility even if background removal is acting up
  const previewFilter = isProcessing
    ? "blur(12px) grayscale(1)"
    : "drop-shadow(0 0 20px rgba(0, 150, 255, 0.4)) contrast(1.1) brightness(1.1)";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="relative h-[90vh] w-[95vw] max-w-6xl overflow-hidden rounded-3xl bg-background shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/50 bg-background/95 px-6 py-4 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-purple-300/80 via-pink-200/70 to-blue-200/60">
              <Camera className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold">AI Photobooth</h2>
              <p className="text-sm text-muted-foreground">
                {step === "describe" && "Describe your perfect background"}
                {step === "capture" && "Get ready for your photo!"}
                {step === "results" && `${capturedPhotos.length} photo${capturedPhotos.length !== 1 ? 's' : ''} taken`}
              </p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content Area */}
        <div className="h-[calc(90vh-80px)] overflow-y-auto p-6">
          {/* Describe Step */}
          {step === "describe" && (
            <div className="flex h-full flex-col items-center justify-center gap-6">
              <div className="w-full max-w-2xl space-y-8">
                <div className="text-center space-y-2">
                  <h3 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">
                    Create Your Scene
                  </h3>
                  <p className="text-muted-foreground">
                    Where should your couple's photo take place?
                  </p>
                </div>

                <div className="space-y-6">
                  <div className="space-y-3">
                    <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      1. The Location
                    </label>
                    <Textarea
                      placeholder="e.g., A rainy street in Tokyo, a cozy bookstore, a moonlit balcony..."
                      value={backgroundDescription}
                      onChange={(e) => setBackgroundDescription(e.target.value)}
                      className="h-24 text-lg bg-black/5 border-white/10 focus-visible:ring-indigo-500"
                    />
                  </div>

                  <div className="space-y-3">
                    <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      2. His Pose
                    </label>
                    <Textarea
                      placeholder="e.g., Leaning against a wall, holding out a hand, looking at me lovingly..."
                      value={poseDescription}
                      onChange={(e) => setPoseDescription(e.target.value)}
                      className="h-20 text-lg bg-black/5 border-white/10 focus-visible:ring-indigo-500"
                    />
                  </div>

                  <Button
                    onClick={generateBackground}
                    disabled={isGenerating || !backgroundDescription.trim()}
                    className="w-full h-14 text-lg bg-indigo-600 hover:bg-indigo-500 shadow-xl shadow-indigo-500/20"
                  >
                    {isGenerating ? (
                      <>
                        <RefreshCw className="mr-3 h-6 w-6 animate-spin" />
                        AI is painting your world...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-3 h-6 w-6" />
                        Enter Photobooth
                      </>
                    )}
                  </Button>

                  {savedBackgrounds.length > 0 && (
                    <div className="space-y-4 pt-4 border-t border-border/50">
                      <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                        Quick Reuse
                      </label>
                      <div className="grid grid-cols-3 gap-3">
                        {savedBackgrounds.slice(0, 3).map((bg) => (
                          <button
                            key={bg.id}
                            onClick={() => {
                              setCurrentBackground(bg)
                              setStep("capture")
                            }}
                            className="group relative aspect-[16/9] overflow-hidden rounded-xl border border-border hover:border-indigo-500 transition-all"
                          >
                            <img src={bg.url} alt={bg.name} className="h-full w-full object-cover group-hover:scale-110 transition-transform duration-500" />
                            <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                              <Check className="text-white h-6 w-6" />
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Capture Step */}
          {step === "capture" && currentBackground && (
            <div className="flex h-full flex-col items-center justify-center gap-6">
              <div className="relative">
                {/* Main Camera Viewfinder */}
                <div className="relative h-[500px] w-[700px] overflow-hidden rounded-2xl bg-black shadow-2xl border-4 border-white/5">
                  {/* Viewfinder Overlay Layers */}
                  <div className="absolute inset-0 pointer-events-none z-20">
                    <div className="absolute top-8 left-8 w-12 h-12 border-t-2 border-l-2 border-white/50 rounded-tl-sm" />
                    <div className="absolute top-8 right-8 w-12 h-12 border-t-2 border-r-2 border-white/50 rounded-tr-sm" />
                    <div className="absolute bottom-8 left-8 w-12 h-12 border-b-2 border-l-2 border-white/50 rounded-bl-sm" />
                    <div className="absolute bottom-8 right-8 w-12 h-12 border-b-2 border-r-2 border-white/50 rounded-br-sm" />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-30">
                      <div className="w-10 h-[2px] bg-white" />
                      <div className="h-10 w-[2px] bg-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                    </div>
                    {/* Recording Dot */}
                    <div className="absolute top-8 left-1/2 -translate-x-1/2 flex items-center gap-2 px-3 py-1 bg-black/50 backdrop-blur-md rounded-full text-[10px] font-mono text-white tracking-tighter uppercase border border-white/10">
                      <div className="h-2 w-2 bg-red-500 rounded-full animate-pulse" />
                      LIVE • 4K
                    </div>
                  </div>

                  {/* Flash Effect Layer */}
                  <div className={`absolute inset-0 bg-white z-[100] transition-opacity duration-75 pointer-events-none ${showFlash ? "opacity-100" : "opacity-0"}`} />

                  {/* The Background Scene */}
                  <img src={currentBackground.url} alt="Scene" className="absolute inset-0 h-full w-full object-cover" />

                  {/* Hidden Video Source */}
                  <video ref={videoRef} autoPlay playsInline muted onLoadedMetadata={() => setIsCameraReady(true)} className="hidden" />

                  {/* Live Render Canvas (User cutout on top of background) */}
                  <canvas
                    ref={previewCanvasRef}
                    className="absolute inset-0 h-full w-full object-cover pointer-events-none z-[25]"
                    style={{ filter: previewFilter }}
                  />

                  {/* Countdown View */}
                  {countdown !== null && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-[2px] z-30">
                      <div className="relative">
                        <div className="absolute inset-0 animate-ping rounded-full border-8 border-white/20" />
                        <span className="relative text-9xl font-black text-white drop-shadow-[0_0_50px_rgba(255,255,255,0.8)]">
                          {countdown}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Processing / Developing Effect */}
                  {isProcessing && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-black/60 backdrop-blur-xl z-50">
                      <div className="h-24 w-24 relative">
                        <div className="absolute inset-0 rounded-full border-4 border-white/10" />
                        <div className="absolute inset-0 rounded-full border-t-4 border-white animate-spin" />
                      </div>
                      <p className="text-xl font-bold tracking-widest text-white uppercase italic">Developing...</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Camera Controls Area */}
              <div className="w-full max-w-2xl px-4 space-y-4">
                <div className="flex items-end justify-between">
                  <div className="space-y-1">
                    <h4 className="text-xl font-bold tracking-tight">{currentBackground.name}</h4>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-mono">
                      Image {capturedPhotos.length + 1} of Session
                    </p>
                  </div>
                  <Button variant="outline" size="sm" onClick={regenerateCurrentBackground} disabled={isGenerating || isProcessing || countdown !== null} className="rounded-full border-white/10">
                    <RotateCw className={`h-4 w-4 mr-2 ${isGenerating ? "animate-spin" : ""}`} />
                    New Scene
                  </Button>
                </div>

                <Button
                  size="lg"
                  onClick={startCountdown}
                  disabled={!isCameraReady || isProcessing || countdown !== null}
                  className="w-full h-20 rounded-2xl text-2xl font-black bg-white text-black hover:bg-neutral-200 shadow-2xl transition-all active:scale-95 group overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-black/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                  <Camera className="mr-3 h-8 w-8" />
                  Capture Moment
                </Button>
              </div>
            </div>
          )}

          {/* Results Step */}
          {step === "results" && (
            <div className="space-y-8 pb-12">
              <div className="text-center space-y-2">
                <h3 className="text-4xl font-black italic tracking-tighter">GALLERY</h3>
                <p className="text-muted-foreground uppercase text-xs tracking-[0.3em] font-bold">
                  Your captured memories from the session
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {capturedPhotos.map((photo) => (
                  <div key={photo.id} className="group relative overflow-hidden rounded-3xl bg-neutral-900 border border-white/5 shadow-2xl aspect-[3/4]">
                    <img src={photo.url} alt="Result" className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-700" />
                    <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/90 via-black/40 to-transparent">
                      <Button
                        onClick={() => downloadPhoto(photo.url, photo.backgroundName)}
                        className="w-full h-12 rounded-xl bg-white/10 backdrop-blur-md hover:bg-white text-white hover:text-black transition-all"
                      >
                        <Download className="mr-2 h-5 w-5" />
                        Save to Devce
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex gap-4 justify-center border-t border-white/5 pt-8">
                <Button onClick={takeAnother} size="lg" className="h-16 px-10 rounded-2xl bg-indigo-600 hover:bg-indigo-500 font-bold">
                  Take Another
                </Button>
                <Button onClick={reset} size="lg" variant="outline" className="h-16 px-10 rounded-2xl border-white/10">
                  Start Fresh
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Hidden Global Capture Canvas */}
        <canvas ref={canvasRef} className="hidden" />
      </div>
    </div>
  )
}
