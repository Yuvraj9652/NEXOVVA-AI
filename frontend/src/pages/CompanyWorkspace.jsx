import React from "react"
import { Building2, FolderOpen, ArrowRight, Users, BarChart3 } from "lucide-react"

const workspaceSections = [
  {
    title: "Project Hub",
    desc: "Manage projects, documents, broadcasting, and AI matching.",
    path: "/company-workspace/project-hub",
    icon: FolderOpen,
  },
]

export default function CompanyWorkspace() {
  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Company Workspace</h1>
        <p className="text-muted-foreground text-sm mt-1">Central hub for your organization's projects, collaboration, and resources.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {workspaceSections.map((sec, i) => {
          const Icon = sec.icon
          return (
            <a
              key={i}
              href={sec.path}
              className="group flex items-center justify-between rounded-xl border border-border bg-card p-6 shadow-premium hover:shadow-premiumDark transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <Icon className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-foreground group-hover:text-primary transition-colors">{sec.title}</h2>
                  <p className="text-xs text-muted-foreground mt-1 max-w-xs">{sec.desc}</p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
            </a>
          )
        })}
      </div>
    </div>
  )
}
