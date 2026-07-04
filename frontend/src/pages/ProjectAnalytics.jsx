import React from "react"
import {
  DollarSign,
  TrendingUp,
  Users,
  Home,
  Target,
  ArrowRight,
} from "lucide-react"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts"

const pipelineData = [
  { name: "New", value: 120000 },
  { name: "Contacted", value: 450000 },
  { name: "Proposal", value: 310000 },
  { name: "Negotiation", value: 680000 },
  { name: "Closed Won", value: 920000 },
]

const monthlyData = [
  { month: "Jan", deals: 4, value: 320000 },
  { month: "Feb", deals: 6, value: 480000 },
  { month: "Mar", deals: 5, value: 410000 },
  { month: "Apr", deals: 8, value: 650000 },
  { month: "May", deals: 7, value: 720000 },
  { month: "Jun", deals: 9, value: 890000 },
]

export default function ProjectAnalytics() {
  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Project Analytics</h1>
        <p className="text-muted-foreground text-sm mt-1">Comprehensive project performance metrics and insights.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-border bg-card p-5 shadow-premium">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Active Projects</span>
            <Home className="h-4 w-4 text-primary" />
          </div>
          <p className="mt-3 text-2xl font-extrabold text-foreground">12</p>
          <span className="text-xs text-muted-foreground">Across 3 cities</span>
        </div>
        <div className="rounded-xl border border-border bg-card p-5 shadow-premium">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Pipeline Value</span>
            <DollarSign className="h-4 w-4 text-emerald-500" />
          </div>
          <p className="mt-3 text-2xl font-extrabold text-foreground">$2.4M</p>
          <span className="flex items-center text-xs text-emerald-500">
            <TrendingUp className="mr-1 h-3 w-3" /> +14.2%
          </span>
        </div>
        <div className="rounded-xl border border-border bg-card p-5 shadow-premium">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Conversion Rate</span>
            <Target className="h-4 w-4 text-blue-500" />
          </div>
          <p className="mt-3 text-2xl font-extrabold text-foreground">68%</p>
          <span className="text-xs text-muted-foreground">Lead to deal</span>
        </div>
        <div className="rounded-xl border border-border bg-card p-5 shadow-premium">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Avg. Days to Close</span>
            <Users className="h-4 w-4 text-amber-500" />
          </div>
          <p className="mt-3 text-2xl font-extrabold text-foreground">21</p>
          <span className="flex items-center text-xs text-emerald-500">
            <TrendingUp className="mr-1 h-3 w-3" /> -3 days
          </span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-6 shadow-premium">
          <h2 className="text-base font-bold text-foreground mb-1">Project Pipeline Distribution</h2>
          <p className="text-xs text-muted-foreground mb-4">Value per project stage</p>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={pipelineData} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    borderColor: "hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                  itemStyle={{ color: "hsl(var(--foreground))" }}
                />
                <Bar dataKey="value" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6 shadow-premium">
          <h2 className="text-base font-bold text-foreground mb-1">Monthly Deal Trends</h2>
          <p className="text-xs text-muted-foreground mb-4">Closed deals count and value</p>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyData}>
                <defs>
                  <linearGradient id="colorProjectValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    borderColor: "hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                  itemStyle={{ color: "hsl(var(--foreground))" }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="hsl(var(--primary))"
                  fillOpacity={1}
                  fill="url(#colorProjectValue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
