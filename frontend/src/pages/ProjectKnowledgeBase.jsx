import React, { useEffect, useRef } from "react"
import { FileText, Search, BarChart3, Upload, FolderOpen, Clock, ChevronRight } from "lucide-react"

const knowledgeItems = [
  { title: "Project Specifications", type: "PDF", updated: "2 hours ago", size: "2.4 MB" },
  { title: "Market Analysis Report", type: "DOCX", updated: "1 day ago", size: "1.8 MB" },
  { title: "Site Survey Data", type: "XLSX", updated: "3 days ago", size: "4.1 MB" },
  { title: "Legal Compliance Docs", type: "PDF", updated: "1 week ago", size: "3.2 MB" },
  { title: "Financial Projections", type: "PDF", updated: "1 week ago", size: "1.5 MB" },
  { title: "Construction Timeline", type: "DOCX", updated: "2 weeks ago", size: "0.8 MB" },
]

export default function ProjectKnowledgeBase() {
  const knowledgeBaseRef = useRef(null)

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
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={knowledgeBaseRef}>
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
        {/* Header Section */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between animate-fade-in">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
              Project Knowledge Base
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              Centralized repository for project documentation, specifications, and reference materials.
            </p>
          </div>
          <div className="flex items-center gap-3 animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search documents..."
                className="h-10 w-64 rounded-lg border border-border bg-muted/40 py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <button className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-teal-500 to-amber-600 px-4 py-2 text-sm font-semibold text-white hover:from-teal-600 hover:to-amber-700 transition-all duration-300 shadow-premium hover:shadow-premiumDark hover:-translate-y-0.5">
              <Upload className="h-4 w-4" /> Upload
            </button>
          </div>
        </div>

        {/* Knowledge Items Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {knowledgeItems.map((item, idx) => (
            <div
              key={idx}
              className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden cursor-pointer"
              style={{ animationDelay: `${0.1 + idx * 0.1}s` }}
            >
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10">
                <div className="flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10 text-teal-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                    <FileText className="h-5 w-5" />
                  </div>
                  <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-bold text-muted-foreground">{item.type}</span>
                </div>
                <h3 className="mt-4 text-sm font-bold text-foreground group-hover:text-primary transition-colors">{item.title}</h3>
                <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {item.updated}</span>
                  <span>{item.size}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
