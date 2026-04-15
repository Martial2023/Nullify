"use client"

import { Component, type ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { AlertTriangle } from "lucide-react"

export function ErrorFallback({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <AlertTriangle className="size-10 text-destructive" strokeWidth={1.5} />
      <h3 className="text-lg font-medium">Une erreur est survenue</h3>
      <p className="max-w-sm text-sm text-muted-foreground">
        {error.message || "Erreur inattendue"}
      </p>
      <Button variant="outline" size="sm" onClick={reset}>
        Réessayer
      </Button>
    </div>
  )
}

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  reset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) return this.props.fallback
      return <ErrorFallback error={this.state.error} reset={this.reset} />
    }
    return this.props.children
  }
}
