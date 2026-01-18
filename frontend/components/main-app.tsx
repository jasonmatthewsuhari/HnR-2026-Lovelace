"use client"

import { useState, useEffect, useRef } from "react"
import { Camera, Menu, Video, Sparkles, Calendar, ShoppingBag, Shirt, Mic, Send, User, MicOff } from "lucide-react"
import { ProfilePage } from "@/components/app/profile-page"
import { CalendarPage } from "@/components/app/calendar-page"
import { PhotoboothModal } from "@/components/photobooth-modal"
import { VideoCallModal } from "@/components/video-call-modal"
import { VirtualTryOnModal } from "@/components/virtual-tryon-modal"
import { SearchProductsModal } from "@/components/search-products-modal"
import { ClothesRecommendationModal } from "@/components/clothes-recommendation-modal"
import { GLBViewerWrapper } from "@/components/glb-viewer-wrapper"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"

// Get backend URL for GLB models
const getBackendUrl = () => {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}

export function MainApp() {
  const [showPhotobooth, setShowPhotobooth] = useState(false)
  const [showVideoCall, setShowVideoCall] = useState(false)
  const [showVirtualTryOn, setShowVirtualTryOn] = useState(false)
  const [showSearchProducts, setShowSearchProducts] = useState(false)
  const [showClothesRecommendation, setShowClothesRecommendation] = useState(false)
  const [showCalendar, setShowCalendar] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  
  const [message, setMessage] = useState("")
  const [chatMessages, setChatMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([
    { role: 'assistant', content: 'Hey! Looking stunning today! Need help with your wardrobe?' }
  ])
  const [isRecording, setIsRecording] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [selectedBoyfriend, setSelectedBoyfriend] = useState<string>("")
  const [boyfriendModelUrl, setBoyfriendModelUrl] = useState<string>("")
  
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  
  // Load selected boyfriend from localStorage
  useEffect(() => {
    const profile = localStorage.getItem("lovelace-user-profile")
    if (profile) {
      try {
        const parsed = JSON.parse(profile)
        console.log('Loaded profile:', parsed)
        
        // Handle both string ID and object format
        let boyfriendId = 'alex' // default
        let modelUrl = ''
        
        if (parsed.selectedBoyfriend) {
          if (typeof parsed.selectedBoyfriend === 'string') {
            // It's a string ID (alex, mike, ryan)
            boyfriendId = parsed.selectedBoyfriend
            modelUrl = `${getBackendUrl()}/3d/models/boyfriends/${boyfriendId}`
          } else if (parsed.selectedBoyfriend.id) {
            // It's a custom boyfriend object with full details
            boyfriendId = parsed.selectedBoyfriend.id
            // Use the modelUrl from the object if available, otherwise construct it
            if (parsed.selectedBoyfriend.modelUrl) {
              modelUrl = parsed.selectedBoyfriend.modelUrl
            } else {
              // Assume it's a custom boyfriend
              modelUrl = `${getBackendUrl()}/3d/models/boyfriends/custom/${boyfriendId}`
            }
          }
        }
        
        console.log('Loaded boyfriend ID:', boyfriendId, 'Model URL:', modelUrl)
        setSelectedBoyfriend(boyfriendId)
        setBoyfriendModelUrl(modelUrl || `${getBackendUrl()}/3d/models/boyfriends/alex`)
      } catch (error) {
        console.error('Error parsing profile:', error)
        setSelectedBoyfriend('alex')
        setBoyfriendModelUrl(`${getBackendUrl()}/3d/models/boyfriends/alex`)
      }
    } else {
      console.log('No profile found in localStorage')
      setSelectedBoyfriend('alex')
      setBoyfriendModelUrl(`${getBackendUrl()}/3d/models/boyfriends/alex`)
    }
  }, [])
  
  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [chatMessages])
  
  // Connect to voice agent WebSocket
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = getBackendUrl().replace('http', 'ws') + '/voice-agent/ws'
      console.log('Connecting to voice agent:', wsUrl)
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      
      ws.onopen = () => {
        console.log('Voice agent connected')
        setIsConnected(true)
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'text') {
            // Add assistant message
            setChatMessages(prev => [...prev, {
              role: 'assistant',
              content: data.content
            }])
          } else if (data.type === 'function_call') {
            // Handle feature navigation
            handleFeatureNavigation(data.function, data.args)
          } else if (data.type === 'audio') {
            // Play audio response
            playAudioResponse(data.content)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
      }
      
      ws.onclose = () => {
        console.log('WebSocket closed')
        setIsConnected(false)
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000)
      }
    }
    
    connectWebSocket()
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])
  
  // Handle feature navigation from voice commands
  const handleFeatureNavigation = (functionName: string, args: any) => {
    console.log('Opening feature:', functionName, args)
    
    switch (functionName) {
      case 'open_video_call':
        setShowVideoCall(true)
        break
      case 'open_virtual_tryon':
        setShowVirtualTryOn(true)
        break
      case 'open_photobooth':
        setShowPhotobooth(true)
        break
      case 'open_shop':
        setShowSearchProducts(true)
        break
      case 'open_recommendations':
        setShowClothesRecommendation(true)
        break
      case 'open_calendar':
        setShowCalendar(true)
        break
      case 'open_wardrobe':
        setShowProfile(true)
        break
    }
    
    // Add feedback message
    const featureNames: Record<string, string> = {
      'open_video_call': 'Opening video call',
      'open_virtual_tryon': 'Opening virtual try-on',
      'open_photobooth': 'Opening photobooth',
      'open_shop': 'Opening shop',
      'open_recommendations': 'Opening recommendations',
      'open_calendar': 'Opening calendar',
      'open_wardrobe': 'Opening wardrobe'
    }
    
    setChatMessages(prev => [...prev, {
      role: 'assistant',
      content: `${featureNames[functionName] || 'Opening feature'}...`
    }])
  }
  
  // Play audio response
  const playAudioResponse = async (base64Audio: string) => {
    try {
      // Decode base64 audio
      const binaryString = atob(base64Audio)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
      }
      
      const audioContext = audioContextRef.current
      const audioBuffer = await audioContext.decodeAudioData(bytes.buffer)
      
      const source = audioContext.createBufferSource()
      source.buffer = audioBuffer
      source.connect(audioContext.destination)
      source.start()
    } catch (error) {
      console.error('Error playing audio:', error)
    }
  }
  
  const handleSendMessage = async () => {
    if (!message.trim()) return
    
    // Add user message
    const userMessage = message
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setMessage("")
    
    // Send to voice agent
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'text',
        content: userMessage
      }))
    }
  }
  
  const handleMicClick = async () => {
    if (isRecording) {
      // Stop recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
      setIsRecording(false)
      
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'stop_recording'
        }))
      }
    } else {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        
        const mediaRecorder = new MediaRecorder(stream)
        mediaRecorderRef.current = mediaRecorder
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            // Convert to base64 and send
            event.data.arrayBuffer().then(buffer => {
              const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)))
              wsRef.current!.send(JSON.stringify({
                type: 'audio',
                data: base64
              }))
            })
          }
        }
        
        mediaRecorder.start(1000) // Send chunks every second
        setIsRecording(true)
        
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: 'start_recording'
          }))
        }
      } catch (error) {
        console.error('Error starting recording:', error)
        alert('Could not access microphone. Please check permissions.')
      }
    }
  }
  
  return (
    <div className="relative h-screen w-full overflow-hidden bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20">
      {/* Main Boyfriend Avatar - Full Screen Background */}
      <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 0 }}>
        <div className="h-full w-full">
          {selectedBoyfriend && boyfriendModelUrl && (
            <GLBViewerWrapper
              url={boyfriendModelUrl}
              width="100%"
              height="100%"
              autoRotate={false}
              className="h-full w-full"
            />
          )}
          {(!selectedBoyfriend || !boyfriendModelUrl) && (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500">Loading your boyfriend...</p>
            </div>
          )}
        </div>
      </div>

      {/* Top Navigation Bar */}
      <div className="fixed left-0 right-0 top-0 z-40 flex items-center justify-between bg-gradient-to-b from-white/80 via-white/60 to-transparent px-4 py-3 backdrop-blur-sm dark:from-gray-900/80 dark:via-gray-900/60">
        {/* Left: Features Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              size="icon"
              variant="ghost"
              className="h-10 w-10 rounded-full bg-white/50 backdrop-blur-sm transition-all hover:scale-105 hover:bg-white/80 dark:bg-gray-800/50 dark:hover:bg-gray-800/80"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56 rounded-2xl">
            <DropdownMenuItem
              onClick={() => setShowVideoCall(true)}
              className="cursor-pointer gap-3 rounded-xl p-3"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-purple-300/80 via-pink-200/70 to-blue-200/60">
                <Video className="h-4 w-4" />
              </div>
              <div>
                <div className="font-semibold">Video Call</div>
                <div className="text-xs text-muted-foreground">Live chat</div>
              </div>
            </DropdownMenuItem>
            
            <DropdownMenuItem
              onClick={() => setShowVirtualTryOn(true)}
              className="cursor-pointer gap-3 rounded-xl p-3"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-300/80 via-purple-200/70 to-pink-200/60">
                <Sparkles className="h-4 w-4" />
              </div>
              <div>
                <div className="font-semibold">Virtual Try-On</div>
                <div className="text-xs text-muted-foreground">Try on clothes</div>
              </div>
            </DropdownMenuItem>
            
            <DropdownMenuItem
              onClick={() => setShowPhotobooth(true)}
              className="cursor-pointer gap-3 rounded-xl p-3"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-pink-300/80 via-purple-200/70 to-blue-200/60">
                <Camera className="h-4 w-4" />
              </div>
              <div>
                <div className="font-semibold">Photobooth</div>
                <div className="text-xs text-muted-foreground">Take photos</div>
              </div>
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={() => setShowSearchProducts(true)}
              className="cursor-pointer gap-3 rounded-xl p-3"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-orange-300/80 via-pink-200/70 to-purple-200/60">
                <ShoppingBag className="h-4 w-4" />
              </div>
              <div>
                <div className="font-semibold">Shop</div>
                <div className="text-xs text-muted-foreground">Find clothes</div>
              </div>
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={() => setShowClothesRecommendation(true)}
              className="cursor-pointer gap-3 rounded-xl p-3"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-teal-300/80 via-cyan-200/70 to-blue-200/60">
                <Shirt className="h-4 w-4" />
              </div>
              <div>
                <div className="font-semibold">Recommendations</div>
                <div className="text-xs text-muted-foreground">Style advice</div>
              </div>
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={() => setShowCalendar(true)}
              className="cursor-pointer gap-3 rounded-xl p-3"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-green-300/80 via-blue-200/70 to-purple-200/60">
                <Calendar className="h-4 w-4" />
              </div>
              <div>
                <div className="font-semibold">Calendar</div>
                <div className="text-xs text-muted-foreground">Your events</div>
              </div>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        
        {/* Right: Profile */}
        <Button
          size="icon"
          variant="ghost"
          onClick={() => setShowProfile(true)}
          className="h-10 w-10 rounded-full bg-white/50 backdrop-blur-sm transition-all hover:scale-105 hover:bg-white/80 dark:bg-gray-800/50 dark:hover:bg-gray-800/80"
        >
          <User className="h-5 w-5" />
        </Button>
      </div>

      {/* Chat Interface - Bottom */}
      <div className="fixed bottom-0 left-0 right-0 z-30 flex flex-col bg-gradient-to-t from-white via-white/95 to-transparent px-4 pb-6 pt-8 dark:from-gray-900 dark:via-gray-900/95">
        {/* Chat Messages - Expandable */}
        {chatMessages.length > 1 && (
          <div 
            ref={chatContainerRef}
            className="mb-4 max-h-48 overflow-y-auto rounded-3xl bg-white/80 p-4 backdrop-blur-sm dark:bg-gray-800/80"
          >
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                className={`mb-2 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white'
                      : 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-white'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Input Box */}
        <div className="flex items-center gap-3">
          <div className="flex-1 rounded-full bg-white shadow-lg dark:bg-gray-800">
            <div className="flex items-center gap-2 px-6 py-4">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask me anything about fashion..."
                className="flex-1 bg-transparent text-base outline-none placeholder:text-gray-400 dark:placeholder:text-gray-500"
              />
              <button
                onClick={handleMicClick}
                className={`rounded-full p-2 transition-all ${
                  isRecording
                    ? 'bg-red-500 text-white animate-pulse'
                    : isConnected
                    ? 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    : 'opacity-50 cursor-not-allowed'
                }`}
                disabled={!isConnected}
                title={isRecording ? 'Stop recording' : isConnected ? 'Start voice input' : 'Connecting to voice agent...'}
              >
                {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </button>
            </div>
          </div>
          
          {/* Send Button */}
          <button
            onClick={handleSendMessage}
            disabled={!message.trim()}
            className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Profile Modal (Slide from right) */}
      {showProfile && (
        <div className="fixed inset-0 z-50 flex">
          {/* Backdrop */}
          <div 
            className="flex-1 bg-black/40 backdrop-blur-sm"
            onClick={() => setShowProfile(false)}
          />
          {/* Profile Panel */}
          <div className="w-full max-w-md animate-in slide-in-from-right overflow-y-auto bg-background">
            <ProfilePage />
          </div>
        </div>
      )}

      {/* Modals */}
      <VideoCallModal 
        isOpen={showVideoCall} 
        onClose={() => setShowVideoCall(false)} 
      />

      <VirtualTryOnModal 
        isOpen={showVirtualTryOn} 
        onClose={() => setShowVirtualTryOn(false)} 
      />

      <PhotoboothModal
        isOpen={showPhotobooth}
        onClose={() => setShowPhotobooth(false)}
        avatarUrl="http://localhost:8000/api/photobooth/avatar"
      />

      <SearchProductsModal
        isOpen={showSearchProducts}
        onClose={() => setShowSearchProducts(false)}
      />

      <ClothesRecommendationModal
        isOpen={showClothesRecommendation}
        onClose={() => setShowClothesRecommendation(false)}
      />

      <CalendarPage
        isOpen={showCalendar}
        onClose={() => setShowCalendar(false)}
      />
    </div>
  )
}
