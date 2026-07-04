import React from "react"
import { useQuery } from "@tanstack/react-query"
import {
  TrendingUp,
  Users,
  Briefcase,
  CheckCircle,
  Sparkles,
  ArrowRight,
  TrendingDown,
  Clock,
  Zap,
} from "lucide-react"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts"
import api from "../api/client"
import useAuthStore from "../store/authStore"

export default function Dashboard() {
  const { user } = useAuthStore()

  // Fetch KPI data & list items
  const { data: contacts } = useQuery({
    queryKey: ["contacts"],
    queryFn: () => api.get("/api/contacts/").then((res) => res.data.results || []),
  })

  const { data: deals } = useQuery({
    queryKey: ["deals"],
    queryFn: () => api.get("/api/pipeline/deals/").then((res) => res.data.results || []),
  })

  const { data: tasks } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => api.get("/api/tasks/").then((res) => res.data.results || []),
  })

  const { data: activities } = useQuery({
    queryKey: ["activities"],
    queryFn: () => api.get("/api/audit/").then((res) => res.data.results || []),
    // Only fetch if manager/admin
    enabled: user?.role === "ADMIN" || user?.role === "MANAGER",
  })

  const { data: aiUsage } = useQuery({
    queryKey: ["aiUsage"],
    queryFn: () => api.get("/api/ai/analytics/").then((res) => res.data),
  })

  // Compute stats
  const totalContacts = contacts?.length || 0
  const activeDeals = deals?.length || 0
  const pipelineValue =
    deals?.reduce((acc, deal) => acc + parseFloat(deal.amount || 0), 0) || 0
  const completedTasks = tasks?.filter((t) => t.completed).length || 0
  const pendingTasks = tasks?.filter((t) => !t.completed).length || 0
  const taskCompletionRate =
    tasks?.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0

  // Chart data
  const stagesCount = {}
  deals?.forEach((d) => {
    const stageName = d.stage_details?.name || "Unassigned"
    stagesCount[stageName] = (stagesCount[stageName] || 0) + parseFloat(d.amount)
  })

  const stagesData = Object.keys(stagesCount).map((key) => ({
    name: key,
    value: stagesCount[key],
  }))

  const defaultStagesData = [
    { name: "New", value: 120000 },
    { name: "Contacted", value: 450000 },
    { name: "Proposal", value: 310000 },
    { name: "Negotiation", value: 680000 },
    { name: "Closed Won", value: 920000 },
  ]

  const chartData = stagesData.length > 0 ? stagesData : defaultStagesData

  const performanceData = [
    { month: "Jan", revenue: 40000 },
    { month: "Feb", revenue: 45000 },
    { month: "Mar", revenue: 60000 },
    { month: "Apr", revenue: 55000 },
    { month: "May", revenue: 78000 },
    { month: "Jun", revenue: 85000 },
  ]

  return (
    <div className="space-y-8 pb-12">
      {/* Welcome Header */}
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            Dashboard
          </h1>
          <p className="text-muted-foreground text-sm">
            Hello, {user?.first_name || user?.username}. Here is what's happening at{" "}
            <span className="font-semibold text-foreground">
              {user?.organization?.name || "your workspace"}
            </span>
            .
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-xl bg-card border border-border px-4 py-2.5 shadow-premium">
          <Sparkles className="h-4 w-4 text-primary animate-pulse" />
          <span className="text-xs font-semibold text-foreground">
            AI Assistant is Active
          </span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* KPI 1 */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-premium hover:shadow-premiumDark transition-all duration-300">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Active Contacts
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-500">
              <Users className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold">{totalContacts}</span>
            <span className="flex items-center text-xs font-medium text-emerald-500">
              <TrendingUp className="mr-0.5 h-3.5 w-3.5" /> +12%
            </span>
          </div>
        </div>

        {/* KPI 2 */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-premium hover:shadow-premiumDark transition-all duration-300">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Pipeline Value
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-500">
              <Briefcase className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold">
              ${pipelineValue.toLocaleString(undefined, { minimumFractionDigits: 0 })}
            </span>
            <span className="flex items-center text-xs font-medium text-emerald-500">
              <TrendingUp className="mr-0.5 h-3.5 w-3.5" /> +8.4%
            </span>
          </div>
        </div>

        {/* KPI 3 */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-premium hover:shadow-premiumDark transition-all duration-300">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Task Execution
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-500/10 text-amber-500">
              <CheckCircle className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold">{taskCompletionRate}%</span>
            <span className="text-xs font-medium text-muted-foreground">
              {completedTasks}/{tasks?.length || 0} tasks
            </span>
          </div>
        </div>

        {/* KPI 4 */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-premium hover:shadow-premiumDark transition-all duration-300">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              AI Processing Cost
            </span>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-500/10 text-violet-500">
              <Zap className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold">
              ${aiUsage?.total_cost?.toFixed(3) || "0.000"}
            </span>
            <span className="text-xs font-medium text-muted-foreground">
              {aiUsage?.total_requests || 0} operations
            </span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Deal Funnel Chart */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-premium">
          <div className="mb-4">
            <h2 className="text-base font-bold text-foreground">Pipeline Funnel Distribution</h2>
            <p className="text-xs text-muted-foreground">Volume in USD ($) divided by pipeline stages</p>
          </div>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
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

        {/* Monthly Revenue Graph */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-premium">
          <div className="mb-4">
            <h2 className="text-base font-bold text-foreground">Performance Yield</h2>
            <p className="text-xs text-muted-foreground">Estimated closed-won performance trends</p>
          </div>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
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
                  dataKey="revenue"
                  stroke="hsl(var(--primary))"
                  fillOpacity={1}
                  fill="url(#colorRevenue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Activity Streams (Audit) & Pending Tasks */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Activity Logs (2 cols wide on desktop) */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-premium lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-foreground">Operational Audit Feed</h2>
              <p className="text-xs text-muted-foreground">Real-time lifecycle modifications logged</p>
            </div>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2">
            {activities && activities.length > 0 ? (
              activities.slice(0, 8).map((act) => (
                <div key={act.id} className="flex gap-4 items-start border-b border-border pb-3 last:border-0 last:pb-0">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted text-xs font-bold uppercase">
                    {act.user_details?.username?.substring(0, 2) || "SY"}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-foreground">{act.description}</p>
                    <span className="text-[10px] text-muted-foreground">
                      {new Date(act.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted-foreground text-center py-6">
                No recent activity reports generated.
              </p>
            )}
          </div>
        </div>

        {/* Pending Tasks list */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-premium">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-foreground">Assigned Tasks</h2>
              <p className="text-xs text-muted-foreground">Pending agent action items</p>
            </div>
            <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-[10px] font-bold text-amber-500">
              {pendingTasks} Due
            </span>
          </div>
          <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
            {tasks && tasks.filter((t) => !t.completed).length > 0 ? (
              tasks
                .filter((t) => !t.completed)
                .slice(0, 5)
                .map((task) => (
                  <div key={task.id} className="flex items-center justify-between rounded-lg bg-muted/30 p-3 border border-border/50">
                    <div>
                      <p className="text-xs font-semibold text-foreground truncate max-w-[150px]">
                        {task.title}
                      </p>
                      <span className="text-[10px] text-muted-foreground">
                        {task.due_date ? new Date(task.due_date).toLocaleDateString() : "No due date"}
                      </span>
                    </div>
                    <span className="text-[9px] uppercase tracking-wider font-bold text-muted-foreground">
                      Pending
                    </span>
                  </div>
                ))
            ) : (
              <p className="text-xs text-muted-foreground text-center py-8">
                All tasks are up-to-date!
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
