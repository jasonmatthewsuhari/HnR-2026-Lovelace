"use client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface UsernameStepProps {
  username: string
  onUsernameChange: (username: string) => void
  onNext: () => void
}

export function UsernameStep({ username, onUsernameChange, onNext }: UsernameStepProps) {
  const MAX_LENGTH = 30
  const isValid = username.length >= 3

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Create username</h1>
        <p className="text-muted-foreground">You can change this at any time.</p>
      </div>

      <div className="space-y-2">
        <Input
          type="text"
          value={username}
          onChange={(e) => onUsernameChange(e.target.value.slice(0, MAX_LENGTH))}
          placeholder="lovelacepoop"
          className="h-14 rounded-xl border-2 text-base"
        />
        <p className="text-sm text-muted-foreground">
          {username.length}/{MAX_LENGTH}
        </p>
      </div>

      <Button
        onClick={onNext}
        disabled={!isValid}
        className="h-14 w-full rounded-full text-base font-medium"
        variant={isValid ? "default" : "secondary"}
      >
        Next
      </Button>
    </div>
  )
}
