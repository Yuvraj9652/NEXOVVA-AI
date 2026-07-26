import React, { useEffect } from "react"
import { UserCheck, Star, Target, ArrowRight } from "lucide-react"
import { useQuery } from "@tanstack/react-query"
import api from "../api/client"

export default function AICustomerMatching() {
  const { data: matches = [] } = useQuery({
    queryKey: ["aiMatching"],
    queryFn: () => api.get("/api/ai/matching/").then((res) => res.data),
  })
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
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground">
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
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between animate-fade-in">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground">
              <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">AI Customer Matching</span>
            </h1>
            <p className="text-muted-foreground text-sm mt-2">Intelligent lead-to-project matching engine powered by behavioral analysis.</p>
          </div>
          <button className="dashboard-card flex items-center gap-2 rounded-xl border border-border bg-card/60 px-4 py-2.5 text-sm font-semibold backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-premiumDark">
            <UserCheck className="h-4 w-4 text-teal-500" /> Run Matching
          </button>
        </div>

        <div className="grid gap-6">
          {matches.map((m, i) => (
            <div
              key={i}
              className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
              style={{ animationDelay: `${0.1 + i * 0.1}s` }}
            >
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-500/10 text-teal-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                    <Target className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-foreground">{m.lead} → {m.project}</h3>
                    <p className="text-xs text-muted-foreground mt-1">{m.reason}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-3 py-1.5 text-xs font-bold text-emerald-500">
                    <Star className="h-3.5 w-3.5" /> {m.score}%
                  </span>
                  <button className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card/60 backdrop-blur-md text-muted-foreground transition-all duration-300 hover:bg-muted hover:text-foreground hover:-translate-y-1 hover:shadow-premiumDark">
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
