import React, { useState, useEffect } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { Sparkles, Eye, EyeOff, Lock, User, Mail, Building, ArrowRight, Check } from "lucide-react"
import axios from "axios"

export default function Register() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    organization_name: "",
  })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  useEffect(() => {
    const errorParam = searchParams.get("error")
    if (errorParam === "oauth_failed") {
      setError("Google authentication failed. Please try again.")
    } else if (errorParam === "oauth_cancelled") {
      setError("Google authentication was cancelled.")
    } else if (errorParam === "oauth_not_configured") {
      setError("Google OAuth is not configured on the server.")
    }
  }, [searchParams])

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setSuccess("")
    setIsLoading(true)

    try {
      await axios.post("/api/auth/register/", formData)
      setSuccess("Account created! Redirecting to OTP verification...")
      setTimeout(() => {
        navigate(`/verify-otp?email=${encodeURIComponent(formData.email)}`)
      }, 2000)
    } catch (err) {
      const data = err.response?.data
      if (data) {
        const errors = Object.keys(data)
          .map((key) => `${key}: ${data[key]}`)
          .join(" | ")
        setError(errors)
      } else {
        setError("Registration failed. Please try again.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen w-full bg-background gradient-bg items-center justify-center p-4 md:p-8">
      {/* Outer Card with Glassmorphism and 3D effects */}
      <div className="flex w-full max-w-5xl rounded-3xl overflow-hidden glass-panel border border-border/80 shadow-premium relative min-h-[600px] transition-all duration-500 hover:rotate-x-1 hover:rotate-y-1 hover:scale-[1.005] hover:shadow-2xl hover:shadow-primary/5">
        <div className="absolute -right-20 -top-20 h-80 w-80 rounded-full bg-primary/10 blur-[120px]" />
        <div className="absolute -left-20 -bottom-20 h-80 w-80 rounded-full bg-amber-500/10 blur-[120px]" />

        {/* Left Branding Panel */}
        <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-card/20 items-center justify-center p-12 border-r border-border/40">
          <div className="absolute inset-0 opacity-[0.02]"
            style={{
              backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
              backgroundSize: '30px 30px',
            }}
          />
          <div className="relative z-10 text-center max-w-sm">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary to-amber-500 text-white shadow-premium hover:rotate-12 transition-transform duration-500">
              <Sparkles className="h-8 w-8" />
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              NEXOVA <span className="bg-gradient-to-r from-primary to-amber-500 bg-clip-text text-transparent">Real Estate</span>
            </h1>
            <p className="mt-4 text-muted-foreground text-sm leading-relaxed">
              Automated AI employees tailored for property developers, agencies, and real estate brokers.
            </p>
            <div className="mt-8 space-y-3.5 text-left text-xs font-semibold text-muted-foreground max-w-xs mx-auto">
              {[
                "AI-Powered Lead Scoring & Matching",
                "Smart Automated Project Broadcasting",
                "Real-Time Analytics & Report Generation",
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                    <Check className="h-3 w-3" />
                  </div>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Form Panel */}
        <div className="flex w-full lg:w-1/2 items-center justify-center px-6 py-10 md:px-12 bg-card/10">
          <div className="w-full max-w-md">
            <div className="lg:hidden mb-6 text-center">
              <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-primary to-amber-500 text-white shadow-premium">
                <Sparkles className="h-5 w-5" />
              </div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">NEXOVA Real Estate</h1>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-foreground">Create Workspace</h2>
              <p className="mt-1 text-xs text-muted-foreground">Set up your brand and get started with NEXOVA AI</p>

              {error && (
                <div className="mt-5 rounded-lg bg-destructive/10 p-3 text-xs font-medium text-destructive border border-destructive/20 max-h-24 overflow-y-auto">
                  {error}
                </div>
              )}
              {success && (
                <div className="mt-5 rounded-lg bg-emerald-500/10 p-3 text-xs font-medium text-emerald-500 border border-emerald-500/20">
                  {success}
                </div>
              )}

              <form onSubmit={handleSubmit} className="mt-5 space-y-3.5">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                      First Name
                    </label>
                    <input
                      type="text"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      placeholder="John"
                      className="block w-full rounded-lg border border-border bg-muted/30 py-2 px-3.5 text-xs text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                      Last Name
                    </label>
                    <input
                      type="text"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      placeholder="Doe"
                      className="block w-full rounded-lg border border-border bg-muted/30 py-2 px-3.5 text-xs text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Organization Name
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <Building className="h-3.5 w-3.5" />
                    </span>
                    <input
                      type="text"
                      required
                      name="organization_name"
                      value={formData.organization_name}
                      onChange={handleChange}
                      placeholder="Apex Realty Group"
                      className="block w-full rounded-lg border border-border bg-muted/30 py-2 pl-9 pr-3 text-xs text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Username
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <User className="h-3.5 w-3.5" />
                    </span>
                    <input
                      type="text"
                      required
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      placeholder="john_doe"
                      className="block w-full rounded-lg border border-border bg-muted/30 py-2 pl-9 pr-3 text-xs text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Email Address
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <Mail className="h-3.5 w-3.5" />
                    </span>
                    <input
                      type="email"
                      required
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="john@example.com"
                      className="block w-full rounded-lg border border-border bg-muted/30 py-2 pl-9 pr-3 text-xs text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <Lock className="h-3.5 w-3.5" />
                    </span>
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="••••••••"
                      className="block w-full rounded-lg border border-border bg-muted/30 py-2 pl-9 pr-9 text-xs text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 flex items-center pr-3 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-primary to-amber-500 py-2.5 text-xs font-bold text-primary-foreground shadow-premium hover:shadow-premiumDark hover:scale-[1.01] active:scale-[0.99] transition-all duration-300 disabled:opacity-50"
                >
                  {isLoading ? "Creating Workspace..." : "Register Workspace"}
                  {!isLoading && <ArrowRight className="h-4 w-4" />}
                </button>

                <div className="relative flex py-1 items-center">
                  <div className="flex-grow border-t border-border"></div>
                  <span className="flex-shrink mx-3 text-[10px] text-muted-foreground uppercase tracking-wider">Or</span>
                  <div className="flex-grow border-t border-border"></div>
                </div>

                <button
                  type="button"
                  onClick={() => window.location.href = "/api/auth/google/login/"}
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-card/40 hover:bg-muted/30 hover:border-primary/50 py-2.5 text-xs font-bold text-foreground transition-all duration-300 hover:scale-[1.01] active:scale-[0.99] shadow-sm hover:shadow-md backdrop-blur-sm"
                >
                  <svg className="h-3.5 w-3.5 mr-1" viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
                    <g transform="matrix(1, 0, 0, 1, 0, 0)">
                      <path d="M21.35,11.1H12v2.7h5.38c-0.24,1.28 -0.96,2.37 -2.04,3.1v2.6h3.29c1.92,-1.78 3.02,-4.4 3.02,-7.4C21.65,11.83 21.54,11.45 21.35,11.1z" fill="#4285F4" />
                      <path d="M12,20.5c2.3,0 4.23,-0.76 5.64,-2.07l-3.29,-2.6c-0.91,0.61 -2.08,0.98 -3.35,0.98 -2.57,0 -4.75,-1.74 -5.53,-4.07H2.07v2.69C3.56,18.3 7.49,20.5 12,20.5z" fill="#34A853" />
                      <path d="M6.47,12.74c-0.2,-0.61 -0.31,-1.26 -0.31,-1.93s0.11,-1.33 0.31,-1.93V6.23H2.07c-0.67,1.34 -1.07,2.85 -1.07,4.58s0.4,3.24 1.07,4.58L6.47,12.74z" fill="#FBBC05" />
                      <path d="M12,5.19c1.25,0 2.37,0.43 3.25,1.27l2.44,-2.44C16.22,2.6 14.29,1.75 12,1.75c-4.51,0 -8.44,2.2 -9.93,5.17l4.4,3.42C7.25,6.93 9.43,5.19 12,5.19z" fill="#EA4335" />
                    </g>
                  </svg>
                  Sign up with Google
                </button>
              </form>

              <p className="mt-5 text-center text-xs text-muted-foreground">
                Already have an account?{" "}
                <Link to="/login" className="font-semibold text-primary hover:underline">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
