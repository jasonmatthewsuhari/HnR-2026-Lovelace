"use client"

import type React from "react"

import { useState } from "react"
import { X, Upload, Camera, LinkIcon, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { addClothingItem, removeBackground } from "@/lib/api"
import { useAuth } from "@/hooks/use-auth"

export interface ClothingItem {
  id: string
  type: "online" | "camera"
  name: string
  images: string[]
  price?: string
  source?: string
  size?: string
  color?: string
  brand?: string
  category?: string
}

interface AddClothingModalProps {
  isOpen: boolean
  onClose: () => void
  onAddItem?: (item: ClothingItem) => void
}

export function AddClothingModal({ isOpen, onClose, onAddItem }: AddClothingModalProps) {
  const { user } = useAuth()
  const [method, setMethod] = useState<"online" | "camera" | null>(null)
  const [uploadedPhotos, setUploadedPhotos] = useState<string[]>([])
  const [isProcessingImages, setIsProcessingImages] = useState(false)

  // Form states
  const [productName, setProductName] = useState("")
  const [productPrice, setProductPrice] = useState("")
  const [productSource, setProductSource] = useState("")

  // Camera method states
  const [itemTitle, setItemTitle] = useState("")
  const [size, setSize] = useState("")
  const [color, setColor] = useState("")
  const [brand, setBrand] = useState("")
  const [category, setCategory] = useState("")

  const [searchQuery, setSearchQuery] = useState("")
  const [mockProducts] = useState([
    {
      id: "1",
      name: "Nike Air Force 1",
      price: "$110",
      source: "nike.com",
      image: "/placeholder.svg?height=200&width=200",
    },
    {
      id: "2",
      name: "Levi's 501 Original Jeans",
      price: "$98",
      source: "levis.com",
      image: "/placeholder.svg?height=200&width=200",
    },
    {
      id: "3",
      name: "Adidas Originals Hoodie",
      price: "$75",
      source: "adidas.com",
      image: "/placeholder.svg?height=200&width=200",
    },
    {
      id: "4",
      name: "Champion Crewneck Sweatshirt",
      price: "$45",
      source: "champion.com",
      image: "/placeholder.svg?height=200&width=200",
    },
    {
      id: "5",
      name: "Converse Chuck Taylor",
      price: "$65",
      source: "converse.com",
      image: "/placeholder.svg?height=200&width=200",
    },
    {
      id: "6",
      name: "Carhartt Work Jacket",
      price: "$120",
      source: "carhartt.com",
      image: "/placeholder.svg?height=200&width=200",
    },
  ])

  if (!isOpen) return null

  const resetForm = () => {
    setMethod(null)
    setUploadedPhotos([])
    setIsProcessingImages(false)
    setProductName("")
    setProductPrice("")
    setProductSource("")
    setItemTitle("")
    setSize("")
    setColor("")
    setBrand("")
    setCategory("")
    setSearchQuery("")
  }

  const handleAddOnlineItem = async (product: any) => {
    if (!user) {
      alert("Please log in to add clothing items")
      return
    }

    try {
      const clothingItem = {
        name: product.name,
        category: "other", // Default category for online items
        images: [product.image],
        price: product.price,
        source: product.source,
        tags: [] as string[],
      }

      const result = await addClothingItem(user.uid, clothingItem)

      // Call onAddItem with the full item from the response
      onAddItem?.(result.item)

      resetForm()
      onClose()
    } catch (error) {
      console.error("Failed to add clothing item:", error)
      alert("Failed to add clothing item. Please try again.")
    }
  }

  const handleAddCameraItem = async () => {
    if (!user) {
      alert("Please log in to add clothing items")
      return
    }

    try {
      const clothingItem = {
        name: itemTitle,
        category: category || "other",
        images: uploadedPhotos,
        color,
        size,
        brand,
        tags: [] as string[],
      }

      const result = await addClothingItem(user.uid, clothingItem)

      // Call onAddItem with the full item from the response
      onAddItem?.(result.item)

      resetForm()
      onClose()
    } catch (error) {
      console.error("Failed to add clothing item:", error)
      alert("Failed to add clothing item. Please try again.")
    }
  }

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || uploadedPhotos.length >= 3) return

    const newPhotos = Array.from(files).slice(0, 3 - uploadedPhotos.length)
    if (newPhotos.length === 0) return

    setIsProcessingImages(true)

    try {
      const processedPhotos: string[] = []

      for (const file of newPhotos) {
        try {
          // Remove background from the image
          const processedImageDataUrl = await removeBackground(file)
          processedPhotos.push(processedImageDataUrl)
        } catch (error) {
          console.error('Failed to remove background:', error)
          // Fallback to original image if background removal fails
          processedPhotos.push(URL.createObjectURL(file))
        }
      }

      setUploadedPhotos([...uploadedPhotos, ...processedPhotos])
    } catch (error) {
      console.error('Error processing images:', error)
    } finally {
      setIsProcessingImages(false)
    }
  }

  const removePhoto = (index: number) => {
    setUploadedPhotos(uploadedPhotos.filter((_, i) => i !== index))
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-md max-h-[90vh] overflow-y-auto rounded-3xl bg-background p-6 shadow-xl">
        {/* Close Button */}
        <button onClick={onClose} className="absolute right-4 top-4 rounded-full p-2 hover:bg-secondary">
          <X className="h-5 w-5" />
        </button>

        <h2 className="mb-6 text-xl font-bold">Add Clothing</h2>

        {!method ? (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground mb-4">Choose how you'd like to add your clothing:</p>

            <button
              onClick={() => setMethod("online")}
              className="w-full flex items-center gap-4 p-4 rounded-2xl border-2 border-border hover:border-foreground transition-colors"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-secondary">
                <LinkIcon className="h-6 w-6" />
              </div>
              <div className="text-left">
                <div className="font-semibold">From Online Listing</div>
                <div className="text-sm text-muted-foreground">Add from e-commerce sites</div>
              </div>
            </button>

            <button
              onClick={() => setMethod("camera")}
              className="w-full flex items-center gap-4 p-4 rounded-2xl border-2 border-border hover:border-foreground transition-colors"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-secondary">
                <Camera className="h-6 w-6" />
              </div>
              <div className="text-left">
                <div className="font-semibold">Take Photos</div>
                <div className="text-sm text-muted-foreground">Upload up to 3 photos</div>
              </div>
            </button>
          </div>
        ) : method === "online" ? (
          <div className="space-y-4">
            <div>
              <Input
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="mb-4"
              />
            </div>

            <div className="max-h-[60vh] overflow-y-auto">
              <div className="grid grid-cols-2 gap-3">
                {mockProducts
                  .filter((product) => product.name.toLowerCase().includes(searchQuery.toLowerCase()))
                  .map((product) => (
                    <button
                      key={product.id}
                      onClick={() => handleAddOnlineItem(product)}
                      className="flex flex-col items-start rounded-xl border-2 border-border p-3 text-left transition-colors hover:border-foreground"
                    >
                      <img
                        src={product.image || "/placeholder.svg"}
                        alt={product.name}
                        className="mb-2 aspect-square w-full rounded-lg object-cover"
                      />
                      <div className="text-sm font-semibold line-clamp-2">{product.name}</div>
                      <div className="text-sm text-muted-foreground">{product.price}</div>
                      <div className="text-xs text-muted-foreground">{product.source}</div>
                    </button>
                  ))}
              </div>
            </div>

            <Button variant="outline" onClick={() => setMethod(null)} className="w-full">
              Back
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Photo Upload Section */}
            <div>
              <Label>Photos (up to 3)</Label>
              <div className="mt-2 grid grid-cols-3 gap-2">
                {uploadedPhotos.map((photo, index) => (
                  <div key={index} className="relative aspect-square">
                    <img
                      src={photo || "/placeholder.svg"}
                      alt={`Upload ${index + 1}`}
                      className="h-full w-full rounded-lg object-cover"
                    />
                    <button
                      onClick={() => removePhoto(index)}
                      className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-foreground text-background"
                    >
                      <X className="h-4 w-4" />
                    </button>
                    <div className="absolute bottom-1 left-1 rounded bg-black/60 px-1.5 py-0.5 text-xs text-white">
                      {index === 0 ? "Front" : index === 1 ? "Back" : "Detail"}
                    </div>
                  </div>
                ))}
                {isProcessingImages && (
                  <div className="flex aspect-square flex-col items-center justify-center rounded-lg border-2 border-dashed border-border">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                    <span className="mt-1 text-xs text-muted-foreground">Processing...</span>
                  </div>
                )}
                {uploadedPhotos.length < 3 && !isProcessingImages && (
                  <label className="flex aspect-square cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border hover:border-foreground transition-colors">
                    <Upload className="h-6 w-6 text-muted-foreground" />
                    <span className="mt-1 text-xs text-muted-foreground">
                      {uploadedPhotos.length === 0 ? "Front" : uploadedPhotos.length === 1 ? "Back" : "Detail"}
                    </span>
                    <input type="file" accept="image/*" className="hidden" onChange={handlePhotoUpload} />
                  </label>
                )}
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Suggested angles: Front view, back view, and detail shot
              </p>
            </div>

            {/* Item Title */}
            <div>
              <Label htmlFor="itemTitle">Item Title</Label>
              <Input
                id="itemTitle"
                placeholder="e.g., Nike Air Force 1"
                value={itemTitle}
                onChange={(e) => setItemTitle(e.target.value)}
                className="mt-1.5"
              />
            </div>

            {/* Metadata Section */}
            <div className="space-y-3">
              <Label>Metadata</Label>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Input placeholder="Size (e.g., M, 32)" value={size} onChange={(e) => setSize(e.target.value)} />
                </div>
                <div>
                  <Input placeholder="Color" value={color} onChange={(e) => setColor(e.target.value)} />
                </div>
              </div>

              <Input placeholder="Brand (optional)" value={brand} onChange={(e) => setBrand(e.target.value)} />

              <Input
                placeholder="Category (e.g., Tops, Shoes)"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </div>

            <div className="flex gap-2 pt-2">
              <Button variant="outline" onClick={() => setMethod(null)} className="flex-1">
                Back
              </Button>
              <Button
                className="flex-1"
                disabled={uploadedPhotos.length === 0 || !itemTitle}
                onClick={handleAddCameraItem}
              >
                Add Item
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
