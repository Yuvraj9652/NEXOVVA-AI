import React from "react"
import { UserCheck, Star, Target, ArrowRight } from "lucide-react"

const matches = [
  { lead: "Aarav Sharma", project: "Oakwood Residency", score: 94, reason: "Budget & location alignment" },
  { lead: "Priya Mehta", project: "Skyline Towers", score: 89, reason: "Preference match for high-rise" },
  { lead: "Rohan Iyer", project: "Green Valley", score: 85, reason: "Family-oriented project affinity" },
  { lead: "Sneha Kapoor", project: "Riverside Apts", score: 78, reason: "Investment timeline sync" },
]

export default function AICustomerMatching() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">AI Customer Matching</h1>
          <p className="text-muted-foreground text-sm mt-1">Intelligent lead-to-project matching engine powered by behavioral analysis.</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-semibold hover:bg-muted">
          <UserCheck className="h-4 w-4" /> Run Matching
        </button>
      </div>

      <div className="grid gap-4">
        {matches.map((m, i) => (
          <div key={i} className="flex items-center justify-between rounded-xl border border-border bg-card p-5 shadow-premium hover:shadow-premiumDark transition-all">
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary text-sm font-bold">
                <Target className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-foreground">{m.lead} → {m.project}</h3>
                <p className="text-xs text-muted-foreground mt-0.5">{m.reason}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-bold text-emerald-500">
                <Star className="h-3 w-3" /> {m.score}%
              </span>
              <button className="flex h-8 w-8 items-center justify-center rounded-lg border border-border hover:bg-muted text-muted-foreground">
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
