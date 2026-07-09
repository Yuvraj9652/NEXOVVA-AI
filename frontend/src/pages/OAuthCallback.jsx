import React, { useEffect, useState } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import axios from "axios"
import useAuthStore from "../store/authStore"

export default function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const access = searchParams.get("access")
  const refresh = searchParams.get("refresh")
  const [error, setError] = useState("")

  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)

  useEffect(() => {
    const handleCallback = async () => {
      if (!access || !refresh) {
        setError("Invalid authentication response.")
        setTimeout(() => navigate("/login"), 3000)
        return
      }

      try {
        // Fetch user profile using the new access token
        const response = await axios.get("/api/auth/profile/", {
          headers: {
            Authorization: `Bearer ${access}`,
          },
        })
        
        // Structure of custom response has data under data
        const profile = response.data.data
        const user = profile.user
        
        // Log in via authStore
        login(access, refresh, user)
        
        // Redirect to dashboard
        navigate("/dashboard")
      } catch (err) {
        setError("Failed to fetch user profile. Redirecting to login...")
        setTimeout(() => navigate("/login"), 3000)
      }
    }

    handleCallback()
  }, [access, refresh, login, navigate])

  return (
    <div className="flex h-screen w-screen items-center justify-center bg-background text-foreground">
      <div className="flex flex-col items-center gap-4">
        {error ? (
          <p className="text-sm font-semibold text-destructive">{error}</p>
        ) : (
          <>
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            <p className="text-sm font-medium tracking-wide text-muted-foreground">
              Finalizing Google Authentication...
            </p>
          </>
        )}
      </div>
    </div>
  )
}
