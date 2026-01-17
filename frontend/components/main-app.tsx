"use client"

import { useState } from "react"
import { Camera, Menu, Video, Sparkles, Calendar, ShoppingBag, Shirt } from "lucide-react"
import { ProfilePage } from "@/components/app/profile-page"
import { CalendarPage } from "@/components/app/calendar-page"
import { PhotoboothModal } from "@/components/photobooth-modal"
import { VideoCallModal } from "@/components/video-call-modal"
import { VirtualTryOnModal } from "@/components/virtual-tryon-modal"
import { SearchProductsModal } from "@/components/search-products-modal"
import { ClothesRecommendationModal } from "@/components/clothes-recommendation-modal"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"

export function MainApp() {
  const [showPhotobooth, setShowPhotobooth] = useState(false)
  const [showVideoCall, setShowVideoCall] = useState(false)
  const [showVirtualTryOn, setShowVirtualTryOn] = useState(false)
  const [showSearchProducts, setShowSearchProducts] = useState(false)
  const [showClothesRecommendation, setShowClothesRecommendation] = useState(false)
  const [showCalendar, setShowCalendar] = useState(false)

  return (
    <div className="relative min-h-screen" style={{ zIndex: 2 }}>
      {/* Features Menu - Top Left */}
      <div className="fixed left-4 top-4 z-40">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              size="icon"
              variant="ghost"
              className="h-12 w-12 rounded-full bg-gradient-to-br from-purple-300/20 via-pink-200/15 to-blue-200/10 backdrop-blur-sm transition-all hover:scale-105 hover:from-purple-300/30 hover:via-pink-200/25 hover:to-blue-200/20"
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
                <div className="text-xs text-muted-foreground">Live chat with your fashion advisor</div>
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
                <div className="text-xs text-muted-foreground">See how clothes look on you</div>
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
                <div className="text-xs text-muted-foreground">Take couple's photos with AI</div>
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
                <div className="font-semibold">Search Products</div>
                <div className="text-xs text-muted-foreground">Find clothing from Singapore stores</div>
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
                <div className="font-semibold">Outfit Recommendations</div>
                <div className="text-xs text-muted-foreground">AI-powered style & shopping advice</div>
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
                <div className="font-semibold">Your Calendar</div>
                <div className="text-xs text-muted-foreground">Sync with Google Calendar</div>
              </div>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Main Content - Profile Page Only */}
      <ProfilePage />

      {/* Video Call Modal */}
      <VideoCallModal 
        isOpen={showVideoCall} 
        onClose={() => setShowVideoCall(false)} 
      />

      {/* Virtual Try-On Modal */}
      <VirtualTryOnModal 
        isOpen={showVirtualTryOn} 
        onClose={() => setShowVirtualTryOn(false)} 
      />

      {/* Photobooth Modal */}
      <PhotoboothModal
        isOpen={showPhotobooth}
        onClose={() => setShowPhotobooth(false)}
        avatarUrl="http://localhost:8000/api/photobooth/avatar"
      />

      {/* Search Products Modal */}
      <SearchProductsModal
        isOpen={showSearchProducts}
        onClose={() => setShowSearchProducts(false)}
      />

      {/* Clothes Recommendation Modal */}
      <ClothesRecommendationModal
        isOpen={showClothesRecommendation}
        onClose={() => setShowClothesRecommendation(false)}
      />

      {/* Calendar Page */}
      <CalendarPage
        isOpen={showCalendar}
        onClose={() => setShowCalendar(false)}
      />
    </div>
  )
}
