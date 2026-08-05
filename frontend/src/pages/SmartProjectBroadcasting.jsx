import React, { useState, useEffect, useRef, useCallback } from "react"
import {
  Radio,
  Users,
  Send,
  Calendar,
  Eye,
  TrendingUp,
  Plus,
  Edit3,
  Trash2,
  Upload,
  Download,
  Search,
  Filter,
  SortAsc,
  Settings,
  BarChart3,
  MessageSquare,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  MoreVertical,
  Copy,
  Archive,
  RotateCcw,
  Sparkles,
  Bot,
  User,
  Zap,
  FileText,
  FolderOpen,
  Image,
  File,
  Tag,
  MapPin,
  DollarSign,
  Building2,
  Home,
  Activity,
  History,
  Wrench,
  FlaskConical,
  ClipboardList,
  Inbox,
  Mail,
  Phone,
  Globe,
  Link,
  Hash,
  Type,
  AlignLeft,
  Bold,
  Italic,
  Underline,
  Play,
  Pause,
  Repeat,
  Shuffle,
  Bell,
  BellOff,
  Timer,
  CalendarDays,
  CalendarClock,
  MailOpen,
  MailPlus,
  MailCheck,
  MailX,
  PhoneCall,
  PhoneForwarded,
  PhoneMissed,
  MessageCircle,
  MessagesSquare,
  SendHorizonal,
  Check,
  CheckCircle2,
  CheckSquare,
  X,
  XOctagon,
  AlertCircle,
  AlertOctagon,
  Info,
  Star,
  StarHalf,
  Heart,
  HeartPulse,
  ThumbsUp,
  ThumbsDown,
  Flag,
  Pin,
  PinOff,
  Lock,
  Unlock,
  Shield,
  ShieldCheck,
  ShieldAlert,
  Key,
  KeyRound,
  Fingerprint,
  Scan,
  QrCode,
  Barcode,
  Tags,
  Gift,
  Trophy,
  Medal,
  Award,
  Crown,
  Gem,
  Rocket,
  Plane,
  PlaneTakeoff,
  PlaneLanding,
  Train,
  TrainFront,
  Car,
  Bus,
  BusFront,
  Truck,
  Ship,
  Map,
  MapPinned,
  Compass,
  Navigation,
  Route,
  Earth,
  EarthLock,
  Wifi,
  WifiOff,
  Signal,
  Antenna,
  Tv,
  Monitor,
  Laptop,
  Tablet,
  Headphones,
  Speaker,
  Mic,
  MicOff,
  Volume,
  VolumeOff,
  Music,
  PlayCircle,
  PlaySquare,
  PauseCircle,
  StopCircle,
  RepeatOff,
  Equal,
  Minimize,
  Maximize,
  Minimize2,
  Maximize2,
  Expand,
  Fullscreen,
  ZoomIn,
  ZoomOut,
  Focus,
  Crosshair,
  Target,
} from "lucide-react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "../api/client"

const STATUS_COLORS = {
  Active: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  Scheduled: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  Completed: "bg-muted text-muted-foreground",
  Draft: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
  Failed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  Running: "bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400",
  Paused: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  Cancelled: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
}

