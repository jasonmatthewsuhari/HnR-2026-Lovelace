"use client"

import { useState, useEffect } from "react"
import { Plus, X, Trash2, ZoomIn, Filter, Loader2, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { AddClothingModal, type ClothingItem } from "@/components/app/add-clothing-modal"
import { useAuth } from "@/hooks/use-auth"
import { getUserClothing, deleteClothingItem, type ClothingItem as APIClothingItem } from "@/lib/api"

export default function ProfilePage() {
  const { user, logout } = useAuth()
  const [activeTab, setActiveTab] = useState<"clothes" | "outfits" | "collections">("clothes")
  const [showCreateOutfitModal, setShowCreateOutfitModal] = useState(false)
  const [showCreateCollectionModal, setShowCreateCollectionModal] = useState(false)
  const [showAddClothingModal, setShowAddClothingModal] = useState(false)
  const [selectedClothingItem, setSelectedClothingItem] = useState<APIClothingItem | null>(null)
  const [clothingFilter, setClothingFilter] = useState<string>("all")
  const [outfitCreationFilter, setOutfitCreationFilter] = useState<string>("all")
  const [isLoadingClothing, setIsLoadingClothing] = useState(false)

  const [showEditProfileModal, setShowEditProfileModal] = useState(false)
  const [userProfile, setUserProfile] = useState({
    firstName: "Jason",
    lastName: "Matthew",
    username: "lovelacepoopi",
  })

  const [clothingItems, setClothingItems] = useState<APIClothingItem[]>([])

  useEffect(() => {
    const savedProfile = localStorage.getItem("lovelace-user-profile")
    if (savedProfile) {
      const profile = JSON.parse(savedProfile)
      setUserProfile({
        firstName: profile.firstName || "Jason",
        lastName: profile.lastName || "Matthew",
        username: profile.username || "lovelacepoopi",
      })
    }
  }, [])

  // Load clothing items from Firebase
  useEffect(() => {
    const loadClothingItems = async () => {
      if (!user) return

      setIsLoadingClothing(true)
      try {
        const result = await getUserClothing(user.uid)
        setClothingItems(result.items)
      } catch (error) {
        console.error("Failed to load clothing items:", error)
        setClothingItems([])
      } finally {
        setIsLoadingClothing(false)
      }
    }

    loadClothingItems()
  }, [user])

  const handleAddClothingItem = (item: APIClothingItem) => {
    setClothingItems((prev) => [...prev, item])
  }

  const handleDeleteClothingItem = async (id: string) => {
    try {
      await deleteClothingItem(id)
      setClothingItems((prev) => prev.filter((item) => item.id !== id))
      setSelectedClothingItem(null)
    } catch (error) {
      console.error("Failed to delete clothing item:", error)
      alert("Failed to delete item. Please try again.")
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
      // Redirect will be handled by useAuth hook
    } catch (error) {
      console.error("Failed to logout:", error)
      alert("Failed to logout. Please try again.")
    }
  }

  const categories = ["all", ...Array.from(new Set(clothingItems.map((item) => item.category).filter(Boolean)))]

  const filteredClothingItems =
    clothingFilter === "all" ? clothingItems : clothingItems.filter((item) => item.category === clothingFilter)

  const filteredOutfitClothingItems =
    outfitCreationFilter === "all"
      ? clothingItems
      : clothingItems.filter((item) => item.category === outfitCreationFilter)

  const hasClothes = clothingItems.length > 0
  const hasOutfits = false

  return (
    <div className="mx-auto min-h-screen max-w-2xl">
      {/* Header */}
      <header className="flex items-center justify-between p-4">
        <h1 className="text-2xl font-bold">{userProfile.username}</h1>
        <Button
          variant="outline"
          size="sm"
          onClick={handleLogout}
          className="gap-2"
        >
          <LogOut className="h-4 w-4" />
          Log out
        </Button>
      </header>

      {/* Profile Info */}
      <div className="px-4 pb-6">
        <div className="flex items-start gap-4">
          <div className="relative">
            <img
              src="/placeholder.svg?height=80&width=80"
              alt="Profile"
              className="h-20 w-20 rounded-full object-cover"
            />
            <button className="absolute bottom-0 right-0 flex h-7 w-7 items-center justify-center rounded-full bg-foreground text-background">
              <Plus className="h-4 w-4" strokeWidth={3} />
            </button>
          </div>

          <div className="flex-1">
            <h2 className="mb-2 text-xl font-bold">
              {userProfile.firstName} {userProfile.lastName}
            </h2>
            <div className="flex gap-6 text-sm">
              <div>
                <div className="font-bold">0</div>
                <div className="text-muted-foreground">Followers</div>
              </div>
              <div>
                <div className="font-bold">0</div>
                <div className="text-muted-foreground">Following</div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 flex gap-3">
          <Button variant="secondary" className="flex-1" onClick={() => setShowEditProfileModal(true)}>
            Edit profile
          </Button>
          <Button variant="secondary" className="flex-1">
            Share profile
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border">
        <div className="flex">
          <button
            onClick={() => setActiveTab("clothes")}
            className={`flex-1 border-b-2 py-3 text-sm font-medium ${
              activeTab === "clothes" ? "border-foreground text-foreground" : "border-transparent text-muted-foreground"
            }`}
          >
            Clothes
          </button>
          <button
            onClick={() => setActiveTab("outfits")}
            className={`flex-1 border-b-2 py-3 text-sm font-medium ${
              activeTab === "outfits" ? "border-foreground text-foreground" : "border-transparent text-muted-foreground"
            }`}
          >
            Outfits
          </button>
          <button
            onClick={() => setActiveTab("collections")}
            className={`flex-1 border-b-2 py-3 text-sm font-medium ${
              activeTab === "collections"
                ? "border-foreground text-foreground"
                : "border-transparent text-muted-foreground"
            }`}
          >
            Collections
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-4">
        {activeTab === "clothes" && (
          <>
            {isLoadingClothing ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground mb-4" />
                <p className="text-sm text-muted-foreground">Loading your wardrobe...</p>
              </div>
            ) : hasClothes ? (
              <>
                <div className="mb-4 flex items-center gap-2">
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  <select
                    value={clothingFilter}
                    onChange={(e) => setClothingFilter(e.target.value)}
                    className="rounded-lg border border-border bg-background px-3 py-1.5 text-sm"
                  >
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat.charAt(0).toUpperCase() + cat.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {filteredClothingItems.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => setSelectedClothingItem(item)}
                      className="group relative flex cursor-pointer flex-col overflow-hidden rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-xl"
                    >
                      <div className="relative aspect-square overflow-hidden rounded-xl">
                        <img
                          src={item.images[0] || "/placeholder.svg"}
                          alt={item.name}
                          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
                        />
                        <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                          <ZoomIn className="h-8 w-8 text-white" />
                        </div>
                      </div>
                      <div className="mt-2 rounded-xl bg-background p-2 transition-all duration-300 group-hover:bg-secondary group-hover:shadow-md">
                        <div className="text-sm font-semibold group-hover:line-clamp-none line-clamp-2">
                          {item.name}
                        </div>
                        {item.price && (
                          <div className="text-sm text-muted-foreground group-hover:line-clamp-none line-clamp-1">
                            {item.price}
                          </div>
                        )}
                        {item.size && (
                          <div className="text-xs text-muted-foreground group-hover:line-clamp-none line-clamp-1">
                            Size: {item.size}
                          </div>
                        )}
                        {item.color && (
                          <div className="text-xs text-muted-foreground group-hover:line-clamp-none line-clamp-1">
                            Color: {item.color}
                          </div>
                        )}
                        {item.brand && (
                          <div className="text-xs text-muted-foreground group-hover:line-clamp-none line-clamp-1">
                            Brand: {item.brand}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="mb-6 flex gap-2">
                  <img src="/placeholder.svg?height=120&width=90" alt="Bag" className="h-32 w-24 object-contain" />
                  <img src="/placeholder.svg?height=160&width=100" alt="Coat" className="h-40 w-28 object-contain" />
                  <img src="/placeholder.svg?height=140&width=95" alt="Blazer" className="h-36 w-26 object-contain" />
                </div>
                <div className="mb-2 flex gap-2">
                  <img src="/placeholder.svg?height=80&width=120" alt="Shoes" className="h-20 w-32 object-contain" />
                </div>
                <h3 className="mb-2 text-center text-lg font-bold">Your clothes will appear here</h3>
                <p className="mb-6 text-center text-sm text-muted-foreground">
                  {user ? "Start adding some clothes." : "Please log in to view your wardrobe."}
                </p>
                {user && (
                  <Button className="rounded-full px-8" onClick={() => setShowAddClothingModal(true)}>
                    Add clothes
                  </Button>
                )}
              </div>
            )}

            {hasClothes && user && (
              <div className="fixed bottom-24 right-6">
                <button
                  onClick={() => setShowAddClothingModal(true)}
                  className="flex h-14 w-14 items-center justify-center rounded-full bg-foreground text-background shadow-lg"
                >
                  <Plus className="h-6 w-6" />
                </button>
              </div>
            )}
          </>
        )}

        {activeTab === "outfits" && (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="relative mb-6">
              <img
                src="/placeholder.svg?height=200&width=120"
                alt="Outfit 1"
                className="absolute left-0 top-0 h-52 w-32 -rotate-12 rounded-2xl object-cover shadow-lg"
              />
              <img
                src="/placeholder.svg?height=200&width=120"
                alt="Outfit 2"
                className="relative z-10 h-52 w-32 rounded-2xl object-cover shadow-lg"
              />
              <img
                src="/placeholder.svg?height=200&width=120"
                alt="Outfit 3"
                className="absolute right-0 top-0 h-52 w-32 rotate-12 rounded-2xl object-cover shadow-lg"
              />
            </div>
            <h3 className="mb-2 text-center text-lg font-bold">Start adding outfits</h3>
            <p className="mb-6 text-center text-sm text-muted-foreground">
              Your outfits will appear here. Create collages or add outfit selfies.
            </p>
            <Button className="rounded-full px-8" onClick={() => setShowCreateOutfitModal(true)}>
              Create outfit
            </Button>
          </div>
        )}

        {activeTab === "collections" && (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col">
                <div className="mb-3 flex aspect-square items-center justify-center rounded-3xl bg-secondary">
                  <svg
                    className="h-20 w-20 text-muted-foreground/40"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  >
                    <path d="M12 2L2 7l10 5 10-5-10-5z" />
                    <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
                    <circle cx="18" cy="16" r="3" />
                    <path d="M18 15v2M17 16h2" />
                  </svg>
                </div>
                <h4 className="mb-1 font-semibold">First</h4>
                <p className="flex items-center gap-1 text-sm text-muted-foreground">
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                  </svg>
                  Wishlist
                </p>
              </div>

              <div className="flex flex-col">
                <div className="mb-3 flex aspect-square items-center justify-center rounded-3xl bg-secondary">
                  <svg
                    className="h-20 w-20 text-muted-foreground/40"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  >
                    <path d="M12 2L2 7l10 5 10-5-10-5z" />
                    <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
                    <circle cx="18" cy="16" r="3" />
                    <path d="M18 15v2M17 16h2" />
                  </svg>
                </div>
                <h4 className="mb-1 font-semibold">My Wishlist</h4>
                <p className="flex items-center gap-1 text-sm text-muted-foreground">
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                  </svg>
                  Wishlist
                </p>
              </div>
            </div>

            <div className="fixed bottom-24 right-6 flex flex-col gap-3">
              <button className="flex h-14 w-14 items-center justify-center rounded-full bg-accent shadow-lg">
                <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
                  <polyline points="16 6 12 2 8 6" />
                  <line x1="12" y1="2" x2="12" y2="15" />
                </svg>
              </button>
              <button className="flex h-14 w-14 items-center justify-center rounded-full bg-accent shadow-lg">
                <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
              </button>
            </div>

            <div className="fixed bottom-24 left-1/2 -translate-x-1/2">
              <Button className="rounded-full px-6 shadow-lg" onClick={() => setShowCreateCollectionModal(true)}>
                <Plus className="mr-2 h-5 w-5" />
                Create new collection
              </Button>
            </div>
          </>
        )}
      </div>

      {selectedClothingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setSelectedClothingItem(null)} />
          <div className="relative z-10 mx-4 w-full max-w-md max-h-[90vh] overflow-y-auto rounded-3xl bg-background p-6 shadow-xl">
            <button
              onClick={() => setSelectedClothingItem(null)}
              className="absolute right-4 top-4 z-10 rounded-full p-2 hover:bg-secondary"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="space-y-4">
              <div className="aspect-square w-full overflow-hidden rounded-2xl">
                <img
                  src={selectedClothingItem.images[0] || "/placeholder.svg"}
                  alt={selectedClothingItem.name}
                  className="h-full w-full object-cover"
                />
              </div>

              <div className="space-y-2">
                <h2 className="text-2xl font-bold">{selectedClothingItem.name}</h2>
                {selectedClothingItem.price && (
                  <p className="text-xl font-semibold text-muted-foreground">{selectedClothingItem.price}</p>
                )}
                {selectedClothingItem.source && (
                  <p className="text-sm text-muted-foreground">Source: {selectedClothingItem.source}</p>
                )}
                {selectedClothingItem.brand && (
                  <p className="text-sm">
                    <span className="font-semibold">Brand:</span> {selectedClothingItem.brand}
                  </p>
                )}
                {selectedClothingItem.size && (
                  <p className="text-sm">
                    <span className="font-semibold">Size:</span> {selectedClothingItem.size}
                  </p>
                )}
                {selectedClothingItem.color && (
                  <p className="text-sm">
                    <span className="font-semibold">Color:</span> {selectedClothingItem.color}
                  </p>
                )}
                {selectedClothingItem.category && (
                  <p className="text-sm">
                    <span className="font-semibold">Category:</span> {selectedClothingItem.category}
                  </p>
                )}
              </div>

              <Button
                variant="destructive"
                className="w-full"
                onClick={() => handleDeleteClothingItem(selectedClothingItem.id)}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Item
              </Button>
            </div>
          </div>
        </div>
      )}

      {showCreateOutfitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowCreateOutfitModal(false)} />
          <div className="relative z-10 mx-4 w-full max-w-md max-h-[90vh] overflow-y-auto rounded-3xl bg-background p-6 shadow-xl">
            <button
              onClick={() => setShowCreateOutfitModal(false)}
              className="absolute right-4 top-4 rounded-full p-2 hover:bg-secondary"
            >
              <X className="h-5 w-5" />
            </button>

            <h2 className="mb-6 text-xl font-bold">Create Outfit</h2>

            {hasClothes ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  <select
                    value={outfitCreationFilter}
                    onChange={(e) => setOutfitCreationFilter(e.target.value)}
                    className="flex-1 rounded-lg border border-border bg-background px-3 py-1.5 text-sm"
                  >
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat.charAt(0).toUpperCase() + cat.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <p className="text-sm text-muted-foreground">Select clothes to add to your outfit:</p>
                <div className="grid grid-cols-3 gap-3">
                  {filteredOutfitClothingItems.map((item) => (
                    <button
                      key={item.id}
                      className="aspect-square rounded-xl border-2 border-border hover:border-foreground transition-colors"
                    >
                      <img
                        src={item.images[0] || "/placeholder.svg"}
                        alt={item.name}
                        className="h-full w-full rounded-xl object-cover"
                      />
                    </button>
                  ))}
                </div>
                <Button className="w-full rounded-full">Create Outfit</Button>
              </div>
            ) : (
              <div className="flex flex-col items-center py-8">
                <div className="mb-6 flex gap-2">
                  <img src="/placeholder.svg?height=120&width=90" alt="Bag" className="h-32 w-24 object-contain" />
                  <img src="/placeholder.svg?height=160&width=100" alt="Coat" className="h-40 w-28 object-contain" />
                  <img src="/placeholder.svg?height=140&width=95" alt="Blazer" className="h-36 w-26 object-contain" />
                </div>
                <div className="mb-2 flex gap-2">
                  <img src="/placeholder.svg?height=80&width=120" alt="Shoes" className="h-20 w-32 object-contain" />
                </div>
                <h3 className="mb-2 text-center text-lg font-bold">Your clothes will appear here</h3>
                <p className="text-center text-sm text-muted-foreground">Start adding some clothes.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {showCreateCollectionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowCreateCollectionModal(false)} />
          <div className="relative z-10 mx-4 w-full max-w-md rounded-3xl bg-background p-6 shadow-xl">
            <button
              onClick={() => setShowCreateCollectionModal(false)}
              className="absolute right-4 top-4 rounded-full p-2 hover:bg-secondary"
            >
              <X className="h-5 w-5" />
            </button>

            <h2 className="mb-6 text-xl font-bold">Create Collection</h2>

            {hasOutfits ? (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">Select outfits to add to your collection:</p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="aspect-[3/4] rounded-xl bg-secondary" />
                  <div className="aspect-[3/4] rounded-xl bg-secondary" />
                </div>
                <Button className="w-full rounded-full">Create Collection</Button>
              </div>
            ) : (
              <div className="flex flex-col items-center py-8">
                <div className="relative mb-6">
                  <img
                    src="/placeholder.svg?height=200&width=120"
                    alt="Outfit 1"
                    className="absolute left-0 top-0 h-52 w-32 -rotate-12 rounded-2xl object-cover shadow-lg"
                  />
                  <img
                    src="/placeholder.svg?height=200&width=120"
                    alt="Outfit 2"
                    className="relative z-10 h-52 w-32 rounded-2xl object-cover shadow-lg"
                  />
                  <img
                    src="/placeholder.svg?height=200&width=120"
                    alt="Outfit 3"
                    className="absolute right-0 top-0 h-52 w-32 rotate-12 rounded-2xl object-cover shadow-lg"
                  />
                </div>
                <h3 className="mb-2 text-center text-lg font-bold">Start adding outfits</h3>
                <p className="text-center text-sm text-muted-foreground">
                  Your outfits will appear here. Create collages or add outfit selfies.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {showEditProfileModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowEditProfileModal(false)} />
          <div className="relative z-10 mx-4 w-full max-w-md rounded-3xl bg-background p-6 shadow-xl">
            <button
              onClick={() => setShowEditProfileModal(false)}
              className="absolute right-4 top-4 rounded-full p-2 hover:bg-secondary"
            >
              <X className="h-5 w-5" />
            </button>

            <h2 className="mb-6 text-xl font-bold">Edit Profile</h2>

            <div className="space-y-4">
              <div>
                <label htmlFor="editFirstName" className="mb-2 block text-sm font-medium text-muted-foreground">
                  First name
                </label>
                <input
                  id="editFirstName"
                  type="text"
                  value={userProfile.firstName}
                  onChange={(e) => setUserProfile({ ...userProfile, firstName: e.target.value })}
                  className="w-full rounded-2xl border-2 border-border bg-background px-4 py-3 focus:border-foreground focus:outline-none"
                />
              </div>

              <div>
                <label htmlFor="editLastName" className="mb-2 block text-sm font-medium text-muted-foreground">
                  Last name
                </label>
                <input
                  id="editLastName"
                  type="text"
                  value={userProfile.lastName}
                  onChange={(e) => setUserProfile({ ...userProfile, lastName: e.target.value })}
                  className="w-full rounded-2xl border-2 border-border bg-background px-4 py-3 focus:border-foreground focus:outline-none"
                />
              </div>

              <div>
                <label htmlFor="editUsername" className="mb-2 block text-sm font-medium text-muted-foreground">
                  Username
                </label>
                <input
                  id="editUsername"
                  type="text"
                  value={userProfile.username}
                  onChange={(e) => setUserProfile({ ...userProfile, username: e.target.value })}
                  className="w-full rounded-2xl border-2 border-border bg-background px-4 py-3 focus:border-foreground focus:outline-none"
                />
              </div>

              <Button
                className="w-full"
                onClick={() => {
                  const savedProfile = localStorage.getItem("lovelace-user-profile")
                  if (savedProfile) {
                    const profile = JSON.parse(savedProfile)
                    localStorage.setItem(
                      "lovelace-user-profile",
                      JSON.stringify({
                        ...profile,
                        firstName: userProfile.firstName,
                        lastName: userProfile.lastName,
                        username: userProfile.username,
                      }),
                    )
                  }
                  setShowEditProfileModal(false)
                }}
              >
                Save Changes
              </Button>
            </div>
          </div>
        </div>
      )}

      <AddClothingModal
        isOpen={showAddClothingModal}
        onClose={() => setShowAddClothingModal(false)}
        onAddItem={handleAddClothingItem}
      />
    </div>
  )
}

export { ProfilePage }
