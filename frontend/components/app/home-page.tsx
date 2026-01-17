"use client"

import { useState, useEffect, useRef } from "react"
import { Heart, Bookmark, Share2, ShoppingBag } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ClothingItem {
  id: string
  name: string
  image: string
  category: string
  color?: string
  size?: string
  brand?: string
  price?: string
  source?: string
}

interface OutfitRecommendation {
  id: string
  title: string
  description: string
  items: ClothingItem[]
  occasion: string
  weather: string
  liked: boolean
  saved: boolean
}

function HomePage() {
  const [recommendations, setRecommendations] = useState<OutfitRecommendation[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const [userClothes, setUserClothes] = useState<ClothingItem[]>([])

  // Load user's clothes from localStorage
  useEffect(() => {
    const clothes = localStorage.getItem("lovelace_clothes")
    if (clothes) {
      setUserClothes(JSON.parse(clothes))
    }
  }, [])

  // Generate mock recommendations based on user's wardrobe
  useEffect(() => {
    const generateRecommendations = () => {
      if (userClothes.length === 0) {
        // Show empty state recommendations
        return [
          {
            id: "empty-1",
            title: "Start Building Your Wardrobe",
            description:
              "Add clothes to your wardrobe to get personalized outfit recommendations based on weather, occasion, and your style.",
            items: [],
            occasion: "Getting Started",
            weather: "Any",
            liked: false,
            saved: false,
          },
        ]
      }

      // Group clothes by category
      const tops = userClothes.filter((c) => c.category === "tops")
      const bottoms = userClothes.filter((c) => c.category === "bottoms")
      const shoes = userClothes.filter((c) => c.category === "shoes")
      const accessories = userClothes.filter((c) => c.category === "accessories")

      const occasions = [
        "Casual Day Out",
        "Work Meeting",
        "Coffee Date",
        "Evening Event",
        "Weekend Brunch",
        "Gym Session",
      ]
      const weathers = ["Sunny", "Rainy", "Cold", "Warm", "Breezy"]

      const recs: OutfitRecommendation[] = []

      // Generate 10 recommendations
      for (let i = 0; i < 10; i++) {
        const outfit: ClothingItem[] = []

        if (tops.length > 0) outfit.push(tops[Math.floor(Math.random() * tops.length)])
        if (bottoms.length > 0) outfit.push(bottoms[Math.floor(Math.random() * bottoms.length)])
        if (shoes.length > 0) outfit.push(shoes[Math.floor(Math.random() * shoes.length)])
        if (accessories.length > 0 && Math.random() > 0.5) {
          outfit.push(accessories[Math.floor(Math.random() * accessories.length)])
        }

        recs.push({
          id: `rec-${i}`,
          title: `${occasions[Math.floor(Math.random() * occasions.length)]} Look`,
          description: "This outfit combines comfort with style, perfect for the occasion and weather forecast.",
          items: outfit,
          occasion: occasions[Math.floor(Math.random() * occasions.length)],
          weather: weathers[Math.floor(Math.random() * weathers.length)],
          liked: false,
          saved: false,
        })
      }

      return recs
    }

    setRecommendations(generateRecommendations())
  }, [userClothes])

  // Handle scroll snap
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleScroll = () => {
      const scrollPosition = container.scrollTop
      const itemHeight = container.clientHeight
      const index = Math.round(scrollPosition / itemHeight)
      setCurrentIndex(index)
    }

    container.addEventListener("scroll", handleScroll)
    return () => container.removeEventListener("scroll", handleScroll)
  }, [])

  const toggleLike = (id: string) => {
    setRecommendations((prev) => prev.map((rec) => (rec.id === id ? { ...rec, liked: !rec.liked } : rec)))
  }

  const toggleSave = (id: string) => {
    setRecommendations((prev) => prev.map((rec) => (rec.id === id ? { ...rec, saved: !rec.saved } : rec)))
  }

  const handleShare = (rec: OutfitRecommendation) => {
    // Share functionality
    console.log("[v0] Sharing outfit:", rec.title)
  }

  const handleShop = (rec: OutfitRecommendation) => {
    // Shop for similar items
    console.log("[v0] Shopping for outfit:", rec.title)
  }

  return (
    <div className="relative h-screen w-full overflow-hidden bg-background">
      {/* Scrollable container with snap */}
      <div
        ref={containerRef}
        className="h-full w-full snap-y snap-mandatory overflow-y-scroll"
        style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
      >
        <style jsx>{`
          div::-webkit-scrollbar {
            display: none;
          }
        `}</style>

        {recommendations.map((rec, index) => (
          <div key={rec.id} className="relative flex h-full w-full snap-start snap-always items-center justify-center">
            {/* Background with outfit visualization */}
            <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/20 to-background">
              {rec.items.length > 0 ? (
                <div className="flex h-full items-center justify-center p-8">
                  <div className="grid max-w-2xl grid-cols-2 gap-6">
                    {rec.items.map((item, idx) => (
                      <div
                        key={`${item.id}-${idx}`}
                        className="relative aspect-square overflow-hidden rounded-2xl bg-card shadow-xl"
                      >
                        <img
                          src={item.image || "/placeholder.svg"}
                          alt={item.name}
                          className="h-full w-full object-cover"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="flex h-full items-center justify-center p-8">
                  <div className="text-center">
                    <div className="mb-6 text-8xl">👗</div>
                    <h3 className="mb-2 text-2xl font-bold">No Clothes Yet</h3>
                    <p className="text-muted-foreground">Add items to your wardrobe to see recommendations</p>
                  </div>
                </div>
              )}
            </div>

            {/* Overlay content */}
            <div className="absolute inset-0 flex flex-col justify-between p-6">
              {/* Top info */}
              <div className="flex items-start justify-between">
                <div className="rounded-full bg-background/80 px-4 py-2 backdrop-blur-sm">
                  <p className="text-sm font-medium">{rec.weather} Weather</p>
                </div>
                <div className="rounded-full bg-background/80 px-4 py-2 backdrop-blur-sm">
                  <p className="text-sm font-medium">{rec.occasion}</p>
                </div>
              </div>

              {/* Bottom info and actions */}
              <div className="flex items-end justify-between gap-4">
                {/* Left side - outfit details */}
                <div className="flex-1 space-y-2">
                  <h2 className="text-balance text-3xl font-bold text-foreground">{rec.title}</h2>
                  <p className="text-pretty text-sm text-foreground/80">{rec.description}</p>
                  {rec.items.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {rec.items.map((item, idx) => (
                        <div
                          key={`tag-${item.id}-${idx}`}
                          className="rounded-full bg-background/80 px-3 py-1 text-xs backdrop-blur-sm"
                        >
                          {item.name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Right side - action buttons */}
                <div className="flex flex-col gap-4">
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-14 w-14 rounded-full bg-background/80 backdrop-blur-sm"
                    onClick={() => toggleLike(rec.id)}
                  >
                    <Heart className={`h-6 w-6 ${rec.liked ? "fill-red-500 text-red-500" : ""}`} />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-14 w-14 rounded-full bg-background/80 backdrop-blur-sm"
                    onClick={() => toggleSave(rec.id)}
                  >
                    <Bookmark className={`h-6 w-6 ${rec.saved ? "fill-primary" : ""}`} />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-14 w-14 rounded-full bg-background/80 backdrop-blur-sm"
                    onClick={() => handleShare(rec)}
                  >
                    <Share2 className="h-6 w-6" />
                  </Button>
                  {rec.items.length > 0 && (
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-14 w-14 rounded-full bg-background/80 backdrop-blur-sm"
                      onClick={() => handleShop(rec)}
                    >
                      <ShoppingBag className="h-6 w-6" />
                    </Button>
                  )}
                </div>
              </div>
            </div>

            {/* Scroll indicator */}
            {index < recommendations.length - 1 && (
              <div className="absolute bottom-24 left-1/2 -translate-x-1/2 animate-bounce">
                <div className="h-8 w-0.5 rounded-full bg-foreground/30" />
              </div>
            )}
          </div>
        ))}

        {/* Load more trigger */}
        {recommendations.length > 0 && (
          <div className="flex h-screen snap-start items-center justify-center">
            <div className="text-center">
              <div className="mb-4 text-4xl">✨</div>
              <p className="text-lg font-medium text-muted-foreground">Loading more recommendations...</p>
            </div>
          </div>
        )}
      </div>

      {/* Progress indicator */}
      <div className="absolute right-4 top-1/2 flex -translate-y-1/2 flex-col gap-2">
        {recommendations.slice(0, 5).map((_, idx) => (
          <div
            key={idx}
            className={`h-2 w-2 rounded-full transition-all ${
              idx === currentIndex % recommendations.length ? "bg-foreground" : "bg-foreground/30"
            }`}
          />
        ))}
      </div>
    </div>
  )
}

export { HomePage }
export default HomePage