export default function SmartProjectBroadcasting() {
  const queryClient = useQueryClient()
  const bcRef = useRef(null)

  const [activeSection, setActiveSection] = useState("dashboard")
  const [campaigns, setCampaigns] = useState([])
  const [teamMembers, setTeamMembers] = useState([])
  const [selectedCampaign, setSelectedCampaign] = useState(null)
  const [showNewCampaign, setShowNewCampaign] = useState(false)
  const [newCampaignStep, setNewCampaignStep] = useState(1)
  const [campaignForm, setCampaignForm] = useState({})
  const [aiPrompt, setAiPrompt] = useState("")
  const [aiGeneratedContent, setAiGeneratedContent] = useState({})
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [toast, setToast] = useState(null)

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3500)
  }, [])

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
  }, [activeSection])

  const { data: campaignsData = [] } = useQuery({
    queryKey: ["broadcastCampaigns", searchQuery, statusFilter],
    queryFn: () => api.get("/api/broadcast/campaigns/", { params: { search: searchQuery, status: statusFilter } }).then((res) => res.data.results || res.data),
    placeholderData: (previousData) => previousData,
  })

  const { data: stats = {} } = useQuery({
    queryKey: ["broadcastStats"],
    queryFn: () => api.get("/api/broadcast/campaigns/stats/").then((res) => res.data),
  })

  const { data: teamData = [] } = useQuery({
    queryKey: ["broadcastTeam"],
    queryFn: () => api.get("/api/employees/").then((res) => res.data.results || res.data),
  })

  const { data: audienceData = [] } = useQuery({
    queryKey: ["broadcastAudience"],
    queryFn: () => api.get("/api/broadcast/audience-segments/").then((res) => res.data.results || res.data),
  })

  const { data: contactListsData = [] } = useQuery({
    queryKey: ["broadcastContactLists"],
    queryFn: () => api.get("/api/broadcast/contact-lists/").then((res) => res.data.results || res.data),
  })

  const { data: templatesData = [] } = useQuery({
    queryKey: ["broadcastTemplates"],
    queryFn: () => api.get("/api/broadcast/templates/").then((res) => res.data.results || res.data),
  })

  const createCampaignMutation = useMutation({
    mutationFn: (data) => api.post("/api/broadcast/campaigns/", data),
    onSuccess: () => {
      queryClient.invalidateQueries(["broadcastCampaigns"])
      queryClient.invalidateQueries(["broadcastStats"])
      setShowNewCampaign(false)
      setNewCampaignStep(1)
      setCampaignForm({})
      showToast("Campaign created successfully", "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Failed to create campaign", "error"),
  })

  const sendCampaignMutation = useMutation({
    mutationFn: ({ campaignId, data }) => api.post(`/api/broadcast/campaigns/${campaignId}/send/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries(["broadcastCampaigns"])
      showToast("Campaign sent successfully", "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Failed to send campaign", "error"),
  })

  const scheduleCampaignMutation = useMutation({
    mutationFn: ({ campaignId, data }) => api.post(`/api/broadcast/campaigns/${campaignId}/schedule/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries(["broadcastCampaigns"])
      showToast("Campaign scheduled successfully", "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Failed to schedule campaign", "error"),
  })

  const deleteCampaignMutation = useMutation({
    mutationFn: (id) => api.delete(`/api/broadcast/campaigns/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries(["broadcastCampaigns"])
      queryClient.invalidateQueries(["broadcastStats"])
      showToast("Campaign deleted", "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Failed to delete campaign", "error"),
  })

  const handleCreateCampaign = () => {
    createCampaignMutation.mutate(campaignForm)
  }

  const handleSendCampaign = (campaign) => {
    sendCampaignMutation.mutate({ campaignId: campaign.id, data: { message: "Campaign message" } })
  }

  const handleScheduleCampaign = (campaign) => {
    scheduleCampaignMutation.mutate({ campaignId: campaign.id, data: { schedule_time: new Date().toISOString() } })
  }

  const filteredCampaigns = (campaignsData || []).filter((c) => {
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      if (!(c.name || "").toLowerCase().includes(q)) return false
    }
    if (statusFilter && c.status !== statusFilter) return false
    return true
  })

  const sectionNav = [
    { key: "dashboard", label: "Dashboard", icon: Radio },
    { key: "new-campaign", label: "New Campaign", icon: Plus },
    { key: "active-campaigns", label: "Active Campaigns", icon: Activity },
    { key: "audience", label: "Audience Manager", icon: Users },
    { key: "contact-lists", label: "Contact Lists", icon: Inbox },
    { key: "templates", label: "Templates", icon: FileText },
    { key: "ai-studio", label: "AI Campaign Studio", icon: Sparkles },
    { key: "analytics", label: "Campaign Analytics", icon: BarChart3 },
    { key: "delivery-logs", label: "Delivery Logs", icon: ClipboardList },
    { key: "scheduled", label: "Scheduled Campaigns", icon: Calendar },
    { key: "team-broadcast", label: "Team Broadcast", icon: Users },
    { key: "imports", label: "Imports", icon: Upload },
    { key: "integrations", label: "Integrations", icon: Link },
    { key: "settings", label: "Settings", icon: Settings },
  ]

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={bcRef}>
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1920&h=1080&fit=crop"
          alt="Modern Real Estate Building"
          className="w-full h-full object-cover opacity-25"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/85 via-background/50 to-background/85" />
      </div>

      <div className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `radial-gradient(circle at center, hsl(180 80% 60%) 1px, transparent 1px)`,
          backgroundSize: '80px 80px',
        }}
      />

      <div className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-teal-400/20 blur-[100px] animate-pulse" />
      <div className="absolute top-1/3 -right-32 h-80 w-80 rounded-full bg-amber-500/15 blur-[100px] animate-pulse" style={{ animationDelay: "1s" }} />
      <div className="absolute bottom-0 left-1/4 h-64 w-64 rounded-full bg-emerald-500/10 blur-[80px] animate-pulse" style={{ animationDelay: "2s" }} />

      <div className="relative z-10 mx-auto max-w-7xl px-6 pt-8 pb-16 lg:px-12 space-y-8">

        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between animate-fade-in">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground">
              <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">Smart Project Broadcasting</span>
            </h1>
            <p className="text-muted-foreground text-sm mt-2">
              AI-powered campaign management — find audience, generate content, broadcast, track, learn.
            </p>
          </div>
          <button
            onClick={() => setShowNewCampaign(true)}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all duration-300 hover:-translate-y-1"
          >
            <Plus className="h-4 w-4" /> New Campaign
          </button>
        </div>

        <div className="flex flex-col lg:flex-row gap-6">

          <div className="lg:w-64 shrink-0">
            <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-4 backdrop-blur-md">
              <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10 space-y-1">
                {sectionNav.map((item) => {
                  const Icon = item.icon
                  const isActive = activeSection === item.key
                  return (
                    <button
                      key={item.key}
                      onClick={() => setActiveSection(item.key)}
                      className={`w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-semibold transition-all duration-200 ${
                        isActive
                          ? "bg-teal-500/10 text-teal-600 border-l-2 border-teal-500"
                          : "text-muted-foreground hover:text-foreground hover:bg-muted/30 border-l-2 border-transparent"
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </button>
                  )
                })}
              </div>
            </div>
          </div>

          <div className="flex-1 min-w-0">

            {activeSection === "dashboard" && (
              <div className="space-y-6 animate-fade-in">
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                  {[
                    { label: "Total Campaigns", value: stats.total || campaignsData.length, icon: Radio, color: "teal" },
                    { label: "Running", value: stats.running || 0, icon: Activity, color: "emerald" },
                    { label: "Scheduled", value: stats.scheduled || 0, icon: Calendar, color: "blue" },
                    { label: "Completed", value: stats.completed || 0, icon: CheckCircle, color: "emerald" },
                    { label: "Failed", value: stats.failed || 0, icon: XCircle, color: "red" },
                    { label: "Draft", value: stats.draft || 0, icon: FileText, color: "slate" },
                    { label: "Messages Sent", value: stats.messages_sent || 0, icon: Send, color: "teal" },
                    { label: "Delivery Rate", value: `${stats.delivery_rate || 0}%`, icon: TrendingUp, color: "emerald" },
                    { label: "Open Rate", value: `${stats.open_rate || 0}%`, icon: Eye, color: "amber" },
                    { label: "Bookings", value: stats.bookings || 0, icon: Trophy, color: "amber" },
                  ].map((stat, i) => {
                    const Icon = stat.icon
                    const colorMap = {
                      teal: "bg-teal-500/10 text-teal-500",
                      emerald: "bg-emerald-500/10 text-emerald-500",
                      blue: "bg-blue-500/10 text-blue-500",
                      red: "bg-red-500/10 text-red-500",
                      slate: "bg-slate-500/10 text-slate-500",
                      amber: "bg-amber-500/10 text-amber-500",
                    }
                    return (
                      <div
                        key={stat.label}
                        className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-premiumDark animate-fade-in overflow-hidden"
                        style={{ animationDelay: `${i * 0.05}s` }}
                      >
                        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                        <div className="relative z-10">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">{stat.label}</span>
                            <div className={`flex h-9 w-9 items-center justify-center rounded-xl ${colorMap[stat.color]} transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6`}>
                              <Icon className="h-4 w-4" />
                            </div>
                          </div>
                          <p className="mt-3 text-2xl font-extrabold text-foreground">{stat.value}</p>
                        </div>
                      </div>
                    )
                  })}
                </div>

                <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in" style={{ animationDelay: "0.2s" }}>
                  <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                  <div className="relative z-10">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-sm font-extrabold text-foreground flex items-center gap-2">
                        <Activity className="h-4 w-4 text-teal-500" /> Active Campaigns
                      </h2>
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          placeholder="Search campaigns..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="rounded-lg border border-border bg-muted/30 px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500"
                        />
                        <select
                          value={statusFilter}
                          onChange={(e) => setStatusFilter(e.target.value)}
                          className="rounded-lg border border-border bg-muted/30 px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500"
                        >
                          <option value="">All Statuses</option>
                          <option value="Active">Active</option>
                          <option value="Scheduled">Scheduled</option>
                          <option value="Running">Running</option>
                          <option value="Completed">Completed</option>
                          <option value="Draft">Draft</option>
                          <option value="Failed">Failed</option>
                          <option value="Paused">Paused</option>
                        </select>
                      </div>
                    </div>
                    {filteredCampaigns.length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-8">No campaigns found.</p>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full border-collapse text-left text-sm">
                          <thead className="bg-muted/40 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                            <tr>
                              <th className="px-4 py-3">Campaign</th>
                              <th className="px-4 py-3">Type</th>
                              <th className="px-4 py-3">Status</th>
                              <th className="px-4 py-3">Audience</th>
                              <th className="px-4 py-3">Channels</th>
                              <th className="px-4 py-3">Reach</th>
                              <th className="px-4 py-3">Date</th>
                              <th className="px-4 py-3">Actions</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-border">
                            {filteredCampaigns.map((campaign) => (
                              <tr key={campaign.id} className="hover:bg-muted/20 transition-colors">
                                <td className="px-4 py-3 font-semibold text-foreground">{campaign.name}</td>
                                <td className="px-4 py-3 text-xs text-muted-foreground">{campaign.campaign_type?.replace("_", " ") || "General"}</td>
                                <td className="px-4 py-3">
                                  <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${STATUS_COLORS[campaign.status] || STATUS_COLORS.Draft}`}>
                                    {campaign.status}
                                  </span>
                                </td>
                                <td className="px-4 py-3 text-xs text-muted-foreground">{campaign.total_reach || 0}</td>
                                <td className="px-4 py-3">
                                  <div className="flex flex-wrap gap-1">
                                    {(campaign.channels || []).map((ch, i) => (
                                      <span key={i} className="rounded-full bg-teal-500/10 px-2 py-0.5 text-[10px] font-bold text-teal-600">{ch}</span>
                                    ))}
                                  </div>
                                </td>
                                <td className="px-4 py-3 text-xs text-muted-foreground">{campaign.delivered || 0} delivered</td>
                                <td className="px-4 py-3 text-xs text-muted-foreground">{campaign.created_at ? new Date(campaign.created_at).toLocaleDateString() : "N/A"}</td>
                                <td className="px-4 py-3">
                                  <div className="flex items-center gap-1">
                                    <button onClick={() => setSelectedCampaign(campaign)} className="rounded-lg p-1.5 text-muted-foreground hover:text-teal-500 hover:bg-teal-500/10 transition-all" title="View">
                                      <Eye className="h-3.5 w-3.5" />
                                    </button>
                                    <button onClick={() => handleSendCampaign(campaign)} className="rounded-lg p-1.5 text-muted-foreground hover:text-emerald-500 hover:bg-emerald-500/10 transition-all" title="Send">
                                      <Send className="h-3.5 w-3.5" />
                                    </button>
                                    <button onClick={() => handleScheduleCampaign(campaign)} className="rounded-lg p-1.5 text-muted-foreground hover:text-blue-500 hover:bg-blue-500/10 transition-all" title="Schedule">
                                      <Calendar className="h-3.5 w-3.5" />
                                    </button>
                                    <button onClick={() => { if (window.confirm(`Delete "${campaign.name}"?`)) deleteCampaignMutation.mutate(campaign.id) }} className="rounded-lg p-1.5 text-muted-foreground hover:text-red-500 hover:bg-red-500/10 transition-all" title="Delete">
                                      <Trash2 className="h-3.5 w-3.5" />
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeSection === "new-campaign" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-extrabold text-foreground flex items-center gap-2">
                      <Plus className="h-5 w-5 text-teal-500" /> New Campaign
                    </h2>
                    <button onClick={() => { setShowNewCampaign(false); setNewCampaignStep(1); setCampaignForm({}) }} className="rounded-lg p-2 text-muted-foreground hover:text-foreground hover:bg-muted transition-all">
                      <X className="h-5 w-5" />
                    </button>
                  </div>

                  <div className="flex items-center gap-2 mb-6">
                    {[1, 2, 3, 4, 5].map((step) => (
                      <React.Fragment key={step}>
                        <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${newCampaignStep >= step ? "bg-teal-500 text-white" : "bg-muted text-muted-foreground"}`}>
                          {step}
                        </div>
                        {step < 5 && <div className={`flex-1 h-0.5 ${newCampaignStep > step ? "bg-teal-500" : "bg-muted"}`} />}
                      </React.Fragment>
                    ))}
                  </div>

                  {newCampaignStep === 1 && (
                    <div className="space-y-4">
                      <h3 className="text-sm font-bold text-foreground">Campaign Type</h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {["PROJECT_LAUNCH", "PRICE_UPDATE", "FESTIVAL_OFFER", "INVENTORY_UPDATE", "GENERAL_ANNOUNCEMENT", "CUSTOM"].map((type) => (
                          <button
                            key={type}
                            onClick={() => setCampaignForm((prev) => ({ ...prev, campaign_type: type }))}
                            className={`rounded-xl border p-4 text-left transition-all ${campaignForm.campaign_type === type ? "border-teal-500 bg-teal-500/10" : "border-border bg-muted/20 hover:border-teal-500/50"}`}
                          >
                            <p className="text-xs font-semibold text-foreground">{type.replace("_", " ")}</p>
                          </button>
                        ))}
                      </div>
                      <div className="flex justify-end pt-2">
                        <button onClick={() => setNewCampaignStep(2)} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all">
                          Next
                        </button>
                      </div>
                    </div>
                  )}

                  {newCampaignStep === 2 && (
                    <div className="space-y-4">
                      <h3 className="text-sm font-bold text-foreground">Choose Project</h3>
                      <input
                        type="text"
                        placeholder="Search project..."
                        value={campaignForm.project_search || ""}
                        onChange={(e) => setCampaignForm((prev) => ({ ...prev, project_search: e.target.value }))}
                        className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500"
                      />
                      <p className="text-xs text-muted-foreground">AI will load project details automatically when you select a project.</p>
                      <div className="flex justify-between pt-2">
                        <button onClick={() => setNewCampaignStep(1)} className="rounded-xl border border-border bg-muted/20 px-5 py-2.5 text-sm font-semibold text-muted-foreground hover:text-foreground transition-all">Back</button>
                        <button onClick={() => setNewCampaignStep(3)} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all">Next</button>
                      </div>
                    </div>
                  )}

                  {newCampaignStep === 3 && (
                    <div className="space-y-4">
                      <h3 className="text-sm font-bold text-foreground">Audience</h3>
                      <div className="space-y-2">
                        {["Customers", "Sales Team", "Channel Partners", "Custom CSV", "Manual Contacts", "Saved Audience", "AI Matching"].map((audience) => (
                          <label key={audience} className="flex items-center gap-3 rounded-xl border border-border bg-muted/20 px-4 py-3 cursor-pointer hover:bg-muted/30 transition-all">
                            <input type="checkbox" className="rounded border-border text-teal-500 focus:ring-teal-500" />
                            <span className="text-sm font-medium text-foreground">{audience}</span>
                          </label>
                        ))}
                      </div>
                      <div className="flex justify-between pt-2">
                        <button onClick={() => setNewCampaignStep(2)} className="rounded-xl border border-border bg-muted/20 px-5 py-2.5 text-sm font-semibold text-muted-foreground hover:text-foreground transition-all">Back</button>
                        <button onClick={() => setNewCampaignStep(4)} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all">Next</button>
                      </div>
                    </div>
                  )}

                  {newCampaignStep === 4 && (
                    <div className="space-y-4">
                      <h3 className="text-sm font-bold text-foreground">AI Campaign Studio</h3>
                      <textarea
                        value={aiPrompt}
                        onChange={(e) => setAiPrompt(e.target.value)}
                        placeholder="Launch Palm Residency to customers interested in 3 BHK under ₹1 Cr in Ahmedabad..."
                        rows={4}
                        className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 resize-none"
                      />
                      <button
                        onClick={() => setAiGeneratedContent((prev) => ({ ...prev, whatsapp: "Hi there! Check out our new campaign." }))}
                        disabled={!aiPrompt.trim()}
                        className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all disabled:opacity-50"
                      >
                        <Sparkles className="h-3 w-3" /> Generate Content
                      </button>
                      <div className="flex justify-between pt-2">
                        <button onClick={() => setNewCampaignStep(3)} className="rounded-xl border border-border bg-muted/20 px-5 py-2.5 text-sm font-semibold text-muted-foreground hover:text-foreground transition-all">Back</button>
                        <button onClick={() => setNewCampaignStep(5)} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all">Next</button>
                      </div>
                    </div>
                  )}

                  {newCampaignStep === 5 && (
                    <div className="space-y-4">
                      <h3 className="text-sm font-bold text-foreground">Channels & Schedule</h3>
                      <div className="space-y-2">
                        {["WhatsApp", "Email", "SMS", "Push Notification", "Sales Team", "CRM Notification"].map((channel) => (
                          <label key={channel} className="flex items-center gap-3 rounded-xl border border-border bg-muted/20 px-4 py-3 cursor-pointer hover:bg-muted/30 transition-all">
                            <input type="checkbox" className="rounded border-border text-teal-500 focus:ring-teal-500" />
                            <span className="text-sm font-medium text-foreground">{channel}</span>
                          </label>
                        ))}
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Schedule</label>
                          <select className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500">
                            <option>Send Now</option>
                            <option>Schedule</option>
                            <option>Recurring</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Time Zone</label>
                          <input type="text" defaultValue="Asia/Kolkata" className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500" />
                        </div>
                      </div>
                      <div className="flex justify-between pt-2">
                        <button onClick={() => setNewCampaignStep(4)} className="rounded-xl border border-border bg-muted/20 px-5 py-2.5 text-sm font-semibold text-muted-foreground hover:text-foreground transition-all">Back</button>
                        <button onClick={handleCreateCampaign} disabled={createCampaignMutation.isPending} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all disabled:opacity-50">
                          {createCampaignMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mx-auto" /> : "Create Campaign"}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeSection === "audience" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <Users className="h-4 w-4 text-teal-500" /> Audience Manager
                  </h2>
                  <div className="flex items-center gap-3 mb-4">
                    <input type="text" placeholder="Search audience..." className="flex-1 rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500" />
                    <button className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-4 py-2.5 text-xs font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all">
                      <Plus className="h-3 w-3" /> New Segment
                    </button>
                  </div>
                  <div className="space-y-3">
                    {audienceData.map((segment) => (
                      <div key={segment.id} className="flex items-center justify-between rounded-xl border border-border bg-muted/20 px-4 py-3">
                        <div>
                          <p className="text-sm font-semibold text-foreground">{segment.name}</p>
                          <p className="text-xs text-muted-foreground">{segment.segment_type} • {segment.customer_count} contacts</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <button className="rounded-lg p-1.5 text-muted-foreground hover:text-teal-500 hover:bg-teal-500/10 transition-all"><Edit3 className="h-3.5 w-3.5" /></button>
                          <button className="rounded-lg p-1.5 text-muted-foreground hover:text-red-500 hover:bg-red-500/10 transition-all"><Trash2 className="h-3.5 w-3.5" /></button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeSection === "contact-lists" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <Inbox className="h-4 w-4 text-teal-500" /> Contact Lists
                  </h2>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {contactListsData.map((list) => (
                      <div key={list.id} className="rounded-xl border border-border bg-muted/20 p-4 hover:border-teal-500/30 transition-all">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-bold text-foreground">{list.name}</h3>
                          <span className="text-[10px] bg-teal-500/10 text-teal-600 px-2 py-0.5 rounded-lg font-bold">{list.contacts?.length || 0} contacts</span>
                        </div>
                        <p className="text-xs text-muted-foreground">{list.description || "No description"}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {(list.tags || []).map((tag, i) => (
                            <span key={i} className="rounded-full bg-amber-500/10 px-2 py-0.5 text-[10px] font-bold text-amber-600">{tag}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeSection === "templates" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <FileText className="h-4 w-4 text-teal-500" /> Templates
                  </h2>
                  <div className="space-y-3">
                    {templatesData.map((template) => (
                      <div key={template.id} className="flex items-center justify-between rounded-xl border border-border bg-muted/20 px-4 py-3">
                        <div>
                          <p className="text-sm font-semibold text-foreground">{template.name}</p>
                          <p className="text-xs text-muted-foreground">{template.template_type} • {template.language}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <button className="rounded-lg p-1.5 text-muted-foreground hover:text-teal-500 hover:bg-teal-500/10 transition-all"><Edit3 className="h-3.5 w-3.5" /></button>
                          <button className="rounded-lg p-1.5 text-muted-foreground hover:text-red-500 hover:bg-red-500/10 transition-all"><Trash2 className="h-3.5 w-3.5" /></button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeSection === "ai-studio" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-amber-500" /> AI Campaign Studio
                  </h2>
                  <textarea
                    value={aiPrompt}
                    onChange={(e) => setAiPrompt(e.target.value)}
                    placeholder="Launch Palm Residency to customers interested in 3 BHK under ₹1 Cr in Ahmedabad..."
                    rows={4}
                    className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 resize-none mb-4"
                  />
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                    {["whatsapp", "email", "sms", "push", "sales_script", "voice_script", "facebook", "instagram"].map((type) => (
                      <button
                        key={type}
                        onClick={() => setAiGeneratedContent((prev) => ({ ...prev, [type]: `Generated ${type} content for campaign.` }))}
                        disabled={!aiPrompt.trim()}
                        className="rounded-xl border border-border bg-muted/20 px-3 py-3 text-xs font-semibold text-foreground hover:border-teal-500/50 hover:bg-teal-500/5 transition-all disabled:opacity-50"
                      >
                        {type.replace("_", " ")}
                      </button>
                    ))}
                  </div>
                  {Object.entries(aiGeneratedContent).map(([type, content]) => (
                    <div key={type} className="rounded-xl border border-border bg-muted/20 p-4 mb-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-foreground uppercase tracking-wider">{type}</span>
                        <button onClick={() => navigator.clipboard.writeText(content)} className="text-xs text-teal-500 hover:text-teal-600">Copy</button>
                      </div>
                      <p className="text-xs text-foreground/80 whitespace-pre-wrap">{content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeSection === "analytics" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-teal-500" /> Campaign Analytics
                  </h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    {[
                      { label: "Delivered", value: stats.delivered || 0, color: "teal" },
                      { label: "Opened", value: stats.opened || 0, color: "blue" },
                      { label: "Clicked", value: stats.clicked || 0, color: "amber" },
                      { label: "Replied", value: stats.replied || 0, color: "emerald" },
                      { label: "Interested", value: stats.interested || 0, color: "teal" },
                      { label: "Site Visits", value: stats.site_visits || 0, color: "emerald" },
                      { label: "Calls Booked", value: stats.calls_booked || 0, color: "amber" },
                      { label: "Meetings", value: stats.meetings || 0, color: "blue" },
                      { label: "Bookings", value: stats.bookings || 0, color: "emerald" },
                      { label: "Revenue", value: `₹${stats.revenue || 0}`, color: "teal" },
                    ].map((stat) => (
                      <div key={stat.label} className="rounded-xl border border-border bg-muted/20 p-4">
                        <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{stat.label}</p>
                        <p className="text-lg font-extrabold text-foreground">{stat.value}</p>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground text-center py-8">Select a campaign to view detailed analytics.</p>
                </div>
              </div>
            )}

            {activeSection === "delivery-logs" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <ClipboardList className="h-4 w-4 text-teal-500" /> Delivery Logs
                  </h2>
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse text-left text-sm">
                      <thead className="bg-muted/40 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        <tr>
                          <th className="px-4 py-3">Name</th>
                          <th className="px-4 py-3">Phone</th>
                          <th className="px-4 py-3">Channel</th>
                          <th className="px-4 py-3">Status</th>
                          <th className="px-4 py-3">Delivered</th>
                          <th className="px-4 py-3">Opened</th>
                          <th className="px-4 py-3">Clicked</th>
                          <th className="px-4 py-3">Failed</th>
                          <th className="px-4 py-3">Reason</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        <tr>
                          <td className="px-4 py-3 text-sm text-foreground">Sample Customer</td>
                          <td className="px-4 py-3 text-xs text-muted-foreground">+91xxxxxxxxxx</td>
                          <td className="px-4 py-3"><span className="rounded-full px-2 py-0.5 text-[10px] font-bold bg-green-100 text-green-700">WhatsApp</span></td>
                          <td className="px-4 py-3"><span className="rounded-full px-2 py-0.5 text-[10px] font-bold bg-emerald-100 text-emerald-700">Delivered</span></td>
                          <td className="px-4 py-3 text-xs text-emerald-500">Yes</td>
                          <td className="px-4 py-3 text-xs text-amber-500">Yes</td>
                          <td className="px-4 py-3 text-xs text-muted-foreground">No</td>
                          <td className="px-4 py-3 text-xs text-red-500">No</td>
                          <td className="px-4 py-3 text-xs text-muted-foreground">-</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {activeSection === "scheduled" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-blue-500" /> Scheduled Campaigns
                  </h2>
                  <p className="text-sm text-muted-foreground text-center py-8">No scheduled campaigns.</p>
                </div>
              </div>
            )}

            {activeSection === "team-broadcast" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <Users className="h-4 w-4 text-teal-500" /> Team Members
                  </h2>
                  <div className="space-y-3">
                    {teamData.map((member) => (
                      <div key={member.id} className="flex items-center justify-between rounded-xl border border-border bg-muted/20 px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500/10 to-amber-500/10 text-teal-500">
                            <User className="h-5 w-5" />
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-foreground">{member.first_name} {member.last_name}</p>
                            <p className="text-xs text-muted-foreground">{member.job_title || "Employee"}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-xs text-muted-foreground">{member.phone || "N/A"}</span>
                          <span className="text-xs text-muted-foreground">{member.email || "N/A"}</span>
                          <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold ${member.status === "ACTIVE" ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-700"}`}>
                            <span className={`h-1.5 w-1.5 rounded-full ${member.status === "ACTIVE" ? "bg-emerald-500" : "bg-gray-400"}`} />
                            {member.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeSection === "imports" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <Upload className="h-4 w-4 text-teal-500" /> Imports
                  </h2>
                  <div className="border-2 border-dashed border-border rounded-2xl p-8 text-center hover:border-teal-500/50 transition-colors">
                    <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-3" />
                    <p className="text-sm font-semibold text-foreground">Drop files here or click to upload</p>
                    <p className="text-xs text-muted-foreground mt-1">Supports CSV, Excel, ZIP, Google Sheet Import</p>
                  </div>
                  <div className="mt-4 space-y-2">
                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Supported Formats</p>
                    <div className="flex flex-wrap gap-2">
                      {["CSV", "Excel", "ZIP", "Google Sheet"].map((fmt) => (
                        <span key={fmt} className="rounded-full bg-teal-500/10 px-3 py-1 text-[10px] font-bold text-teal-600">{fmt}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeSection === "integrations" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <Link className="h-4 w-4 text-teal-500" /> Integrations
                  </h2>
                  <div className="space-y-3">
                    {["WhatsApp Business", "Email Service", "SMS Gateway", "Push Notification", "CRM", "Google Sheets"].map((integration) => (
                      <div key={integration} className="flex items-center justify-between rounded-xl border border-border bg-muted/20 px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-500/10 text-teal-500">
                            <Link className="h-4 w-4" />
                          </div>
                          <span className="text-sm font-semibold text-foreground">{integration}</span>
                        </div>
                        <span className="text-xs text-emerald-500 font-semibold">Connected</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeSection === "settings" && (
              <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in">
                <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <h2 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
                    <Settings className="h-4 w-4 text-teal-500" /> Settings
                  </h2>
                  <p className="text-sm text-muted-foreground">Broadcast settings configuration.</p>
                </div>
              </div>
            )}

          </div>
        </div>

        {toast && (
          <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-2xl border border-border bg-card/90 backdrop-blur-xl px-5 py-3 shadow-2xl animate-fade-in">
            {toast.type === "success" ? (
              <CheckCircle className="h-5 w-5 text-emerald-500" />
            ) : toast.type === "error" ? (
              <AlertCircle className="h-5 w-5 text-red-500" />
            ) : (
              <Info className="h-5 w-5 text-teal-500" />
            )}
            <p className={`text-sm font-semibold ${toast.type === "error" ? "text-red-500" : toast.type === "success" ? "text-emerald-500" : "text-foreground"}`}>
              {toast.message}
            </p>
          </div>
        )}

      </div>
    </div>
  )
}
