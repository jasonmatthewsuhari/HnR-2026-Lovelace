"use client"

import { useState, useRef, useEffect } from "react"
import { Video, VideoOff, Mic, MicOff, X, Volume2, VolumeX, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface VideoCallModalProps {
  isOpen: boolean
  onClose: () => void
}

export function VideoCallModal({ isOpen, onClose }: VideoCallModalProps) {
  const [isConnecting, setIsConnecting] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [isCameraOn, setIsCameraOn] = useState(true)
  const [isMicOn, setIsMicOn] = useState(true)
  const [isSpeakerOn, setIsSpeakerOn] = useState(true)
  const [showTextChat, setShowTextChat] = useState(false)
  const [textMessage, setTextMessage] = useState("")
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; message: string }>>([])
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [error, setError] = useState<string | null>(null)

  const videoRef = useRef<HTMLVideoElement>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioQueueRef = useRef<string[]>([])
  const isPlayingAudioRef = useRef(false)

  useEffect(() => {
    if (isOpen) {
      initializeMedia()
    }
    return () => {
      cleanup()
    }
  }, [isOpen])

  const initializeMedia = async () => {
    try {
      setError(null)
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: "user" },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
          channelCount: 1
        }
      })

      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      console.error("Error accessing media:", err)
      setError("Could not access camera/microphone. Please check permissions.")
    }
  }

  const cleanup = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    // Clear audio queue
    audioQueueRef.current = []
    isPlayingAudioRef.current = false

    setIsConnected(false)
    setIsConnecting(false)
    setChatMessages([])
  }

  const startVideoCall = async () => {
    if (!stream) {
      setError("Media not initialized. Please allow camera and microphone access.")
      return
    }

    setIsConnecting(true)
    setError(null)

    try {
      // Connect to backend WebSocket for Gemini Live API
      const ws = new WebSocket("ws://localhost:8000/api/video-call/live")

      ws.onopen = () => {
        console.log("WebSocket connected")
        setIsConnected(true)
        setIsConnecting(false)

        // Add welcome message
        setChatMessages([{
          role: "assistant",
          message: "Hey! I can hear you now. Just talk naturally - I'll respond with my voice!"
        }])

        // Start streaming audio
        if (isMicOn) {
          startAudioStreaming(ws)
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          // Handle text responses
          if (data.type === "text" && data.content) {
            setChatMessages(prev => [...prev, {
              role: "assistant",
              message: data.content
            }])
          }

          // Handle audio responses
          if (data.type === "audio" && data.content && isSpeakerOn) {
            playAudioResponse(data.content)
          }
        } catch (err) {
          console.error("Error parsing message:", err)
        }
      }

      ws.onerror = (error) => {
        console.error("WebSocket error:", error)
        setError("Connection error. Make sure the backend is running on http://localhost:8000")
        setIsConnected(false)
        setIsConnecting(false)
      }

      ws.onclose = () => {
        console.log("WebSocket closed")
        setIsConnected(false)
      }

    } catch (err) {
      console.error("Error starting video call:", err)
      setError("Failed to connect. Make sure the backend is running.")
      setIsConnecting(false)
    }
  }

  const startAudioStreaming = (ws: WebSocket) => {
    if (!stream) return

    // Get audio track
    const audioTrack = stream.getAudioTracks()[0]
    if (!audioTrack) {
      console.warn('No audio track available')
      return
    }

    try {
      // Create a new MediaStream with ONLY the audio track
      const audioStream = new MediaStream([audioTrack])

      // Check supported MIME types in order of preference
      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm;codecs=pcm',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/mp4',
        ''  // Let browser choose default
      ]

      let selectedMimeType = ''
      for (const mimeType of mimeTypes) {
        if (mimeType === '' || MediaRecorder.isTypeSupported(mimeType)) {
          selectedMimeType = mimeType
          console.log('Selected MIME type:', mimeType || 'browser default')
          break
        }
      }

      console.log('Creating MediaRecorder with MIME type:', selectedMimeType || 'default')

      // Create MediaRecorder for audio streaming with ONLY audio track
      const options: MediaRecorderOptions = {}
      if (selectedMimeType) {
        options.mimeType = selectedMimeType
      }

      const mediaRecorder = new MediaRecorder(audioStream, options)
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
          console.log('Sending audio chunk, size:', event.data.size)
          // Send audio chunk to backend
          event.data.arrayBuffer().then(buffer => {
            const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)))
            ws.send(JSON.stringify({
              type: "audio",
              data: base64,
              mimeType: mediaRecorder.mimeType
            }))
          })
        }
      }

      mediaRecorder.onerror = (event: Event) => {
        console.error('MediaRecorder error:', event)
        const errorEvent = event as ErrorEvent
        console.error('Error details:', errorEvent.error)
        // Don't crash - just stop recording
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
          mediaRecorderRef.current.stop()
        }
      }

      mediaRecorder.onstart = () => {
        console.log('MediaRecorder started successfully')
      }

      mediaRecorder.onstop = () => {
        console.log('MediaRecorder stopped')
      }

      // Start recording with timeslice to send chunks periodically
      // Use 1000ms (1 second) chunks
      mediaRecorder.start(1000)
      console.log('Audio streaming started with 1s chunks')
    } catch (err) {
      console.error("Error starting audio streaming:", err)
      if (err instanceof Error) {
        console.error('Error name:', err.name)
        console.error('Error message:', err.message)
      }
      // Don't set error state - allow video call to continue with text only
      console.log('Continuing with text-only mode')
    }
  }

  const playAudioResponse = async (base64Audio: string) => {
    // Add to queue instead of playing immediately
    audioQueueRef.current.push(base64Audio)
    console.log('Added audio to queue. Queue length:', audioQueueRef.current.length)

    // Start processing queue if not already playing
    if (!isPlayingAudioRef.current) {
      processAudioQueue()
    }
  }

  const processAudioQueue = async () => {
    if (isPlayingAudioRef.current || audioQueueRef.current.length === 0) {
      return
    }

    isPlayingAudioRef.current = true

    while (audioQueueRef.current.length > 0) {
      const base64Audio = audioQueueRef.current.shift()!

      try {
        console.log('Playing audio from queue, remaining:', audioQueueRef.current.length)

        // Decode base64 to raw bytes
        const binaryString = atob(base64Audio)
        const bytes = new Uint8Array(binaryString.length)
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }

        console.log('Decoded bytes:', bytes.length)

        // Create audio context if not exists
        if (!audioContextRef.current) {
          audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
        }

        const audioContext = audioContextRef.current

        // Gemini sends 16-bit PCM at 24kHz, little-endian
        const numSamples = bytes.length / 2
        const audioBuffer = audioContext.createBuffer(1, numSamples, 24000)
        const channelData = audioBuffer.getChannelData(0)

        // Convert 16-bit PCM to float32 (little-endian)
        let sampleIndex = 0
        for (let i = 0; i < bytes.length; i += 2) {
          // Little-endian: low byte first, then high byte
          const low = bytes[i]
          const high = bytes[i + 1]
          const int16 = (high << 8) | low
          // Convert to signed int16
          const signedInt16 = int16 > 32767 ? int16 - 65536 : int16
          // Normalize to -1.0 to 1.0
          channelData[sampleIndex++] = signedInt16 / 32768.0
        }

        console.log('Playing audio buffer with', numSamples, 'samples')

        // Play audio and wait for it to finish
        await new Promise<void>((resolve) => {
          const source = audioContext.createBufferSource()
          source.buffer = audioBuffer
          source.connect(audioContext.destination)

          source.onended = () => {
            console.log('Audio chunk finished')
            resolve()
          }

          source.start()
        })

      } catch (err) {
        console.error("Error playing audio chunk:", err)
        // Continue to next chunk even if this one failed
      }
    }

    isPlayingAudioRef.current = false
    console.log('Audio queue finished')
  }

  const sendTextMessage = () => {
    if (!textMessage.trim() || !isConnected) return

    // Add to chat
    setChatMessages(prev => [...prev, {
      role: "user",
      message: textMessage
    }])

    // TODO: Send to backend WebSocket
    // For now, just simulate a response
    setTimeout(() => {
      setChatMessages(prev => [...prev, {
        role: "assistant",
        message: "I heard you! (Note: Backend WebSocket integration needed)"
      }])
    }, 1000)

    setTextMessage("")
  }

  const toggleCamera = () => {
    if (stream) {
      const videoTrack = stream.getVideoTracks()[0]
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled
        setIsCameraOn(videoTrack.enabled)
      }
    }
  }

  const toggleMic = () => {
    if (stream) {
      const audioTrack = stream.getAudioTracks()[0]
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled
        setIsMicOn(audioTrack.enabled)
      }
    }
  }

  const toggleSpeaker = () => {
    setIsSpeakerOn(!isSpeakerOn)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="relative h-[90vh] w-[95vw] max-w-7xl overflow-hidden rounded-3xl bg-background shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/50 bg-background/95 px-6 py-4 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-purple-300/80 via-pink-200/70 to-blue-200/60">
              <Video className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Video Call with Virtual Boyfriend</h2>
              <p className="text-sm text-muted-foreground">
                {isConnected ? "🟢 Connected - Your fashion advisor is listening!" :
                  isConnecting ? "🟡 Connecting..." :
                    "🔴 Not connected"}
              </p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Main Content */}
        <div className="flex h-[calc(90vh-80px)]">
          {/* Video Area */}
          <div className="flex flex-1 flex-col">
            {/* Video Feed */}
            <div className="relative flex-1 bg-black">
              {error ? (
                <div className="flex h-full items-center justify-center p-8">
                  <div className="text-center">
                    <p className="mb-4 text-lg text-red-500">{error}</p>
                    <Button onClick={initializeMedia}>Try Again</Button>
                  </div>
                </div>
              ) : (
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className={`h-full w-full object-cover ${!isCameraOn ? 'hidden' : ''}`}
                />
              )}

              {!isCameraOn && !error && (
                <div className="flex h-full items-center justify-center bg-black">
                  <div className="text-center">
                    <VideoOff className="mx-auto mb-4 h-16 w-16 text-white/50" />
                    <p className="text-white/70">Camera is off</p>
                  </div>
                </div>
              )}

              {/* Status indicators */}
              {isConnected && (
                <div className="absolute left-4 top-4">
                  <div className="flex items-center gap-2 rounded-full bg-green-500/90 px-3 py-1 text-sm font-medium text-white">
                    <div className="h-2 w-2 animate-pulse rounded-full bg-white" />
                    Live
                  </div>
                </div>
              )}
            </div>

            {/* Controls */}
            <div className="flex items-center justify-center gap-4 border-t border-border/50 bg-background/95 p-4 backdrop-blur-sm">
              <Button
                variant={isCameraOn ? "default" : "destructive"}
                size="icon"
                className="h-12 w-12 rounded-full"
                onClick={toggleCamera}
              >
                {isCameraOn ? <Video className="h-5 w-5" /> : <VideoOff className="h-5 w-5" />}
              </Button>

              <Button
                variant={isMicOn ? "default" : "destructive"}
                size="icon"
                className="h-12 w-12 rounded-full"
                onClick={toggleMic}
              >
                {isMicOn ? <Mic className="h-5 w-5" /> : <MicOff className="h-5 w-5" />}
              </Button>

              <Button
                variant={isSpeakerOn ? "default" : "destructive"}
                size="icon"
                className="h-12 w-12 rounded-full"
                onClick={toggleSpeaker}
              >
                {isSpeakerOn ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
              </Button>

              <Button
                variant={showTextChat ? "secondary" : "outline"}
                size="icon"
                className="h-12 w-12 rounded-full"
                onClick={() => setShowTextChat(!showTextChat)}
              >
                <MessageSquare className="h-5 w-5" />
              </Button>

              {!isConnected && (
                <Button
                  size="lg"
                  disabled={isConnecting || !!error}
                  onClick={startVideoCall}
                  className="ml-4 gap-2 bg-gradient-to-r from-purple-300/90 via-pink-200/80 to-blue-200/70 text-foreground hover:from-purple-300 hover:via-pink-200 hover:to-blue-200"
                >
                  {isConnecting ? "Connecting..." : "Start Call"}
                </Button>
              )}
            </div>
          </div>

          {/* Chat Sidebar */}
          {showTextChat && (
            <div className="flex w-96 flex-col border-l border-border/50 bg-background">
              <div className="border-b border-border/50 px-4 py-3">
                <h3 className="font-semibold">Chat</h3>
              </div>

              <div className="flex-1 space-y-4 overflow-y-auto p-4">
                {chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-2 ${msg.role === 'user'
                        ? 'bg-gradient-to-r from-purple-300/90 via-pink-200/80 to-blue-200/70 text-foreground'
                        : 'bg-muted'
                        }`}
                    >
                      <p className="text-sm">{msg.message}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="border-t border-border/50 p-4">
                <div className="flex gap-2">
                  <Textarea
                    value={textMessage}
                    onChange={(e) => setTextMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        sendTextMessage()
                      }
                    }}
                    placeholder="Type a message..."
                    className="min-h-[60px] resize-none"
                  />
                  <Button onClick={sendTextMessage} disabled={!textMessage.trim()}>
                    Send
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Instructions */}
        {!isConnected && !isConnecting && !error && (
          <div className="absolute bottom-20 left-1/2 -translate-x-1/2 rounded-2xl bg-background/95 p-6 shadow-lg backdrop-blur-sm">
            <h3 className="mb-3 text-center font-semibold">Ready for your live video call?</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>✓ Your camera and microphone are ready</li>
              <li>✓ Talk naturally - the avatar hears you</li>
              <li>✓ Avatar responds with voice in real-time</li>
              <li>✓ Show outfits and get instant fashion advice</li>
            </ul>
            <p className="mt-4 text-center text-xs text-muted-foreground">
              Tip: Speak clearly and wait for the avatar to finish responding
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
