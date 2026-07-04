import { create } from "zustand"

const useAuthStore = create((set) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,

  initialize: () => {
    const accessToken = localStorage.getItem("accessToken")
    const refreshToken = localStorage.getItem("refreshToken")
    const savedUser = localStorage.getItem("user")

    if (accessToken && savedUser) {
      set({
        accessToken,
        refreshToken,
        user: JSON.parse(savedUser),
        isAuthenticated: true,
        isLoading: false,
      })
    } else {
      set({ isLoading: false })
    }
  },

  login: (accessToken, refreshToken, user) => {
    localStorage.setItem("accessToken", accessToken)
    localStorage.setItem("refreshToken", refreshToken)
    localStorage.setItem("user", JSON.stringify(user))

    set({
      accessToken,
      refreshToken,
      user,
      isAuthenticated: true,
    })
  },

  logout: () => {
    localStorage.removeItem("accessToken")
    localStorage.removeItem("refreshToken")
    localStorage.removeItem("user")

    set({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
    })
  },

  updateUser: (user) => {
    localStorage.setItem("user", JSON.stringify(user))
    set({ user })
  },
}))

export default useAuthStore
