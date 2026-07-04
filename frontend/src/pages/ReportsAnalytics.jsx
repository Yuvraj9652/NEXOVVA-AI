import React from "react"
import { FileBarChart, TrendingUp, DollarSign, Users, Download, Calendar } from "lucide-react"

const reportCards = [
  { title: "Sales Performance", desc: "Monthly and weekly sales metrics", icon: TrendingUp },
  { title: "Lead Conversion", desc: "Funnel analysis and conversion rates", icon: Users },
  { title: "Revenue Analytics", desc: "Revenue breakdown by project and agent", icon: DollarSign },
  { title: "AI Usage Reports", desc: "AI operations cost and efficiency", icon: FileBarChart },
  { title: "Employee Performance", desc: "Agent leaderboard and task metrics", icon: Users },
  { title: "Market Trends", desc: "Real estate market insights and forecasts", icon: Calendar },
]

export default function ReportsAnalytics() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Reports & Analytics</h1>
          <p className="text-muted-foreground text-sm mt-1">Business intelligence, performance dashboards, and exportable reports.</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-semibold hover:bg-muted">
          <Download className="h-4 w-4" /> Export All
        </button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {reportCards.map((item, idx) => {
          const Icon = item.icon
          return (
            <div key={idx} className="group flex flex-col rounded-xl border border-border bg-card p-6 shadow-premium hover:shadow-premiumDark transition-all cursor-pointer">
              <div className="flex items-center justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-xs font-medium text-muted-foreground">Report</span>
              </div>
              <h3 className="mt-4 text-base font-bold text-foreground group-hover:text-primary transition-colors">{item.title}</h3>
              <p className="mt-1 text-xs text-muted-foreground">{item.desc}</p>
              <div className="mt-4 flex items-center gap-1 text-xs font-semibold text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                View Report <TrendingUp className="h-3 w-3" />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
