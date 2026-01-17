"use client"

import { useState } from "react"
import { X, Shirt, ShoppingBag, Sparkles, RefreshCw, ExternalLink, TrendingUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface ClothesRecommendationModalProps {
  isOpen: boolean
  onClose: () => void
}

interface OutfitRecommendation {
  outfit_items: Array<{
    id: string
    name: string
    category: string
    color?: string
    images?: string[]
  }>
  confidence_score: number
  occasion: string
  reasoning: string
  style_notes?: string
  color_palette?: string[]
}

interface MissingItemRecommendation {
  category: string
  description: string
  reason: string
  search_query: string
  priority: "high" | "medium" | "low"
  product_links: Array<{
    url: string
    title: string
    description: string
  }>
}

interface RecommendationResult {
  existing_outfits: OutfitRecommendation[]
  missing_items: MissingItemRecommendation[]
  occasion: string | null
  analysis_summary: string
  user_style_profile?: {
    dominant_colors: string[]
    style_keywords: string[]
    common_occasions: string[]
    style_summary: string
  }
}

export function ClothesRecommendationModal({ isOpen, onClose }: ClothesRecommendationModalProps) {
  const [occasion, setOccasion] = useState<string>("")
  const [customOccasion, setCustomOccasion] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<RecommendationResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const occasions = [
    { value: "work", label: "Work / Office" },
    { value: "casual", label: "Casual Day Out" },
    { value: "date night", label: "Date Night" },
    { value: "formal", label: "Formal Event" },
    { value: "party", label: "Party / Night Out" },
    { value: "wedding", label: "Wedding" },
    { value: "gym", label: "Gym / Workout" },
    { value: "beach", label: "Beach / Vacation" },
    { value: "custom", label: "Custom Occasion..." },
  ]

  const generateRecommendations = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const selectedOccasion = occasion === "custom" ? customOccasion : occasion
      
      const response = await fetch("http://localhost:8000/api/recommendations/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: "current_user", // TODO: Get from auth context
          occasion: selectedOccasion || undefined,
          max_outfits: 5,
          max_shopping_items: 5,
        }),
      })

      if (!response.ok) {
        throw new Error(`Failed to generate recommendations: ${response.statusText}`)
      }

      const data = await response.json()
      setRecommendations(data)
    } catch (err) {
      console.error("Error generating recommendations:", err)
      setError(
        err instanceof Error ? err.message : "Failed to generate recommendations. Make sure the backend is running."
      )
    } finally {
      setIsLoading(false)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-500/20 text-red-700 dark:text-red-400"
      case "medium":
        return "bg-yellow-500/20 text-yellow-700 dark:text-yellow-400"
      case "low":
        return "bg-green-500/20 text-green-700 dark:text-green-400"
      default:
        return "bg-gray-500/20 text-gray-700 dark:text-gray-400"
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="relative h-[90vh] w-[95vw] max-w-6xl overflow-hidden rounded-3xl bg-background shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/50 bg-background/95 px-6 py-4 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-teal-300/80 via-cyan-200/70 to-blue-200/60">
              <Shirt className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold">AI Outfit Recommendations</h2>
              <p className="text-sm text-muted-foreground">
                {recommendations
                  ? "Your personalized style suggestions"
                  : "Get AI-powered outfit ideas and shopping advice"}
              </p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="h-[calc(90vh-80px)] overflow-y-auto p-6">
          {!recommendations ? (
            /* Input Section */
            <div className="mx-auto max-w-2xl space-y-6">
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium">
                    What's the occasion? (Optional)
                  </label>
                  <Select value={occasion} onValueChange={setOccasion}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select an occasion or leave blank for general advice" />
                    </SelectTrigger>
                    <SelectContent>
                      {occasions.map((occ) => (
                        <SelectItem key={occ.value} value={occ.value}>
                          {occ.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {occasion === "custom" && (
                  <div>
                    <label className="mb-2 block text-sm font-medium">
                      Describe your occasion
                    </label>
                    <Textarea
                      value={customOccasion}
                      onChange={(e) => setCustomOccasion(e.target.value)}
                      placeholder="e.g., 'Job interview at a creative agency' or 'Brunch with friends'"
                      className="h-24"
                    />
                  </div>
                )}
              </div>

              {error && (
                <div className="rounded-lg bg-red-500/10 p-4 text-red-600 dark:text-red-400">
                  <p className="font-medium">Error</p>
                  <p className="text-sm">{error}</p>
                </div>
              )}

              <Button
                size="lg"
                onClick={generateRecommendations}
                disabled={isLoading || (occasion === "custom" && !customOccasion.trim())}
                className="w-full gap-2 bg-gradient-to-r from-teal-300/90 via-cyan-200/80 to-blue-200/70 text-foreground hover:from-teal-300 hover:via-cyan-200 hover:to-blue-200"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="h-5 w-5 animate-spin" />
                    AI is analyzing your wardrobe...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    Get Recommendations
                  </>
                )}
              </Button>

              <div className="rounded-lg bg-muted p-4">
                <p className="text-sm text-muted-foreground">
                  💡 <strong>What you'll get:</strong>
                  <br />• Complete outfit combinations from your wardrobe
                  <br />• Missing pieces to enhance your style
                  <br />• Shopping links for recommended items
                  <br />• Personalized fashion advice
                </p>
              </div>
            </div>
          ) : (
            /* Results Section */
            <div className="space-y-6">
              {/* Summary */}
              <div className="rounded-2xl bg-gradient-to-r from-teal-50 via-cyan-50 to-blue-50 p-6 dark:from-teal-950/50 dark:via-cyan-950/50 dark:to-blue-950/50">
                <h3 className="mb-2 flex items-center gap-2 text-lg font-bold">
                  <Sparkles className="h-5 w-5" />
                  Style Analysis
                </h3>
                <p className="text-muted-foreground">{recommendations.analysis_summary}</p>
                
                {recommendations.user_style_profile && (
                  <div className="mt-4 grid gap-4 md:grid-cols-2">
                    <div>
                      <p className="mb-2 text-sm font-medium">Your Colors</p>
                      <div className="flex flex-wrap gap-2">
                        {recommendations.user_style_profile.dominant_colors.map((color) => (
                          <Badge key={color} variant="secondary">
                            {color}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="mb-2 text-sm font-medium">Your Style</p>
                      <div className="flex flex-wrap gap-2">
                        {recommendations.user_style_profile.style_keywords.map((style) => (
                          <Badge key={style} variant="secondary">
                            {style}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Tabs for Outfits and Shopping */}
              <Tabs defaultValue="outfits" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="outfits">
                    Outfit Ideas ({recommendations.existing_outfits.length})
                  </TabsTrigger>
                  <TabsTrigger value="shopping">
                    Shopping List ({recommendations.missing_items.length})
                  </TabsTrigger>
                </TabsList>

                {/* Outfit Recommendations */}
                <TabsContent value="outfits" className="space-y-4">
                  {recommendations.existing_outfits.length === 0 ? (
                    <div className="rounded-lg bg-muted p-8 text-center">
                      <Shirt className="mx-auto mb-2 h-12 w-12 text-muted-foreground" />
                      <p className="text-muted-foreground">
                        No outfit combinations available yet. Add more items to your wardrobe!
                      </p>
                    </div>
                  ) : (
                    recommendations.existing_outfits.map((outfit, index) => (
                      <div key={index} className="rounded-2xl border border-border/50 bg-card p-6 shadow-sm">
                        <div className="mb-4 flex items-start justify-between">
                          <div>
                            <h4 className="mb-1 font-bold">Outfit {index + 1}</h4>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline">{outfit.occasion}</Badge>
                              <span className="text-sm text-muted-foreground">
                                {outfit.confidence_score}% confidence
                              </span>
                            </div>
                          </div>
                          {outfit.color_palette && (
                            <div className="flex gap-1">
                              {outfit.color_palette.slice(0, 4).map((color, i) => (
                                <div
                                  key={i}
                                  className="h-6 w-6 rounded-full border border-border"
                                  style={{ backgroundColor: color }}
                                  title={color}
                                />
                              ))}
                            </div>
                          )}
                        </div>

                        <div className="mb-4 space-y-2">
                          <p className="text-sm font-medium">Items:</p>
                          <div className="flex flex-wrap gap-2">
                            {outfit.outfit_items.map((item) => (
                              <Badge key={item.id} variant="secondary">
                                {item.name}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        <div className="space-y-2 rounded-lg bg-muted p-4 text-sm">
                          <p>
                            <strong>Why this works:</strong> {outfit.reasoning}
                          </p>
                          {outfit.style_notes && (
                            <p className="text-muted-foreground">
                              💡 <strong>Tip:</strong> {outfit.style_notes}
                            </p>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </TabsContent>

                {/* Shopping Recommendations */}
                <TabsContent value="shopping" className="space-y-4">
                  {recommendations.missing_items.length === 0 ? (
                    <div className="rounded-lg bg-muted p-8 text-center">
                      <ShoppingBag className="mx-auto mb-2 h-12 w-12 text-muted-foreground" />
                      <p className="text-muted-foreground">
                        Great! Your wardrobe is well-stocked for this occasion.
                      </p>
                    </div>
                  ) : (
                    recommendations.missing_items.map((item, index) => (
                      <div key={index} className="rounded-2xl border border-border/50 bg-card p-6 shadow-sm">
                        <div className="mb-4 flex items-start justify-between">
                          <div className="flex-1">
                            <div className="mb-2 flex items-center gap-2">
                              <h4 className="font-bold">{item.description}</h4>
                              <Badge className={getPriorityColor(item.priority)}>
                                {item.priority} priority
                              </Badge>
                            </div>
                            <Badge variant="outline" className="mb-2">
                              {item.category}
                            </Badge>
                          </div>
                        </div>

                        <div className="mb-4 rounded-lg bg-muted p-4 text-sm">
                          <p>
                            <strong>Why you need it:</strong> {item.reason}
                          </p>
                        </div>

                        {item.product_links.length > 0 ? (
                          <div>
                            <p className="mb-3 text-sm font-medium">Where to shop:</p>
                            <div className="space-y-2">
                              {item.product_links.map((link, linkIndex) => (
                                <a
                                  key={linkIndex}
                                  href={link.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center justify-between rounded-lg border border-border/50 bg-background p-3 transition-colors hover:bg-muted"
                                >
                                  <div className="flex-1">
                                    <p className="font-medium">{link.title}</p>
                                    {link.description && (
                                      <p className="text-xs text-muted-foreground line-clamp-1">
                                        {link.description}
                                      </p>
                                    )}
                                  </div>
                                  <ExternalLink className="ml-2 h-4 w-4 flex-shrink-0 text-muted-foreground" />
                                </a>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="rounded-lg bg-muted p-4 text-sm text-muted-foreground">
                            <p>
                              💡 <strong>Search suggestion:</strong> "{item.search_query}"
                            </p>
                            <p className="mt-2 text-xs">
                              Product search is currently unavailable. Try searching for this on your favorite shopping site!
                            </p>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </TabsContent>
              </Tabs>

              {/* Actions */}
              <div className="flex justify-center gap-4">
                <Button
                  variant="outline"
                  onClick={() => {
                    setRecommendations(null)
                    setOccasion("")
                    setCustomOccasion("")
                  }}
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Another Occasion
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
