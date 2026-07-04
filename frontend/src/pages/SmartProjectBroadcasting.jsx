import React from "react"
import { Radio, Users, Send, Calendar, Eye, TrendingUp } from "lucide-react"

const campaigns = [
  { name: "Oakwood Residency Launch", status: "Active", reach: "2.4K", date: "2026-07-01" },
  { name: "Skyline Towers Update", status: "Scheduled", reach: "1.8K", date: "2026-07-05" },
  { name: "Green Valley Phase 2", status: "Completed", reach: "3.1K", date: "2026-06-28" },
  { name: "Riverside Apartments", status: "Draft", reach: "-", date: "2026-07-10" },
]

export default function SmartProjectBroadcasting() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Smart Project Broadcasting</h1>
          <p className="text-muted-foreground text-sm mt-1">AI-powered project announcements distributed across multiple channels.</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90">
          <Send className="h-4 w-4" /> New Broadcast
        </button>
      </div>

      <div className="rounded-xl border border-border bg-card p-6 shadow-premium">
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
  )
}
