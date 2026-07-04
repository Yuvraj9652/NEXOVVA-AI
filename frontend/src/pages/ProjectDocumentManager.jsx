import React from "react"
import { FileUp, Folder, File, Trash2, MoreVertical, Clock } from "lucide-react"

const documents = [
  { name: "Blueprints - Block A", type: "PDF", size: "12 MB", modified: "Today, 10:30 AM" },
  { name: "Legal Agreements v2", type: "DOCX", size: "4.2 MB", modified: "Yesterday, 4:15 PM" },
  { name: "Construction Budget", type: "XLSX", size: "1.8 MB", modified: "Jul 1, 2026" },
  { name: "Interior Specifications", type: "PDF", size: "8.5 MB", modified: "Jun 28, 2026" },
  { name: "Site Survey Report", type: "PDF", size: "15 MB", modified: "Jun 25, 2026" },
]

export default function ProjectDocumentManager() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Project Document Manager</h1>
          <p className="text-muted-foreground text-sm mt-1">Organize, upload, and manage project documents securely.</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90">
          <FileUp className="h-4 w-4" /> Upload Document
        </button>
      </div>

      <div className="rounded-xl border border-border bg-card shadow-premium overflow-hidden">
        <div className="flex items-center justify-between border-b border-border bg-muted/20 px-6 py-4">
          <h2 className="text-sm font-bold text-foreground">Documents</h2>
          <span className="text-xs text-muted-foreground">{documents.length} files</span>
        </div>
        <div className="divide-y divide-border">
          {documents.map((doc, i) => (
            <div key={i} className="flex items-center justify-between px-6 py-4 hover:bg-muted/20 transition-colors">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
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
                <button className="rounded-lg p-2 text-muted-foreground hover:text-destructive hover:bg-muted">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
