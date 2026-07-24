import React, { useEffect, useRef } from "react"
import { FileUp, Folder, File, Trash2, MoreVertical, Clock } from "lucide-react"

const documents = [
  { name: "Blueprints - Block A", type: "PDF", size: "12 MB", modified: "Today, 10:30 AM" },
  { name: "Legal Agreements v2", type: "DOCX", size: "4.2 MB", modified: "Yesterday, 4:15 PM" },
  { name: "Construction Budget", type: "XLSX", size: "1.8 MB", modified: "Jul 1, 2026" },
  { name: "Interior Specifications", type: "PDF", size: "8.5 MB", modified: "Jun 28, 2026" },
  { name: "Site Survey Report", type: "PDF", size: "15 MB", modified: "Jun 25, 2026" },
]

export default function ProjectDocumentManager() {
  const documentManagerRef = useRef(null)

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
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={documentManagerRef}>
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
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground">
              <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">Project Document Manager</span>
            </h1>
            <p className="text-muted-foreground text-sm mt-2">
              Organize, upload, and manage project documents securely.
            </p>
          </div>
          <button className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all duration-300 hover:-translate-y-1 animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <FileUp className="h-4 w-4" /> Upload Document
          </button>
        </div>

        {/* Documents List */}
        <div className="dashboard-card group relative rounded-3xl border border-border bg-card/60 backdrop-blur-md shadow-premium overflow-hidden animate-fade-in" style={{ animationDelay: "0.2s" }}>
          <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
          <div className="relative z-10">
            <div className="flex items-center justify-between border-b border-border bg-muted/20 px-6 py-4">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-500/10 text-teal-500">
                  <Folder className="h-4 w-4" />
                </div>
                <h2 className="text-sm font-bold text-foreground">Documents</h2>
              </div>
              <span className="text-xs text-muted-foreground">{documents.length} files</span>
            </div>
            <div className="divide-y divide-border">
              {documents.map((doc, i) => (
                <div key={i} className="flex items-center justify-between px-6 py-4 hover:bg-muted/20 transition-all duration-300 group/row">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary transition-all duration-300 group-hover/row:scale-110 group-hover/row:rotate-6">
                      <File className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-foreground">{doc.name}</p>
                      <span className="text-xs text-muted-foreground">{doc.type} • {doc.size}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" /> {doc.modified}
                    </span>
                    <button className="rounded-lg p-2 text-muted-foreground hover:text-destructive hover:bg-muted transition-all duration-200 hover:scale-110">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
