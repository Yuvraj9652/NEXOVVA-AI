import React, { useEffect, useRef } from "react"
import {
  DollarSign,
  TrendingUp,
  Users,
  Home,
  Target,
  ArrowRight,
} from "lucide-react"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts"

const pipelineData = [
  { name: "New", value: 120000 },
  { name: "Contacted", value: 450000 },
  { name: "Proposal", value: 310000 },
  { name: "Negotiation", value: 680000 },
  { name: "Closed Won", value: 920000 },
]

const monthlyData = [
  { month: "Jan", deals: 4, value: 320000 },
  { month: "Feb", deals: 6, value: 480000 },
  { month: "Mar", deals: 5, value: 410000 },
  { month: "Apr", deals: 8, value: 650000 },
  { month: "May", deals: 7, value: 720000 },
  { month: "Jun", deals: 9, value: 890000 },
]

export default function ProjectAnalytics() {
  const dashboardRef = useRef(null)

  // Mouse tracking for dashboard cards
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
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={dashboardRef}>
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
        
        {/* Header */}
        <div className="animate-fade-in">
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">Project Analytics</span>
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Comprehensive project performance metrics and insights.</p>
        </div>

        {/* KPI Cards Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div
            className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
            style={{ animationDelay: "0.1s" }}
          >
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Active Projects
                </span>
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-500/10 text-teal-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                  <Home className="h-4 w-4" />
                </div>
              </div>
              <p className="mt-3 text-2xl font-extrabold bg-gradient-to-r from-teal-500 to-emerald-500 bg-clip-text text-transparent">12</p>
              <span className="text-xs text-muted-foreground">Across 3 cities</span>
            </div>
          </div>

          <div
            className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
            style={{ animationDelay: "0.2s" }}
          >
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-amber-500/0 via-amber-500/10 to-amber-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Pipeline Value
                </span>
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                  <DollarSign className="h-4 w-4" />
                </div>
              </div>
              <p className="mt-3 text-2xl font-extrabold bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent">$2.4M</p>
              <span className="flex items-center text-xs text-emerald-500">
                <TrendingUp className="mr-1 h-3 w-3" /> +14.2%
              </span>
            </div>
          </div>

          <div
            className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
            style={{ animationDelay: "0.3s" }}
          >
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-emerald-500/0 via-emerald-500/10 to-emerald-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Conversion Rate
                </span>
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                  <Target className="h-4 w-4" />
                </div>
              </div>
              <p className="mt-3 text-2xl font-extrabold bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">68%</p>
              <span className="text-xs text-muted-foreground">Lead to deal</span>
            </div>
          </div>

          <div
            className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
            style={{ animationDelay: "0.4s" }}
          >
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Avg. Days to Close
                </span>
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-amber-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                  <Users className="h-4 w-4" />
                </div>
              </div>
              <p className="mt-3 text-2xl font-extrabold bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent">21</p>
              <span className="flex items-center text-xs text-emerald-500">
                <TrendingUp className="mr-1 h-3 w-3" /> -3 days
              </span>
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          <div
            className="dashboard-card group relative rounded-3xl border border-border bg-card/60 p-6 backdrop-blur-xl shadow-2xl overflow-hidden animate-fade-in"
            style={{ animationDelay: "0.5s" }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="mb-6">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-500/10 text-teal-500">
                    <Target className="h-4 w-4" />
                  </div>
                  <h2 className="text-base font-extrabold text-foreground">Project Pipeline Distribution</h2>
                </div>
                <p className="text-xs text-muted-foreground mt-1 ml-10">Value per project stage</p>
              </div>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={pipelineData} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        borderColor: "hsl(var(--border))",
                        borderRadius: "12px",
                        backdropFilter: "blur(12px)",
                      }}
                      itemStyle={{ color: "hsl(var(--foreground))" }}
                    />
                    <Bar 
                      dataKey="value" 
                      fill="url(#barGradient)" 
                      radius={[8, 8, 0, 0]}
                    />
                    <defs>
                      <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(180 80% 55%)" stopOpacity={0.9} />
                        <stop offset="95%" stopColor="hsl(180 80% 45%)" stopOpacity={0.4} />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div
            className="dashboard-card group relative rounded-3xl border border-border bg-card/60 p-6 backdrop-blur-xl shadow-2xl overflow-hidden animate-fade-in"
            style={{ animationDelay: "0.6s" }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="mb-6">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 text-amber-500">
                    <TrendingUp className="h-4 w-4" />
                  </div>
                  <h2 className="text-base font-extrabold text-foreground">Monthly Deal Trends</h2>
                </div>
                <p className="text-xs text-muted-foreground mt-1 ml-10">Closed deals count and value</p>
              </div>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={monthlyData}>
                    <defs>
                      <linearGradient id="colorProjectValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(180 80% 55%)" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="hsl(180 80% 45%)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        borderColor: "hsl(var(--border))",
                        borderRadius: "12px",
                        backdropFilter: "blur(12px)",
                      }}
                      itemStyle={{ color: "hsl(var(--foreground))" }}
                    />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="hsl(var(--primary))"
                      strokeWidth={3}
                      fillOpacity={1}
                      fill="url(#colorProjectValue)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
