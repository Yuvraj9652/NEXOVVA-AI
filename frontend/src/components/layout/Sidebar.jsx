import React, { useState } from "react"
import { Link, useLocation } from "react-router-dom"
import {
  LayoutDashboard,
  Users,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Sparkles,
  Building,
  User,
  Settings as SettingsIcon,
  ChevronDown,
  FolderOpen,
  FileText,
  Radio,
  UserCheck,
  BarChart3,
  Folder,
  TrendingUp,
} from "lucide-react"
import useAuthStore from "../../store/authStore"

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [expandedMenus, setExpandedMenus] = useState({})
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const toggleMenu = (menu) => {
    setExpandedMenus((prev) => ({ ...prev, [menu]: !prev[menu] }))
  }

  const isActive = (path) => location.pathname === path
  const isChildActive = (paths) => paths.some((p) => location.pathname === p)

  const menuItems = [
    {
      path: "/dashboard",
      name: "Dashboard",
      icon: LayoutDashboard,
    },
    {
      path: "/crm",
      name: "AI Sales Employee & Lead Management",
      icon: Users,
    },
    {
      path: "/reports-analytics",
      name: "Reports & Analytics",
      icon: TrendingUp,
    },
    {
      name: "Company Workspace",
      icon: Building,
      children: [
        {
          name: "Project Hub",
          icon: FolderOpen,
          children: [
            { path: "/company-workspace/project-hub/knowledge-base", name: "Project Knowledge Base", icon: FileText },
            { path: "/company-workspace/project-hub/broadcasting", name: "Smart Project Broadcasting", icon: Radio },
            { path: "/company-workspace/project-hub/ai-matching", name: "AI Customer Matching", icon: UserCheck },
            { path: "/company-workspace/project-hub/analytics", name: "Project Analytics", icon: BarChart3 },
            { path: "/company-workspace/project-hub/documents", name: "Project Document Manager", icon: Folder },
          ],
        },
      ],
    },
    {
      path: "/ai-chat",
      name: "AI Assistant",
      icon: MessageSquare,
    },
    {
      path: "/settings",
      name: "Settings & Security",
      icon: SettingsIcon,
    },
  ]

  return (
    <aside
      className={`relative flex flex-col border-r border-border bg-card transition-all duration-300 ${
        isCollapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-border">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-tr from-primary to-violet-400 text-white shadow-premium">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="font-bold tracking-tight text-lg bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text">
              NEXOVA AI
            </span>
          </div>
        )}
        {isCollapsed && (
          <div className="flex h-8 w-8 mx-auto items-center justify-center rounded-lg bg-gradient-to-tr from-primary to-violet-400 text-white">
            <Sparkles className="h-4 w-4" />
          </div>
        )}

        {/* Collapse Button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={`flex h-6 w-6 items-center justify-center rounded-full border border-border bg-background shadow-premium hover:bg-muted ${
            isCollapsed ? "absolute -right-3 top-5" : ""
          }`}
        >
          {isCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
        </button>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon
          const hasChildren = item.children && item.children.length > 0
          const isExpanded = expandedMenus[item.name] || (hasChildren && isChildActive(item.children.flatMap(c => c.path ? [c.path] : c.children?.map(ch => ch.path) || [])))

          if (hasChildren) {
            return (
              <div key={item.name} className="space-y-1">
                <button
                  onClick={() => !isCollapsed && toggleMenu(item.name)}
                  className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                    isCollapsed ? "justify-center" : ""
                  } ${
                    isChildActive(item.children.flatMap(c => c.path ? [c.path] : c.children?.map(ch => ch.path) || []))
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {!isCollapsed && <span className="flex-1 text-left">{item.name}</span>}
                  {!isCollapsed && (
                    <ChevronDown
                      className={`h-4 w-4 transition-transform ${isExpanded ? "rotate-180" : ""}`}
                    />
                  )}
                </button>

                {!isCollapsed && isExpanded && (
                  <div className="ml-4 space-y-1 border-l border-border pl-3">
                    {item.children.map((child) => {
                      const ChildIcon = child.icon
                      const childHasChildren = child.children && child.children.length > 0
                      const childExpanded = expandedMenus[child.name]

                      if (childHasChildren) {
                        return (
                          <div key={child.name}>
                            <button
                              onClick={() => toggleMenu(child.name)}
                              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-all"
                            >
                              <ChildIcon className="h-4 w-4 shrink-0" />
                              <span className="flex-1 text-left">{child.name}</span>
                              <ChevronDown
                                className={`h-3 w-3 transition-transform ${childExpanded ? "rotate-180" : ""}`}
                              />
                            </button>
                            {childExpanded && (
                              <div className="ml-4 space-y-1 border-l border-border pl-3">
                                {child.children.map((grandChild) => {
                                  const GCIcon = grandChild.icon
                                  const active = isActive(grandChild.path)
                                  return (
                                    <Link
                                      key={grandChild.path}
                                      to={grandChild.path}
                                      className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition-all duration-200 ${
                                        active
                                          ? "bg-primary text-primary-foreground shadow-premium"
                                          : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                      }`}
                                    >
                                      <GCIcon className="h-4 w-4 shrink-0" />
                                      <span>{grandChild.name}</span>
                                    </Link>
                                  )
                                })}
                              </div>
                            )}
                          </div>
                        )
                      }

                      const active = isActive(child.path)
                      return (
                        <Link
                          key={child.path}
                          to={child.path}
                          className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition-all duration-200 ${
                            active
                              ? "bg-primary text-primary-foreground shadow-premium"
                              : "text-muted-foreground hover:bg-muted hover:text-foreground"
                          }`}
                        >
                          <ChildIcon className="h-4 w-4 shrink-0" />
                          <span>{child.name}</span>
                        </Link>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          }

          const active = isActive(item.path)
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                active
                  ? "bg-primary text-primary-foreground shadow-premium"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!isCollapsed && <span>{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      {/* User Info & Logout */}
      <div className="border-t border-border p-3">
        {!isCollapsed && user && (
          <div className="mb-4 rounded-xl bg-muted/50 p-3">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
                <User className="h-4 w-4" />
              </div>
              <div className="overflow-hidden">
                <p className="truncate text-xs font-semibold text-foreground">
                  {user.first_name || user.username}
                </p>
                <p className="truncate text-[10px] text-muted-foreground uppercase tracking-wide">
                  {user.role}
                </p>
              </div>
            </div>
            {user.organization && (
              <div className="mt-2 flex items-center gap-1.5 text-[10px] text-muted-foreground">
                <Building className="h-3 w-3" />
                <span className="truncate">{user.organization.name}</span>
              </div>
            )}
          </div>
        )}

        <button
          onClick={logout}
          className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-destructive hover:bg-destructive/10 transition-all duration-200 ${
            isCollapsed ? "justify-center" : ""
          }`}
        >
          <LogOut className="h-5 w-5 shrink-0" />
          {!isCollapsed && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  )
}

