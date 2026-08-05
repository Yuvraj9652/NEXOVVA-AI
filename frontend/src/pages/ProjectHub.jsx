import React, { useEffect, useRef } from "react"
import {
  FileText,
  Radio,
  UserCheck,
  ArrowRight,
  ChevronLeft,
} from "lucide-react"

const hubModules = [
  {
    title: "Project Knowledge Base",
    desc: "Centralized repository for project documentation and references.",
    path: "/company-workspace/project-hub/knowledge-base",
    icon: FileText,
  },
  {
    title: "Smart Project Broadcasting",
    desc: "AI-powered project announcement distribution.",
    path: "/company-workspace/project-hub/broadcasting",
    icon: Radio,
  },
  {
    title: "AI Customer Matching",
    desc: "Intelligent lead-to-project matching engine.",
    path: "/company-workspace/project-hub/ai-matching",
    icon: UserCheck,
  },
]

export default function ProjectHub() {
  const projectHubRef = useRef(null)

  // Mouse tracking for dashboard cards
  useEffect(() => {
    const boxElements = document.querySelectorAll(".dashboard-card, .chart-box")

    const handleMouseMove = (e) => {
      const element = e.target.closest(".dashboard-card") || e.target.closest(".chart-box")
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
      const element = e.target.closest(".dashboard-card") || e.target.closest(".chart-box")
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

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={projectHubRef}>
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

      {/* Main Content */}
      <div className="relative z-10 mx-auto max-w-7xl px-6 pt-8 pb-16 lg:px-12 space-y-8">
        {/* Welcome Header */}
        <div className="flex items-center gap-4 animate-fade-in">
          <a
            href="/company-workspace"
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-card/60 text-muted-foreground hover:text-foreground hover:bg-muted/40 hover:border-teal-500/30 transition-all duration-300 shadow-sm shrink-0"
            title="Back to Company Workspace"
          >
            <ChevronLeft className="h-5 w-5" />
          </a>
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight">
              <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">Project Hub</span>
            </h1>
            <p className="text-muted-foreground text-sm mt-1">Manage and broadcast your real estate projects with AI-powered tools.</p>
          </div>
        </div>

        {/* Modules Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {hubModules.map((mod, i) => {
            const Icon = mod.icon
            return (
              <a
                key={i}
                href={mod.path}
                className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
                style={{ animationDelay: `${0.1 + i * 0.1}s` }}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <div className="flex items-center justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-500/10 text-teal-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                      <Icon className="h-5 w-5" />
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <h2 className="mt-4 text-base font-bold text-foreground group-hover:text-primary transition-colors">{mod.title}</h2>
                  <p className="mt-1 text-xs text-muted-foreground">{mod.desc}</p>
                </div>
              </a>
            )
          })}
        </div>
      </div>
    </div>
  )
}
