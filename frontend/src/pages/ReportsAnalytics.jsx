import React, { useEffect, useRef } from "react"
import { FileBarChart, TrendingUp, DollarSign, Users, Download, Calendar } from "lucide-react"

const reportCards = [
  { title: "Sales Performance", desc: "Monthly and weekly sales metrics", icon: TrendingUp },
  { title: "Lead Conversion", desc: "Funnel analysis and conversion rates", icon: Users },
  { title: "Revenue Analytics", desc: "Revenue breakdown by project and agent", icon: DollarSign },
  { title: "AI Usage Reports", desc: "AI operations cost and efficiency", icon: FileBarChart },
  { title: "Employee Performance", desc: "Agent leaderboard and task metrics", icon: Users },
  { title: "Market Trends", desc: "Real estate market insights and forecasts", icon: Calendar },
]

export default function ReportsAnalytics() {
  const reportsRef = useRef(null)

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
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={reportsRef}>
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
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between animate-fade-in">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground">
              <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">Reports & Analytics</span>
            </h1>
            <p className="text-muted-foreground text-sm mt-2">
              Business intelligence, performance dashboards, and exportable reports.
            </p>
          </div>
          <button className="group flex items-center gap-2 rounded-xl border border-border bg-card/60 px-4 py-2.5 text-sm font-semibold hover:from-teal-500 hover:to-amber-600 hover:text-white transition-all duration-300 backdrop-blur-md hover:shadow-premiumDark animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <Download className="h-4 w-4 transition-transform duration-300 group-hover:scale-110" /> Export All
          </button>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {reportCards.map((item, idx) => {
            const Icon = item.icon
            return (
              <div
                key={idx}
                className="dashboard-card group relative flex flex-col rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden cursor-pointer"
                style={{ animationDelay: `${0.1 + idx * 0.1}s` }}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10 flex flex-col flex-1">
                  <div className="flex items-center justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className="text-xs font-medium text-muted-foreground">Report</span>
                  </div>
                  <h3 className="mt-4 text-base font-bold text-foreground group-hover:text-primary transition-colors">{item.title}</h3>
                  <p className="mt-1 text-xs text-muted-foreground flex-1">{item.desc}</p>
                  <div className="mt-4 flex items-center gap-1 text-xs font-semibold text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                    View Report <TrendingUp className="h-3 w-3" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
