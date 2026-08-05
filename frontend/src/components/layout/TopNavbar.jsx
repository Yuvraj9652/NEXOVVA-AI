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
  Database,
} from "lucide-react"
import useAuthStore from "../../store/authStore"

export default function TopNavbar() {
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const navItems = [
    { path: "/dashboard", name: "Dashboard", icon: LayoutDashboard },
    { path: "/customers", name: "Customer Database", icon: Database },
    { path: "/crm", name: "AI Sales & Leads", icon: Users },
    { path: "/reports-analytics", name: "Reports", icon: TrendingUp },
    { path: "/company-workspace", name: "Workspace", icon: Building },
    { path: "/ai-chat", name: "AI Assistant", icon: MessageSquare },
    { path: "/settings", name: "Settings", icon: SettingsIcon },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/50 bg-card/40 backdrop-blur-2xl">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-lg shadow-teal-500/20">
              <Sparkles className="h-4.5 w-4.5" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-tight text-foreground">NEXOVA</span>
              <span className="text-[10px] font-medium text-teal-500 -mt-0.5">AI Platform</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.path)
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium transition-all duration-200 ${
                    active
                      ? "bg-teal-500/10 text-teal-500"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.name}
                </Link>
              )
            })}
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-3">
            {/* User Info - Desktop */}
            <div className="hidden md:flex items-center gap-3">
              <div className="flex items-center gap-2 rounded-xl bg-muted/50 px-3 py-1.5 border border-border/50">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-tr from-teal-500/10 to-amber-500/10 text-teal-500">
                  <User className="h-3.5 w-3.5" />
                </div>
                <div className="hidden lg:block">
                  <p className="text-xs font-semibold text-foreground truncate max-w-[120px]">
                    {user?.first_name || user?.username}
                  </p>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wide">
                    {user?.role}
                  </p>
                </div>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium text-destructive hover:bg-destructive/10 transition-all duration-200"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden lg:inline">Sign Out</span>
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-card/60 backdrop-blur-md text-muted-foreground hover:text-foreground transition-all"
            >
              {isOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden border-t border-border/50 bg-card/80 backdrop-blur-2xl animate-fade-in">
          <div className="mx-auto max-w-7xl px-6 py-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.path)
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 ${
                    active
                      ? "bg-teal-500/10 text-teal-500"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.name}
                </Link>
              )
            })}
            <div className="pt-3 border-t border-border/50 mt-3 space-y-2">
              <div className="flex items-center gap-3 px-4 py-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-tr from-teal-500/10 to-amber-500/10 text-teal-500">
                  <User className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-foreground">
                    {user?.first_name || user?.username}
                  </p>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wide">
                    {user?.role}
                  </p>
                </div>
              </div>
              <button
                onClick={() => { logout(); setIsOpen(false) }}
                className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-destructive hover:bg-destructive/10 transition-all duration-200 w-full"
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
