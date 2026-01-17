"use client"

import { useState } from "react"
import { X, Search, Loader2, ShoppingBag } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface ProductResult {
  url: string
  image?: string | null
  title: string
  description: string
}

interface SearchProductsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function SearchProductsModal({ isOpen, onClose }: SearchProductsModalProps) {
  const [query, setQuery] = useState("")
  const [size, setSize] = useState("")
  const [color, setColor] = useState("")
  const [brand, setBrand] = useState("")
  const [category, setCategory] = useState("")
  const [results, setResults] = useState<ProductResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Please enter a search query")
      return
    }

    setLoading(true)
    setError("")
    setResults([])

    try {
      // Build query params
      const params = new URLSearchParams({
        query: query.trim(),
        n: "10",
      })
      
      if (size) params.append("size", size)
      if (color) params.append("color", color)
      if (brand) params.append("brand", brand)
      if (category) params.append("category", category)

      const response = await fetch(`http://localhost:8000/api/search/clothes?${params}`)
      
      if (!response.ok) {
        throw new Error("Search failed. Please try again.")
      }

      const data = await response.json()
      setResults(data.products || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !loading) {
      handleSearch()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-3xl border border-border/50 bg-gradient-to-br from-background/95 to-muted/30 shadow-2xl backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/50 bg-gradient-to-r from-purple-300/10 via-pink-200/10 to-blue-200/10 p-6">
          <div>
            <h2 className="text-2xl font-bold">Search Products</h2>
            <p className="text-sm text-muted-foreground">Find clothing items from Singapore stores</p>
          </div>
          <Button
            size="icon"
            variant="ghost"
            onClick={onClose}
            className="h-10 w-10 rounded-full hover:bg-muted/50"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto p-6" style={{ maxHeight: "calc(90vh - 100px)" }}>
          {/* Search Form */}
          <div className="space-y-4 rounded-2xl border border-border/50 bg-background/50 p-6 backdrop-blur-sm">
            {/* Main Query */}
            <div>
              <Label htmlFor="query">What are you looking for?</Label>
              <div className="mt-1.5 flex gap-2">
                <Input
                  id="query"
                  placeholder="e.g., summer dress, running shoes, casual jacket"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="flex-1"
                />
                <Button 
                  onClick={handleSearch} 
                  disabled={loading || !query.trim()}
                  className="bg-gradient-to-r from-purple-400 to-pink-400 hover:from-purple-500 hover:to-pink-500"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-4 w-4" />
                      Search
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Filters */}
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <div>
                <Label htmlFor="size" className="text-xs">Size (optional)</Label>
                <Input
                  id="size"
                  placeholder="e.g., M, 32"
                  value={size}
                  onChange={(e) => setSize(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="color" className="text-xs">Color (optional)</Label>
                <Input
                  id="color"
                  placeholder="e.g., black, blue"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="brand" className="text-xs">Brand (optional)</Label>
                <Input
                  id="brand"
                  placeholder="e.g., Nike, Zara"
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="category" className="text-xs">Category (optional)</Label>
                <Input
                  id="category"
                  placeholder="e.g., Tops, Shoes"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="mt-1"
                />
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-600 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">
              {error}
            </div>
          )}

          {/* Results */}
          {results.length > 0 && (
            <div className="mt-6 space-y-3">
              <h3 className="flex items-center gap-2 text-lg font-semibold">
                <ShoppingBag className="h-5 w-5" />
                Found {results.length} products
              </h3>
              
              <div className="space-y-3">
                {results.map((product, index) => (
                  <div
                    key={index}
                    className="group rounded-xl border border-border/50 bg-background/50 p-4 backdrop-blur-sm transition-all hover:border-purple-300/50 hover:bg-purple-50/50 hover:shadow-md dark:hover:bg-purple-900/10"
                  >
                    <div className="flex items-start gap-4">
                      {/* Product Image */}
                      <div className="relative h-24 w-24 shrink-0 overflow-hidden rounded-lg bg-gradient-to-br from-purple-300/30 via-pink-300/20 to-orange-300/30">
                        {product.image ? (
                          <img
                            src={product.image}
                            alt={product.title}
                            className="h-full w-full object-cover"
                            onError={(e) => {
                              // If image fails to load, hide it and show icon instead
                              e.currentTarget.style.display = 'none'
                              const fallback = e.currentTarget.nextElementSibling
                              if (fallback) {
                                fallback.classList.remove('hidden')
                              }
                            }}
                          />
                        ) : null}
                        <div className={product.image ? "hidden absolute inset-0 flex items-center justify-center" : "flex items-center justify-center h-full"}>
                          <ShoppingBag className="h-12 w-12 text-purple-500/50 dark:text-purple-400/50" />
                        </div>
                      </div>

                      {/* Product Details */}
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-foreground group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                          {product.title}
                        </h4>
                        {product.description && (
                          <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                            {product.description}
                          </p>
                        )}
                        <div className="mt-2 flex items-center gap-2">
                          <div className="rounded-full bg-purple-100 dark:bg-purple-900/30 px-2 py-0.5 text-xs font-medium text-purple-600 dark:text-purple-400">
                            {new URL(product.url).hostname.replace('www.', '')}
                          </div>
                        </div>
                      </div>

                      {/* Arrow Link */}
                      <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex shrink-0 items-center justify-center rounded-full bg-gradient-to-r from-purple-400 to-pink-400 p-3 text-white transition-all hover:scale-110 hover:from-purple-500 hover:to-pink-500 hover:shadow-lg"
                        title="View Product"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-5 w-5"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {!loading && !error && results.length === 0 && query && (
            <div className="mt-6 rounded-xl border border-border/50 bg-background/50 p-12 text-center backdrop-blur-sm">
              <ShoppingBag className="mx-auto h-12 w-12 text-muted-foreground/50" />
              <p className="mt-4 text-muted-foreground">
                No results yet. Try searching for something!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
