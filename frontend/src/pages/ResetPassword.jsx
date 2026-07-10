import React, { useState, useEffect } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { Sparkles, Key, Lock, Eye, EyeOff, ArrowRight, ArrowLeft } from "lucide-react"
import axios from "axios"

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const [email, setEmail] = useState("")
  const [otpCode, setOtpCode] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const navigate = useNavigate()

  useEffect(() => {
    const emailParam = searchParams.get("email")
    if (emailParam) {
      setEmail(emailParam)
    }
  }, [searchParams])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setSuccess("")

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.")
      return
    }

    setIsLoading(true)

    try {
      await axios.post("/api/auth/reset-password/", {
        email,
        otp_code: otpCode,
        new_password: newPassword,
        confirm_new_password: confirmPassword,
      })
      setSuccess("Password has been reset successfully! Redirecting to login...")
      setTimeout(() => {
        navigate("/login")
      }, 2500)
    } catch (err) {
      const data = err.response?.data
      setError(
        data?.otp_code?.[0] ||
        data?.new_password?.[0] ||
        data?.confirm_new_password?.[0] ||
        data?.detail ||
        "Failed to reset password. Please verify the code and try again."
      )
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
        <div className="absolute -top-20 -left-20 h-64 w-64 rounded-full bg-primary/20 blur-[100px]" />
        <div className="absolute bottom-20 right-20 h-64 w-64 rounded-full bg-violet-500/20 blur-[100px]" />

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
        </div>
      </div>

      {/* Right Form Panel */}
      <div className="flex w-full items-center justify-center px-6 py-12 lg:w-1/2">
        <div className="w-full max-w-md">
          <div className="rounded-2xl border border-border bg-card p-8 shadow-premium relative overflow-hidden">
            <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-primary/5 blur-2xl" />
            <div className="absolute -left-10 -bottom-10 h-32 w-32 rounded-full bg-violet-500/5 blur-2xl" />

            <div className="relative z-10">
              <h2 className="text-2xl font-bold text-foreground">Reset Password</h2>
              <p className="mt-1 text-sm text-muted-foreground">Enter the 6-digit OTP code sent to your email along with your new password.</p>

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
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="john@example.com"
                    className="block w-full rounded-lg border border-border bg-muted/40 py-2.5 px-4 text-sm text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                    6-Digit Reset OTP Code
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <Key className="h-4 w-4" />
                    </span>
                    <input
                      type="text"
                      required
                      maxLength={6}
                      value={otpCode}
                      onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ""))}
                      placeholder="123456"
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2.5 pl-10 pr-4 text-sm font-semibold tracking-[0.3em] text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all text-center"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                    New Password
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <Lock className="h-4 w-4" />
                    </span>
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="••••••••"
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2.5 pl-10 pr-10 text-sm text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
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

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                    Confirm New Password
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                      <Lock className="h-4 w-4" />
                    </span>
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2.5 pl-10 pr-10 text-sm text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-primary to-violet-500 py-2.5 text-sm font-bold text-primary-foreground shadow-premium hover:shadow-premiumDark transition-all disabled:opacity-50 mt-2"
                >
                  {isLoading ? "Resetting..." : "Reset Password"}
                  <ArrowRight className="h-4 w-4" />
                </button>
              </form>

              <div className="mt-6 text-center">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 text-xs font-semibold text-muted-foreground hover:text-foreground transition-all"
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  Back to Login
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
