import React, { useState } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { ShieldCheck, ArrowRight, RefreshCw } from "lucide-react"
import axios from "axios"
import useAuthStore from "../store/authStore"

export default function OTPVerify() {
  const [searchParams] = useSearchParams()
  const email = searchParams.get("email") || ""
  const [otpCode, setOtpCode] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isResending, setIsResending] = useState(false)

  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setSuccess("")
    setIsLoading(true)

    try {
      const response = await axios.post("/api/auth/verify-otp/", {
        email,
        otp_code: otpCode,
      })
      const result = response.data.data
      login(result.access, result.refresh, result.user)
      setSuccess("Email verified and login successful! Redirecting...")
      setTimeout(() => {
        navigate("/dashboard")
      }, 1500)
    } catch (err) {
      setError(
        err.response?.data?.otp_code || 
        err.response?.data?.message || 
        "Verification failed. Please check the code and try again."
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleResend = async () => {
    setError("")
    setSuccess("")
    setIsResending(true)

    try {
      await axios.post("/api/auth/resend-otp/", { email })
      setSuccess("A new verification code has been sent to your email.")
    } catch (err) {
      setError(
        err.response?.data?.email || 
        err.response?.data?.message || 
        "Failed to resend verification code. Please try again."
      )
    } finally {
      setIsResending(false)
    }
  }

  return (
    <div className="flex min-h-screen w-full bg-background items-center justify-center px-6 py-12">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-border bg-card p-8 shadow-premium relative overflow-hidden">
          <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-primary/5 blur-2xl" />
          <div className="absolute -left-10 -bottom-10 h-32 w-32 rounded-full bg-violet-500/5 blur-2xl" />

          <div className="relative z-10 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-primary to-violet-400 text-white shadow-premium">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <h2 className="text-2xl font-bold text-foreground">Verify Your Email</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              We've sent a 6-digit verification code to <span className="font-semibold text-foreground">{email}</span>
            </p>

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

            <form onSubmit={handleSubmit} className="mt-6 space-y-5">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground text-left mb-1.5">
                  Verification Code
                </label>
                <input
                  type="text"
                  required
                  maxLength={6}
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ""))}
                  placeholder="123456"
                  className="block w-full text-center tracking-[1.2em] text-lg font-bold rounded-lg border border-border bg-muted/40 py-3 pr-4 text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || otpCode.length !== 6}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-primary to-violet-500 py-2.5 text-sm font-bold text-primary-foreground shadow-premium hover:shadow-premiumDark transition-all disabled:opacity-50"
              >
                {isLoading ? "Verifying..." : "Verify Code"}
                {!isLoading && <ArrowRight className="h-4 w-4" />}
              </button>
            </form>

            <div className="mt-6 flex items-center justify-center gap-2">
              <span className="text-xs text-muted-foreground">Didn't receive the code?</span>
              <button
                type="button"
                onClick={handleResend}
                disabled={isResending}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-primary hover:underline disabled:opacity-50"
              >
                <RefreshCw className={`h-3 w-3 ${isResending ? "animate-spin" : ""}`} />
                {isResending ? "Resending..." : "Resend OTP"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
