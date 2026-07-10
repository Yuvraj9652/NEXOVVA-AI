import axios from "axios"

const api = axios.create({
  baseURL: "",
  headers: {
    "Content-Type": "application/json",
  },
})

// Inject JWT access tokens into request headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config;
  },
  (error) => Promise.reject(error)
)

// Global 401 handler to sign out users on token expiry
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("accessToken")
      localStorage.removeItem("refreshToken")
      // Redirect to login if window is available
      if (typeof window !== "undefined") {
        window.location.href = "/login"
      }
    }
    return Promise.reject(error)
  }
)

export default api
