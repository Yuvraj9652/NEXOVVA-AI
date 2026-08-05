import React, { useEffect } from "react"
import { Building2, FolderOpen, ArrowRight, Users, BarChart3, ChevronLeft } from "lucide-react"

const workspaceSections = [
  {
    title: "Project Hub",
    desc: "Manage projects, documents, broadcasting, and AI matching.",
    path: "/company-workspace/project-hub",
    icon: FolderOpen,
  },
]

export default function CompanyWorkspace() {
  const workspaceRef = React.useRef(null)

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

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={workspaceRef}>
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1920&h=1080&fit=crop"
          alt="Modern Real Estate Building"
          className="w-full h-full object-cover opacity-30"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/60 to-background/80" />
      </div>

      <div className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `radial-gradient(circle at center, hsl(180 80% 60%) 1px, transparent 1px)`,
          backgroundSize: '80px 80px',
        }}
      />

      <div className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-teal-400/20 blur-[100px] animate-pulse" />
      <div className="absolute top-1/3 -right-32 h-80 w-80 rounded-full bg-amber-500/15 blur-[100px] animate-pulse" style={{ animationDelay: "1s" }} />
      <div className="absolute bottom-0 left-1/4 h-64 w-64 rounded-full bg-emerald-500/10 blur-[80px] animate-pulse" style={{ animationDelay: "2s" }} />

      <div className="relative z-10 mx-auto max-w-7xl px-6 pt-8 pb-16 lg:px-12 space-y-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
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
                Company Workspace
              </h1>
              <p className="text-muted-foreground text-sm mt-1">
                Central hub for your organization's projects, collaboration, and resources.
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {workspaceSections.map((sec, i) => {
            const Icon = sec.icon
            return (
              <a
                key={i}
                href={sec.path}
                className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
                style={{ animationDelay: `${0.1 + i * 0.1}s` }}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500/10 to-amber-500/10 text-teal-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                      <Icon className="h-6 w-6" />
                    </div>
                    <div>
                      <h2 className="text-base font-bold text-foreground group-hover:text-teal-500 transition-colors">{sec.title}</h2>
                      <p className="text-xs text-muted-foreground mt-1 max-w-xs">{sec.desc}</p>
                    </div>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-teal-500 transition-colors" />
                </div>
              </a>
            )
          })}
        </div>
      </div>
    </div>
  )
}
