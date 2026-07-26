import React, { useEffect, useRef } from "react"
import { Radio, Users, Send, Calendar, Eye, TrendingUp } from "lucide-react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "../api/client"

export default function SmartProjectBroadcasting() {
  const broadcastingRef = useRef(null)
  const queryClient = useQueryClient()

  const { data: campaigns = [] } = useQuery({
    queryKey: ["campaigns"],
    queryFn: () => api.get("/api/communications/campaigns/").then((res) => res.data.results || res.data || []),
  })

  const newCampaignMutation = useMutation({
    mutationFn: (name) => api.post("/api/communications/campaigns/", {
      name,
      status: "Active",
      date: new Date().toISOString().split("T")[0]
    }),
    onSuccess: () => {
      queryClient.invalidateQueries(["campaigns"])
    }
  })

  const handleNewBroadcast = () => {
    const name = prompt("Enter Campaign Name:")
    if (name) {
      newCampaignMutation.mutate(name)
    }
  }

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
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={broadcastingRef}>
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
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between animate-fade-in">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
              <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">
                Smart Project Broadcasting
              </span>
            </h1>
            <p className="text-muted-foreground text-sm mt-1">AI-powered project announcements distributed across multiple channels.</p>
          </div>
          <button onClick={handleNewBroadcast} className="dashboard-card group flex items-center gap-2 rounded-xl border border-border bg-gradient-to-r from-teal-500 to-amber-600 px-4 py-2 text-sm font-semibold text-primary-foreground hover:shadow-premiumDark transition-all duration-300 animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <Send className="h-4 w-4" /> New Broadcast
          </button>
        </div>

        {/* Active Campaigns */}
        <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md shadow-premium transition-all duration-300 hover:-translate-y-1 hover:shadow-premiumDark overflow-hidden animate-fade-in" style={{ animationDelay: "0.2s" }}>
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
          <div className="relative z-10">
            <h2 className="text-base font-bold text-foreground mb-4">Active Campaigns</h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-left text-sm">
                <thead className="bg-muted/40 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  <tr>
                    <th className="px-4 py-3">Campaign</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Audience Reach</th>
                    <th className="px-4 py-3">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {campaigns.map((c, i) => (
                    <tr key={i} className="hover:bg-muted/20">
                      <td className="px-4 py-3 font-medium text-foreground">{c.name}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                            c.status === "Active" ? "bg-emerald-500/10 text-emerald-500"
                            : c.status === "Scheduled" ? "bg-blue-500/10 text-blue-500"
                            : c.status === "Completed" ? "bg-muted text-muted-foreground"
                            : "bg-amber-500/10 text-amber-500"
                          }`}
                        >
                          {c.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{c.reach}</td>
                      <td className="px-4 py-3 text-muted-foreground">{c.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
