import React from "react"
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
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Project Knowledge Base</h1>
          <p className="text-muted-foreground text-sm mt-1">Centralized repository for project documentation, specifications, and reference materials.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search documents..."
              className="h-10 w-64 rounded-lg border border-border bg-muted/40 py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90">
            <Upload className="h-4 w-4" /> Upload
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {knowledgeItems.map((item, idx) => (
          <div key={idx} className="group rounded-xl border border-border bg-card p-5 shadow-premium hover:shadow-premiumDark transition-all cursor-pointer">
            <div className="flex items-start justify-between">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
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
        ))}
      </div>
    </div>
  )
}
