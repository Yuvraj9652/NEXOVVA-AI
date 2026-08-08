import React, { useState } from "react"
import { Link, useLocation } from "react-router-dom"
import {
  LayoutDashboard,
  Users,
  TrendingUp,
  Building,
  MessageSquare,
  Settings as SettingsIcon,
  LogOut,
  Sparkles,
  Menu,
  X,
  User,
  ChevronRight,
} from "lucide-react"
import useAuthStore from "../../store/authStore"

export default function TopNavbar() {
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()
  const { user, logout } = useAuthStore()

  // Removed Customer Database as requested by user!
  const navItems = [
    { path: "/dashboard", name: "Dashboard", icon: LayoutDashboard },
    { path: "/crm", name: "AI Sales & Leads", icon: Users },
    { path: "/reports-analytics", name: "Reports", icon: TrendingUp },
    { path: "/company-workspace", name: "Workspace", icon: Building },
    { path: "/ai-chat", name: "AI Assistant", icon: MessageSquare },
    { path: "/settings", name: "Settings", icon: SettingsIcon },
  ]

  const isActive = (path) => {
    if (path === "/dashboard" && location.pathname === "/") return true
    return location.pathname === path || location.pathname.startsWith(path + "/")
  }

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/60 bg-card/70 backdrop-blur-xl shadow-lg transition-all duration-300">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <div className="flex h-16 items-center justify-between gap-4">
          
          {/* Brand Logo */}
          <Link to="/dashboard" className="flex items-center gap-3 group shrink-0">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-md shadow-teal-500/20 group-hover:scale-105 transition-transform duration-300">
              <Sparkles className="h-4.5 w-4.5 animate-pulse" />
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-base tracking-tight text-foreground group-hover:text-teal-400 transition-colors">
                NEXOVA
              </span>
              <span className="text-[10px] font-bold text-teal-400 -mt-1 tracking-wider uppercase">
                AI Platform
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Items */}
          <div className="hidden md:flex items-center gap-1.5 rounded-2xl border border-border/40 bg-muted/20 p-1 backdrop-blur-md">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.path)
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all duration-200 ${
                    active
                      ? "bg-teal-500/15 text-teal-400 border border-teal-500/30 shadow-sm shadow-teal-500/10"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/40"
                  }`}
                >
                  <Icon className={`h-4 w-4 transition-transform duration-200 ${active ? "text-teal-400 scale-110" : ""}`} />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </div>

          {/* Right User Controls */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="hidden md:flex items-center gap-3">
              <div className="flex items-center gap-2.5 rounded-xl bg-muted/40 px-3 py-1.5 border border-border/50 backdrop-blur-md">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-tr from-teal-500/20 to-amber-500/20 text-teal-400 font-bold text-xs">
                  {user?.first_name?.[0] || user?.username?.[0] || "U"}
                </div>
                <div className="hidden lg:block text-left">
                  <p className="text-xs font-bold text-foreground leading-tight truncate max-w-[110px]">
                    {user?.first_name || user?.username || "Admin"}
                  </p>
                  <p className="text-[9px] font-extrabold text-teal-400 uppercase tracking-wider">
                    {user?.role || "Manager"}
                  </p>
                </div>
              </div>

              <button
                onClick={logout}
                className="flex items-center gap-1.5 rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-1.5 text-xs font-bold text-rose-400 hover:bg-rose-500/20 hover:text-rose-300 transition-all duration-200 shadow-sm"
                title="Sign Out"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span className="hidden lg:inline">Sign Out</span>
              </button>
            </div>

            {/* Mobile Hamburger Menu Toggle */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-card/80 text-muted-foreground hover:text-foreground transition-all"
            >
              {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {isOpen && (
        <div className="md:hidden border-t border-border/60 bg-card/95 backdrop-blur-2xl animate-fade-in shadow-2xl">
          <div className="mx-auto max-w-7xl px-6 py-4 space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.path)
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center justify-between rounded-xl px-4 py-2.5 text-sm font-semibold transition-all duration-200 ${
                    active
                      ? "bg-teal-500/15 text-teal-400 border border-teal-500/30"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/40"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </div>
                  <ChevronRight className="h-4 w-4 opacity-60" />
                </Link>
              )
            })}

            <div className="pt-3 border-t border-border/60 mt-3 space-y-2">
              <div className="flex items-center gap-3 px-4 py-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-500/20 text-teal-400 font-bold text-xs">
                  {user?.first_name?.[0] || user?.username?.[0] || "U"}
                </div>
                <div>
                  <p className="text-xs font-bold text-foreground">
                    {user?.first_name || user?.username}
                  </p>
                  <p className="text-[10px] font-extrabold text-teal-400 uppercase tracking-wider">
                    {user?.role || "Manager"}
                  </p>
                </div>
              </div>

              <button
                onClick={() => { logout(); setIsOpen(false) }}
                className="flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold text-rose-400 bg-rose-500/10 hover:bg-rose-500/20 transition-all duration-200 w-full justify-center border border-rose-500/30"
              >
                <LogOut className="h-4 w-4" />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
