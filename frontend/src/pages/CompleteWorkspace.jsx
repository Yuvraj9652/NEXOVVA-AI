import React, { useState, useEffect } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { Building2, ArrowRight, Loader2 } from "lucide-react"
import axios from "axios"
import useAuthStore from "../store/authStore"

export default function CompleteWorkspace() {
  const [orgName, setOrgName] = useState("")
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)

  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const access = searchParams.get("access")
  const refresh = searchParams.get("refresh")
  const login = useAuthStore((state) => state.login)

  useEffect(() => {
    if (!access || !refresh) {
      setError("Session expired or invalid authentication parameters.")
      setTimeout(() => navigate("/login"), 3000)
    }
  }, [access, refresh, navigate])

  const steps = [
    "Setting up your workspace...",
    "Creating organization profile...",
    "Seeding database with default templates...",
    "Generating realistic property inventories...",
    "Finalizing your secure admin panel..."
  ]

  useEffect(() => {
    let interval
    if (isLoading) {
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev))
      }, 2500)
    }
    return () => clearInterval(interval)
  }, [isLoading])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!orgName.trim()) {
      setError("Organization name is required.")
      return
    }
    setError("")
    setIsLoading(true)
    setLoadingStep(0)

    try {
      const response = await axios.post(
        "/api/auth/google/onboarding/",
        { organization_name: orgName.trim() },
        {
          headers: {
            Authorization: `Bearer ${access}`,
          },
        }
      )

      const result = response.data.data
      
      // Store in auth store
      login(result.access, result.refresh, result.user)
      
      // Redirect to dashboard
      navigate("/dashboard")
    } catch (err) {
      setError(
        err.response?.data?.message ||
        err.response?.data?.detail ||
        "Failed to initialize organization. Please try again."
      )
      setIsLoading(false)
    }
  }

  if (!access || !refresh) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background text-foreground">
        <div className="flex flex-col items-center gap-4 text-center p-6">
          <p className="text-sm font-semibold text-destructive">{error || "Redirecting to login..."}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen w-full bg-background gradient-bg items-center justify-center p-4">
      {/* Decorative background elements */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: '40px 40px',
        }}
      />
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-amber-500/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative w-full max-w-md">
        {/* Logo/Icon */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary to-amber-500 text-white shadow-lg shadow-primary/20 mb-3">
            <Building2 className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-foreground to-foreground/75 bg-clip-text text-transparent">
            Setup Your Workspace
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5 text-center">
            You're just one step away from launching your NEXOVA AI real estate platform.
          </p>
        </div>

        {/* Form Card */}
        <div className="rounded-2xl border border-border/40 bg-card/60 p-8 backdrop-blur-xl shadow-2xl relative overflow-hidden">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
              <h3 className="text-sm font-semibold tracking-wide text-foreground">
                Configuring Environment
              </h3>
              <p className="text-xs text-muted-foreground mt-2 max-w-[280px]">
                {steps[loadingStep]}
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="orgName" className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                  Organization / Workspace Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground/60">
                    <Building2 className="h-4 w-4" />
                  </div>
                  <input
                    id="orgName"
                    type="text"
                    required
                    value={orgName}
                    onChange={(e) => setOrgName(e.target.value)}
                    placeholder="e.g. Acme Realty"
                    className="block w-full rounded-xl border border-border bg-background/50 pl-10 pr-3 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary placeholder:text-muted-foreground/45"
                  />
                </div>
              </div>

              {error && (
                <div className="rounded-xl border border-destructive/20 bg-destructive/10 p-3 text-xs text-destructive">
                  {error}
                </div>
              )}

              <button
                type="submit"
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-primary to-amber-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/20 hover:opacity-95 transition-opacity"
              >
                <span>Launch Platform</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
