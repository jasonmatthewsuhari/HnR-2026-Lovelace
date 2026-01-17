"use client"

import { useState } from "react"
import { AddClothingModal, type ClothingItem } from "@/components/app/add-clothing-modal"

export default function AddPage({ onNavigateHome }: { onNavigateHome?: () => void }) {
  const [showAddClothingModal, setShowAddClothingModal] = useState(true)

  const handleAddClothingItem = (item: ClothingItem) => {
    const saved = localStorage.getItem("lovelace-clothing")
    const existing = saved ? JSON.parse(saved) : []
    localStorage.setItem("lovelace-clothing", JSON.stringify([...existing, item]))
  }

  const handleClose = () => {
    setShowAddClothingModal(false)
    onNavigateHome?.()
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <AddClothingModal isOpen={showAddClothingModal} onClose={handleClose} onAddItem={handleAddClothingItem} />
    </div>
  )
}

export { AddPage }
