import React, { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
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
      setSuccess("Account created! Redirecting to login...")
      setTimeout(() => {
        navigate("/login")
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
    <div className="flex min-h-screen w-full bg-background">
      {/* Left Branding Panel */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-primary/10 via-background to-violet-500/10 items-center justify-center">
        <div className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />
        <div className="absolute -top-20 -right-20 h-64 w-64 rounded-full bg-primary/20 blur-[100px]" />
        <div className="absolute bottom-20 left-20 h-64 w-64 rounded-full bg-blue-500/20 blur-[100px]" />

        <div className="relative z-10 max-w-md px-12 text-center">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary to-violet-400 text-white shadow-premium">
            <Sparkles className="h-8 w-8" />
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight">
            NEXOVA <span className="bg-gradient-to-r from-primary to-violet-400 bg-clip-text text-transparent">Real Estate</span>
          </h1>
          <p className="mt-4 text-muted-foreground leading-relaxed">
            AI Employees built for Property Developers, Brokers, and Agencies.
          </p>
          <div className="mt-8 flex flex-col items-center gap-3 text-xs text-muted-foreground">
            {[
              "AI-Powered Lead Scoring",
              "Smart Project Broadcasting",
              "Real-Time Analytics",
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="flex h-4 w-4 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Check className="h-2.5 w-2.5" />
                </div>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Form Panel */}
      <div className="flex w-full items-center justify-center px-6 py-12 lg:w-1/2">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-8 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-primary to-violet-400 text-white shadow-premium">
              <Sparkles className="h-6 w-6" />
            </div>
            <h1 className="text-2xl font-bold">NEXOVA Real Estate</h1>
          </div>

          <div className="rounded-2xl border border-border bg-card p-8 shadow-premium relative overflow-hidden">
            <div className="absolute -right-10 -bottom-10 h-32 w-32 rounded-full bg-primary/5 blur-2xl" />
            <div className="absolute -left-10 -top-10 h-32 w-32 rounded-full bg-violet-500/5 blur-2xl" />

            <div className="relative z-10">
              <h2 className="text-2xl font-bold text-foreground">Create Workspace</h2>
              <p className="mt-1 text-sm text-muted-foreground">Set up your organization</p>

              {error && (
                <div className="mt-6 rounded-lg bg-destructive/10 p-3 text-sm font-medium text-destructive">
                  {error}
                </div>
              )}
              {success && (
                <div className="mt-6 rounded-lg bg-emerald-500/10 p-3 text-sm font-medium text-emerald-500">
                  {success}
                </div>
              )}

              <form onSubmit={handleSubmit} className="mt-6 space-y-4">
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
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
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
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Organization Name
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <Building className="h-4 w-4" />
                    </span>
                    <input
                      type="text"
                      required
                      name="organization_name"
                      value={formData.organization_name}
                      onChange={handleChange}
                      placeholder="Apex Realty Group"
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2 pl-10 pr-4 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Username
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <User className="h-4 w-4" />
                    </span>
                    <input
                      type="text"
                      required
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      placeholder="john_doe"
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2 pl-10 pr-4 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Email Address
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <Mail className="h-4 w-4" />
                    </span>
                    <input
                      type="email"
                      required
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="john@example.com"
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2 pl-10 pr-4 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <Lock className="h-4 w-4" />
                    </span>
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="••••••••"
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2 pl-10 pr-10 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 flex items-center pr-3 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-primary to-violet-500 py-2.5 text-sm font-bold text-primary-foreground shadow-premium hover:shadow-premiumDark transition-all disabled:opacity-50"
                >
                  {isLoading ? "Creating Workspace..." : "Register Workspace"}
                  {!isLoading && <ArrowRight className="h-4 w-4" />}
                </button>
              </form>

              <p className="mt-6 text-center text-xs text-muted-foreground">
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
