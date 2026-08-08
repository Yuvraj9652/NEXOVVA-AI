import React, { useState, useEffect, useRef } from "react"
import { Lock, Shield, ShieldCheck, ShieldAlert, QrCode, Check, AlertTriangle, Key, ChevronLeft } from "lucide-react"
import api from "../api/client"
import useAuthStore from "../store/authStore"

export default function Settings() {
  const { user } = useAuthStore()
  const settingsRef = useRef(null)

  // Mouse tracking for dashboard cards
  useEffect(() => {
    const boxElements = document.querySelectorAll(".dashboard-card")

    const handleMouseMove = (e) => {
      const element = e.target.closest(".dashboard-card")
      if (element) {
        const rect = element.getBoundingClientRect()
        const x = ((e.clientX - rect.left) / rect.width) * 100
        const y = ((e.clientY - rect.top) / rect.height) * 100
        element.style.setProperty("--mouse-x", `${x}%`)
        element.style.setProperty("--mouse-y", `${y}%`)
        element.style.setProperty("--show-gradient", "1")
      }
    }

    const handleMouseLeave = (e) => {
      const element = e.target.closest(".dashboard-card")
      if (element) {
        element.style.setProperty("--show-gradient", "0")
      }
    }

    boxElements.forEach((el) => {
      el.addEventListener("mousemove", handleMouseMove)
      el.addEventListener("mouseleave", handleMouseLeave)
    })

    return () => {
      boxElements.forEach((el) => {
        el.removeEventListener("mousemove", handleMouseMove)
        el.removeEventListener("mouseleave", handleMouseLeave)
      })
    }
  }, [])

  // Password change state
  const [oldPassword, setOldPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [pwdError, setPwdError] = useState("")
  const [pwdSuccess, setPwdSuccess] = useState("")
  const [isPwdLoading, setIsPwdLoading] = useState(false)

  // MFA states
  const [mfaEnabled, setMfaEnabled] = useState(false)
  const [isMfaLoading, setIsMfaLoading] = useState(true)
  const [mfaSetupData, setMfaSetupData] = useState(null)
  const [totpToken, setTotpToken] = useState("")
  const [mfaError, setMfaError] = useState("")
  const [mfaSuccess, setMfaSuccess] = useState("")
  const [isMfaActionLoading, setIsMfaActionLoading] = useState(false)

  const hasUsablePassword = user?.has_usable_password !== false

  useEffect(() => {
    fetchMfaStatus()
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await api.get("/api/auth/profile/")
      const profile = response.data.data
      if (profile && profile.user) {
        const completeUser = {
          ...profile.user,
          role: profile.role,
          organization: profile.organization,
        }
        useAuthStore.getState().updateUser(completeUser)
      }
    } catch (err) {
      console.error("Failed to fetch user profile", err)
    }
  }

  const fetchMfaStatus = async () => {
    setIsMfaLoading(true)
    try {
      const response = await api.get("/api/auth/mfa/status/")
      setMfaEnabled(response.data.data.mfa_enabled)
    } catch (err) {
      console.error("Failed to fetch MFA status", err)
    } finally {
      setIsMfaLoading(false)
    }
  }

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    setPwdError("")
    setPwdSuccess("")

    if (newPassword !== confirmPassword) {
      setPwdError("New passwords do not match.")
      return
    }

    setIsPwdLoading(true)
    try {
      if (!hasUsablePassword) {
        await api.post("/api/auth/create-password/", {
          new_password: newPassword,
          confirm_password: confirmPassword,
        })
        setPwdSuccess("Password created successfully!")
        useAuthStore.getState().updateUser({
          ...user,
          has_usable_password: true,
        })
      } else {
        await api.post("/api/auth/change-password/", {
          old_password: oldPassword,
          new_password: newPassword,
          confirm_new_password: confirmPassword,
        })
        setPwdSuccess("Password updated successfully!")
      }
      setOldPassword("")
      setNewPassword("")
      setConfirmPassword("")
    } catch (err) {
      const data = err.response?.data
      if (!hasUsablePassword) {
        setPwdError(
          data?.new_password?.[0] ||
          data?.confirm_password?.[0] ||
          data?.non_field_errors?.[0] ||
          data?.detail ||
          "Failed to create password. Please try again."
        )
      } else {
        setPwdError(
          data?.old_password?.[0] ||
          data?.new_password?.[0] ||
          data?.confirm_new_password?.[0] ||
          data?.detail ||
          "Failed to change password. Please verify your current password."
        )
      }
    } finally {
      setIsPwdLoading(false)
    }
  }

  const initiateMfaSetup = async () => {
    setMfaError("")
    setMfaSuccess("")
    setIsMfaActionLoading(true)
    try {
      const response = await api.post("/api/auth/mfa/setup/")
      setMfaSetupData(response.data.data)
    } catch (err) {
      setMfaError(err.response?.data?.message || "Failed to initiate MFA setup.")
    } finally {
      setIsMfaActionLoading(false)
    }
  }

  const confirmMfaSetup = async (e) => {
    e.preventDefault()
    setMfaError("")
    setMfaSuccess("")
    setIsMfaActionLoading(true)

    try {
      await api.post("/api/auth/mfa/verify-setup/", { token: totpToken })
      setMfaSuccess("Multi-Factor Authentication enabled successfully!")
      setMfaEnabled(true)
      setMfaSetupData(null)
      setTotpToken("")
    } catch (err) {
      setMfaError(err.response?.data?.message || "Invalid code. Please try again.")
    } finally {
      setIsMfaActionLoading(false)
    }
  }

  const disableMfa = async (e) => {
    e.preventDefault()
    setMfaError("")
    setMfaSuccess("")
    setIsMfaActionLoading(true)

    try {
      await api.post("/api/auth/mfa/disable/", { token: totpToken })
      setMfaSuccess("Multi-Factor Authentication disabled successfully.")
      setMfaEnabled(false)
      setTotpToken("")
    } catch (err) {
      setMfaError(err.response?.data?.message || "Invalid code. Could not disable MFA.")
    } finally {
      setIsMfaActionLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={settingsRef}>
      {/* Static Background Image */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1920&h=1080&fit=crop"
          alt="Modern Real Estate Building"
          className="w-full h-full object-cover opacity-30"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/60 to-background/80" />
      </div>

      {/* Animated background particles - teal color */}
      <div className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `radial-gradient(circle at center, hsl(180 80% 60%) 1px, transparent 1px)`,
          backgroundSize: '80px 80px',
        }}
      />

      {/* Floating orbs - teal and amber colors */}
      <div className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-teal-400/20 blur-[100px] animate-pulse" />
      <div className="absolute top-1/3 -right-32 h-80 w-80 rounded-full bg-amber-500/15 blur-[100px] animate-pulse" style={{ animationDelay: "1s" }} />
      <div className="absolute bottom-0 left-1/4 h-64 w-64 rounded-full bg-emerald-500/10 blur-[80px] animate-pulse" style={{ animationDelay: "2s" }} />

      {/* Main Settings Content */}
      <div className="relative z-10 mx-auto max-w-7xl px-6 pt-8 pb-16 lg:px-12 space-y-8">
        
        {/* Header */}
        <div className="flex items-center gap-4 animate-fade-in">
          <a
            href="/dashboard"
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-card/60 text-muted-foreground hover:text-foreground hover:bg-muted/40 hover:border-teal-500/30 transition-all duration-300 shadow-sm shrink-0"
            title="Back to Dashboard"
          >
            <ChevronLeft className="h-5 w-5" />
          </a>
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground">
              <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">Settings</span>{" "}
              <span className="text-foreground">&</span>{" "}
              <span className="bg-gradient-to-r from-amber-500 to-emerald-500 bg-clip-text text-transparent">Security</span>
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              Manage your account security, passwords, and multi-factor authentication.
            </p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Change Password Card */}
          <div
            className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
            style={{ animationDelay: "0.1s" }}
          >
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-primary/5 blur-2xl" />
            
            <div className="relative z-10 space-y-4">
              <div className="flex items-center gap-2 border-b border-border pb-3">
                <Lock className="h-5 w-5 text-teal-500" />
                <h2 className="text-lg font-bold text-foreground">
                  {hasUsablePassword ? "Change Password" : "Create Password"}
                </h2>
              </div>

              {pwdError && (
                <div className="rounded-lg bg-destructive/10 p-3 text-sm font-medium text-destructive">
                  {pwdError}
                </div>
              )}

              {pwdSuccess && (
                <div className="rounded-lg bg-emerald-500/10 p-3 text-sm font-medium text-emerald-500">
                  {pwdSuccess}
                </div>
              )}

              <form onSubmit={handlePasswordChange} className="space-y-4">
                {hasUsablePassword && (
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                      Current Password
                    </label>
                    <input
                      type="password"
                      required
                      value={oldPassword}
                      onChange={(e) => setOldPassword(e.target.value)}
                      placeholder="••••••••"
                      className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm text-foreground placeholder-muted-foreground focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all"
                    />
                  </div>
                )}

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                    New Password
                  </label>
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm text-foreground placeholder-muted-foreground focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                    {hasUsablePassword ? "Confirm New Password" : "Confirm Password"}
                  </label>
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm text-foreground placeholder-muted-foreground focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isPwdLoading}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-teal-500 to-amber-600 py-2 text-sm font-bold text-white shadow-premium hover:shadow-premiumDark transition-all disabled:opacity-50"
                >
                  {isPwdLoading 
                    ? (hasUsablePassword ? "Updating..." : "Creating...")
                    : (hasUsablePassword ? "Update Password" : "Create Password")}
                </button>
              </form>
            </div>
          </div>

          {/* MFA / Two-Factor Card */}
          <div
            className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
            style={{ animationDelay: "0.2s" }}
          >
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-amber-500/0 via-amber-500/10 to-amber-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-violet-500/5 blur-2xl" />

            <div className="relative z-10 space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-amber-500" />
                  <h2 className="text-lg font-bold text-foreground">Two-Factor Auth (MFA)</h2>
                </div>
                <div>
                  {isMfaLoading ? (
                    <span className="text-xs text-muted-foreground animate-pulse">Checking status...</span>
                  ) : mfaEnabled ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-xs font-semibold text-emerald-500">
                      <ShieldCheck className="h-3 w-3" /> Enabled
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-2 py-0.5 text-xs font-semibold text-amber-500">
                      <ShieldAlert className="h-3 w-3" /> Disabled
                    </span>
                  )}
                </div>
              </div>

              {mfaError && (
                <div className="rounded-lg bg-destructive/10 p-3 text-sm font-medium text-destructive">
                  {mfaError}
                </div>
              )}

              {mfaSuccess && (
                <div className="rounded-lg bg-emerald-500/10 p-3 text-sm font-medium text-emerald-500">
                  {mfaSuccess}
                </div>
              )}

              {!isMfaLoading && (
                <div className="space-y-4">
                  {/* MFA Disabled state: offer initiation */}
                  {!mfaEnabled && !mfaSetupData && (
                    <div className="space-y-4">
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        Securing your account with Two-Factor Authentication (TOTP) adds an extra layer of defense. In addition to credentials, you'll need to enter a verification code generated by authenticator apps like Google Authenticator.
                      </p>
                      <button
                        onClick={initiateMfaSetup}
                        disabled={isMfaActionLoading}
                        className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-teal-500 to-amber-600 py-2 text-sm font-bold text-white shadow-premium hover:shadow-premiumDark transition-all disabled:opacity-50"
                      >
                        Enable Two-Factor Authentication
                      </button>
                    </div>
                  )}

                  {/* MFA Setup Initiation in progress: display secret & qr code */}
                  {!mfaEnabled && mfaSetupData && (
                    <div className="space-y-4 border border-border/80 rounded-xl p-4 bg-muted/20">
                      <div className="flex flex-col items-center gap-4 text-center">
                        <p className="text-xs text-muted-foreground font-medium">
                          Scan this QR code with Google Authenticator or your preferred TOTP app.
                        </p>
                        
                        <div className="rounded-lg bg-white p-2.5 shadow-premium">
                          <img
                            src={`https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(mfaSetupData.config_url)}`}
                            alt="MFA QR Code"
                            className="h-[180px] w-[180px] select-none"
                          />
                        </div>

                        <div className="w-full text-left space-y-1">
                          <span className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Or input secret manually:</span>
                          <code className="block select-all rounded bg-muted/80 p-2 font-mono text-xs text-center font-bold tracking-wider border border-border">
                            {mfaSetupData.secret}
                          </code>
                        </div>
                      </div>

                      <form onSubmit={confirmMfaSetup} className="space-y-3 pt-2 border-t border-border/60">
                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                            Verify 6-Digit Code
                          </label>
                          <div className="relative">
                            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                              <Key className="h-4 w-4" />
                            </span>
                            <input
                              type="text"
                              required
                              maxLength={6}
                              value={totpToken}
                              onChange={(e) => setTotpToken(e.target.value.replace(/\D/g, ""))}
                              placeholder="123456"
                              className="block w-full rounded-lg border border-border bg-muted/40 py-2 pl-10 pr-4 text-sm text-center font-semibold tracking-[0.2em] focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all"
                            />
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => setMfaSetupData(null)}
                            className="flex-1 rounded-lg border border-border py-2 text-sm font-semibold text-foreground hover:bg-muted transition-all"
                          >
                            Cancel
                          </button>
                          <button
                            type="submit"
                            disabled={isMfaActionLoading || totpToken.length !== 6}
                            className="flex-1 rounded-lg bg-gradient-to-r from-teal-500 to-amber-600 py-2 text-sm font-bold text-white hover:shadow-premiumDark transition-all disabled:opacity-50"
                          >
                            Confirm & Enable
                          </button>
                        </div>
                      </form>
                    </div>
                  )}

                  {/* MFA Enabled state: offer disablement */}
                  {mfaEnabled && (
                    <div className="space-y-4">
                      <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 flex gap-3 items-start">
                        <div className="rounded bg-emerald-500/10 p-1.5 text-emerald-500 shrink-0">
                          <ShieldCheck className="h-5 w-5" />
                        </div>
                        <div className="space-y-1">
                          <h4 className="text-sm font-bold text-emerald-500">MFA is Active</h4>
                          <p className="text-xs text-muted-foreground leading-relaxed">
                            Your account is protected by Google Authenticator. Login attempts will require both credentials and a verification code.
                          </p>
                        </div>
                      </div>

                      <form onSubmit={disableMfa} className="space-y-3 pt-2 border-t border-border">
                        <div className="flex gap-2 items-center text-amber-500 text-xs font-bold uppercase tracking-wider">
                          <AlertTriangle className="h-4 w-4 shrink-0" />
                          <span>Disable Two-Factor Auth</span>
                        </div>
                        
                        <div>
                          <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                            Enter Current Authenticator Code
                          </label>
                          <div className="relative">
                            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                              <Key className="h-4 w-4" />
                            </span>
                            <input
                              type="text"
                              required
                              maxLength={6}
                              value={totpToken}
                              onChange={(e) => setTotpToken(e.target.value.replace(/\D/g, ""))}
                              placeholder="123456"
                              className="block w-full rounded-lg border border-border bg-muted/40 py-2 pl-10 pr-4 text-sm text-center font-semibold tracking-[0.2em] focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all"
                            />
                          </div>
                        </div>

                        <button
                          type="submit"
                          disabled={isMfaActionLoading || totpToken.length !== 6}
                          className="w-full rounded-lg bg-gradient-to-r from-red-500 to-red-600 py-2 text-sm font-bold text-white hover:shadow-premiumDark transition-all disabled:opacity-50"
                        >
                          Disable MFA
                        </button>
                      </form>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
