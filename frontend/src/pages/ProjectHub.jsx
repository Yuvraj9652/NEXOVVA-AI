import React from "react"
import {
  FileText,
  Radio,
  UserCheck,
  BarChart3,
  FolderOpen,
  ArrowRight,
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
  {
    title: "Project Analytics",
    desc: "Comprehensive project performance metrics.",
    path: "/company-workspace/project-hub/analytics",
    icon: BarChart3,
  },
  {
    title: "Project Document Manager",
    desc: "Organize and manage project files and documents.",
    path: "/company-workspace/project-hub/documents",
    icon: FolderOpen,
  },
]

export default function ProjectHub() {
  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Project Hub</h1>
        <p className="text-muted-foreground text-sm mt-1">Manage and broadcast your real estate projects with AI-powered tools.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {hubModules.map((mod, i) => {
          const Icon = mod.icon
          return (
            <a
              key={i}
              href={mod.path}
              className="group flex flex-col rounded-xl border border-border bg-card p-6 shadow-premium hover:shadow-premiumDark transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <h2 className="mt-4 text-base font-bold text-foreground group-hover:text-primary transition-colors">{mod.title}</h2>
              <p className="mt-1 text-xs text-muted-foreground">{mod.desc}</p>
            </a>
          )
        })}
      </div>
    </div>
  )
}
