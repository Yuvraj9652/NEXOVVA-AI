import React, { useState, useEffect, useRef, useCallback } from "react"
import {
  FileText,
  FolderOpen,
  Search,
  Filter,
  SortAsc,
  Plus,
  Edit3,
  Trash2,
  Upload,
  Download,
  Eye,
  Settings,
  BarChart3,
  MessageSquare,
  Send,
  X,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  CheckCircle,
  Clock,
  Tag,
  Image,
  File,
  Archive,
  RotateCcw,
  Copy,
  Sparkles,
  Bot,
  User,
  Zap,
  Grid3X3,
  List,
  SlidersHorizontal,
  ArrowUpDown,
  BookOpen,
  Palette,
  MapPin,
  DollarSign,
  Home,
  Building2,
  Layers,
  Activity,
  History,
  Wrench,
  FlaskConical,
  ClipboardList,
  Inbox,
  MoreVertical,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Ban,
  Check,
  XCircle,
  AlertTriangle,
  Info,
  Star,
  TrendingUp,
  Users,
  EyeOff,
} from "lucide-react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "../api/client"

const STATUS_COLORS = {
  PAST: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
  ONGOING: "bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400",
  UPCOMING: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  DRAFT: "bg-muted text-muted-foreground",
  ARCHIVED: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
}

const STATUS_BORDER_COLORS = {
  PAST: "border-l-slate-500",
  ONGOING: "border-l-teal-500",
  UPCOMING: "border-l-amber-500",
  DRAFT: "border-l-muted-foreground",
  ARCHIVED: "border-l-red-500",
}

const STATUS_DOT_COLORS = {
  PAST: "bg-slate-500",
  ONGOING: "bg-teal-500",
  UPCOMING: "bg-amber-500",
  DRAFT: "bg-muted-foreground",
  ARCHIVED: "bg-red-500",
}

const STATUS_ICONS = {
  PAST: Clock,
  ONGOING: Activity,
  UPCOMING: Star,
  DRAFT: FileText,
  ARCHIVED: Archive,
}

const JOB_STATUS_COLORS = {
  PENDING: "text-amber-500",
  PROCESSING: "text-teal-500",
  COMPLETED: "text-emerald-500",
  FAILED: "text-red-500",
}

const JOB_STATUS_ICONS = {
  PENDING: Clock,
  PROCESSING: RefreshCw,
  COMPLETED: CheckCircle,
  FAILED: XCircle,
}

function formatPrice(price) {
  if (!price) return "N/A"
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(price)
}

function formatDate(dateStr) {
  if (!dateStr) return "N/A"
  return new Date(dateStr).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })
}

function truncate(str, len = 80) {
  if (!str) return ""
  return str.length > len ? str.slice(0, len) + "..." : str
}

function getStatusLabel(status) {
  const labels = { ONGOING: "Ongoing", PAST: "Past", UPCOMING: "Upcoming", DRAFT: "Draft", ARCHIVED: "Archived" }
  return labels[status] || status
}

export default function ProjectKnowledgeBase() {
  const queryClient = useQueryClient()
  const kbRef = useRef(null)
  const detailRef = useRef(null)

  const [view, setView] = useState("list")
  const [selectedProject, setSelectedProject] = useState(null)
  const [detailTab, setDetailTab] = useState("overview")
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showBulkImportModal, setShowBulkImportModal] = useState(false)
  const [showTrash, setShowTrash] = useState(false)
  const [showChatModal, setShowChatModal] = useState(false)
  const [showJobsModal, setShowJobsModal] = useState(false)
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState("")
  const [chatSessionId, setChatSessionId] = useState(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [typeFilter, setTypeFilter] = useState("")
  const [sortBy, setSortBy] = useState("newest")
  const [addStep, setAddStep] = useState(1)
  const [editStep, setEditStep] = useState(1)
  const [formData, setFormData] = useState({})
  const [editData, setEditData] = useState({})
  const [importFiles, setImportFiles] = useState([])
  const [bulkImportResults, setBulkImportResults] = useState(null)
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
  }, [view, selectedProject])

  const { data: projects = [], isLoading: projectsLoading, refetch: refetchProjects } = useQuery({
    queryKey: ["knowledgeBaseProjects", searchQuery, statusFilter, typeFilter, sortBy],
    queryFn: () => {
      const params = new URLSearchParams()
      if (searchQuery) params.set("search", searchQuery)
      if (statusFilter) params.set("status", statusFilter)
      if (typeFilter) params.set("property_type", typeFilter)
      return api.get("/api/knowledge-base/", { params }).then((res) => res.data.results || res.data)
    },
    placeholderData: (previousData) => previousData,
    refetchInterval: 30000,
  })

  const { data: allProjects = [] } = useQuery({
    queryKey: ["allKnowledgeBaseProjects"],
    queryFn: () => api.get("/api/knowledge-base/").then((res) => res.data.results || res.data),
    refetchInterval: 30000,
  })

  const { data: stats = {} } = useQuery({
    queryKey: ["knowledgeBaseStats"],
    queryFn: () => api.get("/api/knowledge-base/stats/").then((res) => res.data),
  })

  const dynamicStats = {
    total: stats.total ?? allProjects.length ?? projects.length,
    ongoing: stats.ongoing ?? allProjects.filter((p) => p.status === "ONGOING").length,
    upcoming: stats.upcoming ?? allProjects.filter((p) => p.status === "UPCOMING").length,
    past: stats.past ?? allProjects.filter((p) => p.status === "PAST").length,
    draft: stats.draft ?? allProjects.filter((p) => p.status === "DRAFT").length,
    archived: stats.archived ?? allProjects.filter((p) => p.status === "ARCHIVED").length,
  }

  const { data: trashProjects = [] } = useQuery({
    queryKey: ["knowledgeBaseTrash"],
    queryFn: () => api.get("/api/knowledge-base/trash/").then((res) => res.data),
    enabled: showTrash,
  })

  const { data: chatSessions = [] } = useQuery({
    queryKey: ["projectChatSessions", selectedProject?.id],
    queryFn: () =>
      selectedProject
        ? api.get(`/api/knowledge-base/${selectedProject.id}/chat-sessions/`).then((res) => res.data.results || res.data)
        : [],
    enabled: !!selectedProject && showChatModal,
  })

  const invalidateAllProjectQueries = () => {
    queryClient.invalidateQueries(["knowledgeBaseProjects"])
    queryClient.invalidateQueries(["allKnowledgeBaseProjects"])
    queryClient.invalidateQueries(["knowledgeBaseStats"])
    queryClient.invalidateQueries(["knowledgeBaseTrash"])
  }

  const createProjectMutation = useMutation({
    mutationFn: (data) => api.post("/api/knowledge-base/", data),
    onSuccess: () => {
      invalidateAllProjectQueries()
      setShowAddModal(false)
      setAddStep(1)
      setFormData({})
      showToast("Project created successfully", "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Failed to create project", "error"),
  })

  const updateProjectMutation = useMutation({
    mutationFn: ({ id, data }) => api.patch(`/api/knowledge-base/${id}/`, data),
    onSuccess: () => {
      invalidateAllProjectQueries()
      setShowEditModal(false)
      setEditStep(1)
      setEditData({})
      showToast("Project updated successfully", "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Failed to update project", "error"),
  })

  const deleteProjectMutation = useMutation({
    mutationFn: (id) => api.delete(`/api/knowledge-base/${id}/`),
    onSuccess: () => {
      invalidateAllProjectQueries()
      showToast("Project archived", "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Failed to archive project", "error"),
  })

  const restoreProjectMutation = useMutation({
    mutationFn: (id) => api.post(`/api/knowledge-base/${id}/restore/`),
    onSuccess: () => {
      invalidateAllProjectQueries()
      showToast("Project restored", "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Failed to restore project", "error"),
  })

  const duplicateProjectMutation = useMutation({
    mutationFn: (id) => api.post(`/api/knowledge-base/${id}/duplicate/`),
    onSuccess: () => {
      invalidateAllProjectQueries()
      showToast("Project duplicated", "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Failed to duplicate project", "error"),
  })

  const bulkImportMutation = useMutation({
    mutationFn: (formData) => api.post("/api/knowledge-base/bulk_import/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
    onSuccess: (res) => {
      invalidateAllProjectQueries()
      setBulkImportResults(res.data)
      showToast(`Imported ${res.data.imported?.length || 0} projects`, "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "Import failed", "error"),
  })

  const aiGenerateMutation = useMutation({
    mutationFn: ({ id, type }) => api.post(`/api/knowledge-base/ai-generate/${id}/`, { type }),
    onSuccess: (res, variables) => {
      queryClient.invalidateQueries(["knowledgeBaseProjects"])
      showToast(`AI generation started for project #${variables.id}`, "success")
    },
    onError: (err) => showToast(err.response?.data?.detail || "AI generation failed", "error"),
  })

  const chatMutation = useMutation({
    mutationFn: ({ id, message }) => api.post(`/api/knowledge-base/${id}/chat/`, { message }),
    onSuccess: (res) => {
      setChatMessages((prev) => [...prev, { role: "assistant", content: res.data.response, created_at: new Date().toISOString() }])
    },
    onError: (err) => showToast(err.response?.data?.detail || "Chat failed", "error"),
  })

  const cleanPayload = (data) => {
    if (!data) return {}
    const {
      media,
      documents,
      amenities,
      tags,
      faqs,
      highlights,
      analytics,
      versions,
      created_by,
      created_at,
      updated_at,
      chat_sessions,
      processing_jobs,
      id,
      ...rest
    } = data

    const payload = { ...rest }

    if (payload.starting_price === "" || payload.starting_price === undefined || payload.starting_price === null) {
      payload.starting_price = null
    } else {
      payload.starting_price = Number(payload.starting_price)
    }

    if (payload.max_price === "" || payload.max_price === undefined || payload.max_price === null) {
      payload.max_price = null
    } else {
      payload.max_price = Number(payload.max_price)
    }

    if (!payload.status) payload.status = "DRAFT"
    return payload
  }

  const handleSelectProject = (project) => {
    setSelectedProject(project)
    setDetailTab("overview")
    setView("detail")
    setTimeout(() => {
      detailRef.current?.scrollIntoView({ behavior: "smooth" })
    }, 100)
  }

  const handleAddProject = () => {
    if (!formData.name || !formData.name.trim()) {
      showToast("Project Name is required", "error")
      return
    }
    const payload = cleanPayload(formData)
    createProjectMutation.mutate(payload)
  }

  const handleEditProject = () => {
    if (!editData.name || !editData.name.trim()) {
      showToast("Project Name is required", "error")
      return
    }
    const payload = cleanPayload(editData)
    updateProjectMutation.mutate({ id: editData.id, data: payload })
  }

  const handleBulkImport = () => {
    const fd = new FormData()
    importFiles.forEach((f) => fd.append("files", f))
    bulkImportMutation.mutate(fd)
  }

  const handleSendChat = (e) => {
    e.preventDefault()
    if (!chatInput.trim() || !selectedProject) return
    const userMsg = { role: "user", content: chatInput, created_at: new Date().toISOString() }
    setChatMessages((prev) => [...prev, userMsg])
    chatMutation.mutate({ id: selectedProject.id, message: chatInput })
    setChatInput("")
  }

  const filteredProjects = (projects || []).filter((p) => {
    if (showTrash && p.status !== "ARCHIVED") return false
    if (!showTrash && p.status === "ARCHIVED") return false
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      const match =
        (p.name || "").toLowerCase().includes(q) ||
        (p.builder || "").toLowerCase().includes(q) ||
        (p.city || "").toLowerCase().includes(q) ||
        (p.description || "").toLowerCase().includes(q)
      if (!match) return false
    }
    if (statusFilter && p.status !== statusFilter) return false
    if (typeFilter && p.property_type !== typeFilter) return false
    return true
  })

  const sortedProjects = [...filteredProjects].sort((a, b) => {
    switch (sortBy) {
      case "name_asc":
        return (a.name || "").localeCompare(b.name || "")
      case "name_desc":
        return (b.name || "").localeCompare(a.name || "")
      case "price_asc":
        return (a.starting_price || 0) - (b.starting_price || 0)
      case "price_desc":
        return (b.starting_price || 0) - (a.starting_price || 0)
      case "oldest":
        return new Date(a.created_at) - new Date(b.created_at)
      case "newest":
      default:
        return new Date(b.created_at) - new Date(a.created_at)
    }
  })

  const PropertyTypeIcon = {
    APARTMENT: Building2,
    VILLA: Home,
    PLOT: Grid3X3,
    COMMERCIAL: Building2,
    PENTHOUSE: Home,
    TOWNHOUSE: Home,
  }

  const renderStars = (rating) => {
    const stars = []
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <Star key={i} className={`h-3 w-3 ${i <= rating ? "text-amber-400 fill-amber-400" : "text-muted"}`} />
      )
    }
    return stars
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={kbRef}>
      {/* Static Background Image */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&h=1080&fit=crop"
          alt="Modern Real Estate Development"
          className="w-full h-full object-cover opacity-25"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/85 via-background/50 to-background/85" />
      </div>

      {/* Animated background particles - teal color */}
      <div className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `radial-gradient(circle at center, hsl(180 80% 60%) 1px, transparent 1px)`,
          backgroundSize: '80px 80px',
        }}
      />

      {/* Floating orbs - teal and amber colors */}
      <div className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-teal-400/20 blur-[100px] animate-pulse" />
      <div className="absolute top-1/3 -right-32 h-80 w-80 rounded-full bg-amber-500/15 blur-[100px] animate-pulse" style={{ animationDelay: "1s" }} />
      <div className="absolute bottom-0 left-1/4 h-64 w-64 rounded-full bg-emerald-500/10 blur-[80px] animate-pulse" style={{ animationDelay: "2s" }} />

      {/* Main Content */}
      <div className="relative z-10 mx-auto max-w-7xl px-6 pt-8 pb-16 lg:px-12 space-y-8">

        {/* Header */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between animate-fade-in">
          <div className="flex items-center gap-4">
            <a
              href="/company-workspace/project-hub"
              className="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-card/60 text-muted-foreground hover:text-foreground hover:bg-muted/40 hover:border-teal-500/30 transition-all duration-300 shadow-sm shrink-0"
              title="Back to Project Hub"
            >
              <ChevronLeft className="h-5 w-5" />
            </a>
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight text-foreground">
                <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">Project Knowledge Base</span>
              </h1>
              <p className="text-muted-foreground text-sm mt-1">
                Centralized repository for project documentation, AI processing, and analytics.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <a
              href="/sample_projects.csv"
              download="sample_projects.csv"
              className="flex items-center gap-2 rounded-xl border border-teal-500/30 bg-teal-500/10 px-4 py-2.5 text-sm font-semibold text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-all duration-300 hover:-translate-y-1"
            >
              <Download className="h-4 w-4" /> Sample CSV
            </a>
            <button
              onClick={() => setShowBulkImportModal(true)}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all duration-300 hover:-translate-y-1"
            >
              <Upload className="h-4 w-4" /> Bulk Import
            </button>
            <button
              onClick={() => { setFormData({}); setAddStep(1); setShowAddModal(true) }}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all duration-300 hover:-translate-y-1"
            >
              <Plus className="h-4 w-4" /> Add Project
            </button>
          </div>
        </div>

        {/* Dynamic Stats Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-6 animate-fade-in" style={{ animationDelay: "0.1s" }}>
          {[
            { label: "Total Projects", value: dynamicStats.total, icon: FolderOpen, color: "teal", statusKey: "" },
            { label: "Ongoing", value: dynamicStats.ongoing, icon: Activity, color: "emerald", statusKey: "ONGOING" },
            { label: "Upcoming", value: dynamicStats.upcoming, icon: Star, color: "amber", statusKey: "UPCOMING" },
            { label: "Past", value: dynamicStats.past, icon: Clock, color: "slate", statusKey: "PAST" },
            { label: "Drafts", value: dynamicStats.draft, icon: FileText, color: "muted", statusKey: "DRAFT" },
            { label: "Archived", value: dynamicStats.archived, icon: Archive, color: "red", statusKey: "ARCHIVED" },
          ].map((stat, i) => {
            const Icon = stat.icon
            const colorMap = {
              teal: "bg-teal-500/10 text-teal-500",
              emerald: "bg-emerald-500/10 text-emerald-500",
              amber: "bg-amber-500/10 text-amber-500",
              slate: "bg-slate-500/10 text-slate-500",
              muted: "bg-muted text-muted-foreground",
              red: "bg-red-500/10 text-red-500",
            }
            const isActive = stat.statusKey === "ARCHIVED" ? showTrash : (statusFilter === stat.statusKey && !showTrash)

            const handleCardClick = () => {
              if (stat.statusKey === "ARCHIVED") {
                setShowTrash(true)
                setStatusFilter("")
              } else {
                setShowTrash(false)
                setStatusFilter(stat.statusKey)
              }
            }

            return (
              <div
                key={stat.label}
                onClick={handleCardClick}
                className={`dashboard-card group relative rounded-2xl border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-premiumDark animate-fade-in overflow-hidden cursor-pointer ${
                  isActive
                    ? "border-teal-500 ring-2 ring-teal-500/40 bg-teal-500/10 shadow-lg scale-[1.02]"
                    : "border-border hover:border-teal-500/40"
                }`}
                style={{ animationDelay: `${0.1 + i * 0.05}s` }}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-bold uppercase tracking-wider ${isActive ? "text-teal-500 font-extrabold" : "text-muted-foreground"}`}>
                      {stat.label}
                    </span>
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

        {/* Search & Filter Bar */}
        <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-4 backdrop-blur-md animate-fade-in" style={{ animationDelay: "0.2s" }}>
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search projects by name, builder, city..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-xl border border-border bg-muted/30 pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all"
              />
            </div>
            <div className="flex items-center gap-3">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="rounded-xl border border-border bg-card text-foreground px-3.5 py-2.5 text-sm font-medium shadow-sm hover:border-teal-500/50 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all cursor-pointer"
              >
                <option value="" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">All Statuses</option>
                <option value="DRAFT" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Draft</option>
                <option value="ONGOING" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Ongoing</option>
                <option value="UPCOMING" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Upcoming</option>
                <option value="PAST" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Past</option>
                <option value="ARCHIVED" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Archived</option>
              </select>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="rounded-xl border border-border bg-card text-foreground px-3.5 py-2.5 text-sm font-medium shadow-sm hover:border-teal-500/50 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all cursor-pointer"
              >
                <option value="" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">All Types</option>
                <option value="APARTMENT" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Apartment</option>
                <option value="VILLA" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Villa</option>
                <option value="PLOT" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Plot</option>
                <option value="COMMERCIAL" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Commercial</option>
                <option value="PENTHOUSE" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Penthouse</option>
                <option value="TOWNHOUSE" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Townhouse</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="rounded-xl border border-border bg-card text-foreground px-3.5 py-2.5 text-sm font-medium shadow-sm hover:border-teal-500/50 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all cursor-pointer"
              >
                <option value="newest" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Newest First</option>
                <option value="oldest" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Oldest First</option>
                <option value="name_asc" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Name A-Z</option>
                <option value="name_desc" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Name Z-A</option>
                <option value="price_asc" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Price: Low to High</option>
                <option value="price_desc" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Price: High to Low</option>
              </select>
              <button
                onClick={() => refetchProjects()}
                className="flex items-center gap-1.5 rounded-xl border border-border bg-muted/20 px-3 py-2.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-all"
                title="Refresh"
              >
                <RefreshCw className="h-3 w-3" /> Refresh
              </button>
              <button
                onClick={() => { setSearchQuery(""); setStatusFilter(""); setTypeFilter(""); setSortBy("newest") }}
                className="flex items-center gap-1.5 rounded-xl border border-border bg-muted/20 px-3 py-2.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-all"
              >
                <RefreshCw className="h-3 w-3" /> Clear
              </button>
            </div>
          </div>
        </div>

        {/* Projects Grid */}
        {projectsLoading ? (
          <div className="flex items-center justify-center py-24">
            <Loader2 className="h-8 w-8 animate-spin text-teal-500" />
          </div>
        ) : sortedProjects.length === 0 ? (
          <div className="dashboard-card group relative rounded-3xl border border-border bg-card/60 p-12 backdrop-blur-md text-center animate-fade-in">
            <div className="relative z-10">
              <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-muted/50 text-muted-foreground mb-4">
                <FolderOpen className="h-8 w-8" />
              </div>
              <h3 className="text-lg font-bold text-foreground">No projects found</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {showTrash ? "No archived projects." : "Add a new project or adjust your filters."}
              </p>
            </div>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 animate-fade-in" style={{ animationDelay: "0.3s" }}>
            {sortedProjects.map((project, i) => {
              const StatusIcon = STATUS_ICONS[project.status] || FileText
              const TypeIcon = PropertyTypeIcon[project.property_type] || Building2
              const borderColor = STATUS_BORDER_COLORS[project.status] || STATUS_BORDER_COLORS.DRAFT
              const dotColor = STATUS_DOT_COLORS[project.status] || STATUS_DOT_COLORS.DRAFT
              return (
                <div
                  key={project.id}
                  className={`dashboard-card group relative rounded-2xl border border-border bg-card/60 overflow-hidden backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in border-l-4 ${borderColor} cursor-pointer`}
                  style={{ animationDelay: `${0.3 + i * 0.06}s` }}
                  onClick={() => handleSelectProject(project)}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                  <div className="relative z-10">
                    {/* Card Header */}
                    <div className="relative h-36 overflow-hidden">
                      <img
                        src={project.image_url || (project.media && project.media.length > 0 ? project.media[0].file : null) || `https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=600&h=300&fit=crop&random=${project.id}`}
                        alt={project.name}
                        className="w-full h-full object-cover opacity-80 group-hover:scale-105 transition-transform duration-500"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=600&h=300&fit=crop";
                        }}
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-card/90 via-card/30 to-transparent" />
                      <div className="absolute top-3 right-3 flex items-center gap-2">
                        <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ${STATUS_COLORS[project.status] || STATUS_COLORS.DRAFT}`}>
                          <span className={`h-2 w-2 rounded-full ${dotColor} shrink-0`} />
                          <StatusIcon className="h-3 w-3" />
                          {project.status === "ONGOING" ? "Ongoing" : project.status === "PAST" ? "Past" : project.status === "UPCOMING" ? "Upcoming" : project.status === "DRAFT" ? "Draft" : project.status === "ARCHIVED" ? "Archived" : project.status}
                        </span>
                      </div>
                      <div className="absolute bottom-3 left-3">
                        <h3 className="text-base font-extrabold text-foreground drop-shadow-lg">{project.name}</h3>
                      </div>
                    </div>

                    {/* Card Body */}
                    <div className="p-4 space-y-3">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <MapPin className="h-3 w-3" />
                        <span>{project.city || "N/A"}</span>
                        {project.builder && (
                          <>
                            <span className="text-border">|</span>
                            <Building2 className="h-3 w-3" />
                            <span>{project.builder}</span>
                          </>
                        )}
                      </div>

                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <TypeIcon className="h-3 w-3" />
                        <span>{project.property_type || "N/A"}</span>
                        {project.starting_price && (
                          <>
                            <span className="text-border">|</span>
                            <DollarSign className="h-3 w-3" />
                            <span>{formatPrice(project.starting_price)}</span>
                          </>
                        )}
                      </div>

                      {/* Tags */}
                      {project.tags && project.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1.5">
                          {project.tags.slice(0, 3).map((tag, idx) => (
                            <span key={idx} className="inline-flex items-center gap-1 rounded-full bg-teal-500/10 px-2 py-0.5 text-[10px] font-bold text-teal-600 dark:text-teal-400">
                              <Tag className="h-2.5 w-2.5" />
                              {typeof tag === "string" ? tag : tag.name}
                            </span>
                          ))}
                          {project.tags.length > 3 && (
                            <span className="text-[10px] text-muted-foreground">+{project.tags.length - 3} more</span>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Card Actions */}
                    <div className="border-t border-border px-4 py-3 flex items-center justify-between">
                      <div className="flex items-center gap-1">
                         <button
                           onClick={(e) => { e.stopPropagation(); handleSelectProject(project) }}
                           className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:text-teal-500 hover:bg-teal-500/10 transition-all"
                           title="View Details"
                         >
                           <Eye className="h-4 w-4" />
                         </button>
                         <button
                           onClick={(e) => { e.stopPropagation(); setEditData({ ...project }); setEditStep(1); setShowEditModal(true) }}
                           className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:text-amber-500 hover:bg-amber-500/10 transition-all"
                           title="Edit Project"
                         >
                           <Edit3 className="h-4 w-4" />
                         </button>
                         <button
                           onClick={(e) => {
                             e.stopPropagation()
                             if (window.confirm(`Are you sure you want to delete/archive "${project.name}"?`)) {
                               deleteProjectMutation.mutate(project.id)
                             }
                           }}
                           className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:text-red-500 hover:bg-red-500/10 transition-all"
                           title="Delete / Archive Project"
                         >
                           <Trash2 className="h-4 w-4" />
                         </button>
                       </div>
                       <div className="flex items-center gap-1">
                         <button
                           onClick={(e) => { e.stopPropagation(); duplicateProjectMutation.mutate(project.id) }}
                           className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:text-emerald-500 hover:bg-emerald-500/10 transition-all"
                           title="Duplicate"
                         >
                           <Copy className="h-4 w-4" />
                         </button>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Trash View */}
        {showTrash && (
          <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md animate-fade-in" style={{ animationDelay: "0.4s" }}>
            <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-extrabold text-foreground flex items-center gap-2">
                  <Archive className="h-4 w-4 text-red-500" />
                  Archived Projects
                </h2>
                <button
                  onClick={() => setShowTrash(false)}
                  className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  Close Trash View
                </button>
              </div>
              {trashProjects.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">No archived projects.</p>
              ) : (
                <div className="space-y-3">
                  {trashProjects.map((project) => (
                    <div key={project.id} className="flex items-center justify-between rounded-xl border border-border bg-muted/20 px-4 py-3 hover:bg-muted/30 transition-all">
                      <div className="flex items-center gap-3">
                        <Archive className="h-5 w-5 text-red-400" />
                        <div>
                          <p className="text-sm font-semibold text-foreground">{project.name}</p>
                          <p className="text-xs text-muted-foreground">{project.city} • {project.property_type} • {getStatusLabel(project.status)} • {formatDate(project.updated_at)}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => restoreProjectMutation.mutate(project.id)}
                          className="flex items-center gap-1.5 rounded-lg bg-teal-500/10 px-3 py-1.5 text-xs font-semibold text-teal-600 hover:bg-teal-500/20 transition-all"
                        >
                          <RotateCcw className="h-3 w-3" /> Restore
                        </button>
                        <button
                          onClick={() => {
                            if (window.confirm(`Permanently delete "${project.name}"?`)) {
                              deleteProjectMutation.mutate(project.id)
                            }
                          }}
                          className="flex items-center gap-1.5 rounded-lg bg-red-500/10 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-500/20 transition-all"
                        >
                          <Trash2 className="h-3 w-3" /> Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Processing Jobs Modal */}
        {showJobsModal && selectedProject && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm" onClick={() => setShowJobsModal(false)}>
            <div className="dashboard-card group relative w-full max-w-2xl rounded-3xl border border-border bg-card/90 backdrop-blur-xl shadow-2xl p-6 mx-4 max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-extrabold text-foreground flex items-center gap-2">
                    <Wrench className="h-5 w-5 text-teal-500" />
                    Processing Jobs — {selectedProject.name}
                  </h2>
                  <button onClick={() => setShowJobsModal(false)} className="rounded-lg p-2 text-muted-foreground hover:text-foreground hover:bg-muted transition-all">
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <JobList projectId={selectedProject.id} />
              </div>
            </div>
          </div>
        )}

        {/* Add Project Modal */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm" onClick={() => setShowAddModal(false)}>
            <div className="dashboard-card group relative w-full max-w-2xl rounded-3xl border border-border bg-card/90 backdrop-blur-xl shadow-2xl p-6 mx-4 max-h-[85vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-extrabold text-foreground flex items-center gap-2">
                    <Plus className="h-5 w-5 text-teal-500" />
                    Add New Project
                  </h2>
                  <button onClick={() => { setShowAddModal(false); setFormData({}); setAddStep(1) }} className="rounded-lg p-2 text-muted-foreground hover:text-foreground hover:bg-muted transition-all">
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <AddProjectForm step={addStep} setStep={setAddStep} formData={formData} setFormData={setFormData} onSubmit={handleAddProject} isPending={createProjectMutation.isPending} />
              </div>
            </div>
          </div>
        )}

        {/* Edit Project Modal */}
        {showEditModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm" onClick={() => setShowEditModal(false)}>
            <div className="dashboard-card group relative w-full max-w-2xl rounded-3xl border border-border bg-card/90 backdrop-blur-xl shadow-2xl p-6 mx-4 max-h-[85vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-extrabold text-foreground flex items-center gap-2">
                    <Edit3 className="h-5 w-5 text-amber-500" />
                    Edit Project
                  </h2>
                  <button onClick={() => { setShowEditModal(false); setEditData({}); setEditStep(1) }} className="rounded-lg p-2 text-muted-foreground hover:text-foreground hover:bg-muted transition-all">
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <EditProjectForm step={editStep} setStep={setEditStep} editData={editData} setEditData={setEditData} onSubmit={handleEditProject} isPending={updateProjectMutation.isPending} />
              </div>
            </div>
          </div>
        )}

        {/* Bulk Import Modal */}
        {showBulkImportModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm" onClick={() => setShowBulkImportModal(false)}>
            <div className="dashboard-card group relative w-full max-w-lg rounded-3xl border border-border bg-card/90 backdrop-blur-xl shadow-2xl p-6 mx-4" onClick={(e) => e.stopPropagation()}>
              <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-extrabold text-foreground flex items-center gap-2">
                    <Upload className="h-5 w-5 text-teal-500" />
                    Bulk Import Projects
                  </h2>
                  <button onClick={() => { setShowBulkImportModal(false); setImportFiles([]); setBulkImportResults(null) }} className="rounded-lg p-2 text-muted-foreground hover:text-foreground hover:bg-muted transition-all">
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between bg-muted/20 p-3 rounded-xl border border-border">
                    <div>
                      <p className="text-xs font-semibold text-foreground">Need a template?</p>
                      <p className="text-[10px] text-muted-foreground">Download sample CSV file with standard fields</p>
                    </div>
                    <a
                      href="/sample_projects.csv"
                      download="sample_projects.csv"
                      className="flex items-center gap-1.5 rounded-lg bg-teal-500/10 px-3 py-1.5 text-xs font-semibold text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-all"
                    >
                      <Download className="h-3.5 w-3.5" /> Sample CSV
                    </a>
                  </div>
                  <div className="border-2 border-dashed border-border rounded-2xl p-8 text-center hover:border-teal-500/50 transition-colors">
                    <Upload className="h-10 w-10 mx-auto text-muted-foreground mb-3" />
                    <p className="text-sm font-semibold text-foreground">Drop files here or click to upload</p>
                    <p className="text-xs text-muted-foreground mt-1">Supports CSV, Excel, JSON formats</p>
                    <input
                      type="file"
                      multiple
                      accept=".csv,.xlsx,.xls,.json"
                      onChange={(e) => setImportFiles(Array.from(e.target.files || []))}
                      className="hidden"
                      id="bulkImportFile"
                    />
                    <label
                      htmlFor="bulkImportFile"
                      className="mt-4 inline-flex cursor-pointer items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all"
                    >
                      <Upload className="h-3 w-3" /> Choose Files
                    </label>
                  </div>
                  {importFiles.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Selected Files</p>
                      {importFiles.map((f, i) => (
                        <div key={i} className="flex items-center gap-2 rounded-lg bg-muted/30 px-3 py-2 text-xs">
                          <File className="h-4 w-4 text-teal-500" />
                          <span className="flex-1 text-foreground font-medium">{f.name}</span>
                          <span className="text-muted-foreground">{(f.size / 1024).toFixed(1)} KB</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {bulkImportResults && (
                    <div className="rounded-xl border border-border bg-muted/20 p-4 space-y-2">
                      <p className="text-xs font-bold text-foreground">Import Results</p>
                      <p className="text-xs text-emerald-500">Imported: {bulkImportResults.imported?.length || 0}</p>
                      {bulkImportResults.errors?.length > 0 && (
                        <p className="text-xs text-red-500">Errors: {bulkImportResults.errors.length}</p>
                      )}
                    </div>
                  )}
                  <button
                    onClick={handleBulkImport}
                    disabled={importFiles.length === 0 || bulkImportMutation.isPending}
                    className="w-full rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all disabled:opacity-50"
                  >
                    {bulkImportMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mx-auto" /> : "Start Import"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Project Detail View */}
        {view === "detail" && selectedProject && (
          <div ref={detailRef} className="animate-fade-in pt-4 scroll-mt-6">
            {/* Detail Header */}
            <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md mb-6 animate-fade-in">
              <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-4">
                  <button
                    onClick={() => { setView("list"); setSelectedProject(null); setDetailTab("overview") }}
                    className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-all"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </button>
                  <div className="flex-1">
                    <h2 className="text-xl font-extrabold text-foreground">{selectedProject.name}</h2>
                    <p className="text-xs text-muted-foreground">{selectedProject.city} • {selectedProject.property_type} • {selectedProject.builder}</p>
                  </div>
                      <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ${STATUS_COLORS[selectedProject.status] || STATUS_COLORS.DRAFT}`}>
                        <span className={`h-2 w-2 rounded-full ${STATUS_DOT_COLORS[selectedProject.status] || STATUS_DOT_COLORS.DRAFT}`} />
                        {getStatusLabel(selectedProject.status)}
                      </span>
                </div>

                {/* Detail Tabs */}
                <div className="flex items-center gap-1 border-b border-border overflow-x-auto">
                  {[
                    { key: "overview", label: "Overview", icon: Info },
                    { key: "media", label: "Media", icon: Image },
                    { key: "documents", label: "Documents", icon: File },
                    { key: "analytics", label: "Analytics", icon: BarChart3 },
                  ].map((tab) => {
                    const Icon = tab.icon
                    return (
                      <button
                        key={tab.key}
                        onClick={() => setDetailTab(tab.key)}
                        className={`flex items-center gap-1.5 rounded-t-xl px-4 py-2.5 text-xs font-semibold transition-all ${
                          detailTab === tab.key
                            ? "bg-teal-500/10 text-teal-600 border-b-2 border-teal-500"
                            : "text-muted-foreground hover:text-foreground border-b-2 border-transparent"
                        }`}
                      >
                        <Icon className="h-3 w-3" />
                        {tab.label}
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Tab Content */}
            <div className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
              {detailTab === "overview" && <OverviewTab project={selectedProject} />}
              {detailTab === "media" && <MediaTab project={selectedProject} />}
              {detailTab === "documents" && <DocumentsTab project={selectedProject} />}
              {detailTab === "analytics" && <AnalyticsTab project={selectedProject} />}
            </div>
          </div>
        )}

        {/* AI Chat Modal */}
        {showChatModal && selectedProject && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm" onClick={() => setShowChatModal(false)}>
            <div className="dashboard-card group relative w-full max-w-2xl rounded-3xl border border-border bg-card/90 backdrop-blur-xl shadow-2xl flex flex-col mx-4" style={{ height: "70vh" }} onClick={(e) => e.stopPropagation()}>
              <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
              <div className="relative z-10 flex flex-col h-full">
                {/* Chat Header */}
                <div className="relative z-10 border-b border-border bg-muted/10 px-6 py-4 flex items-center justify-between shrink-0">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-premium">
                      <Bot className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-extrabold text-foreground">AI Assistant — {selectedProject.name}</h3>
                      <p className="text-[10px] text-muted-foreground">Ask about this project</p>
                    </div>
                  </div>
                  <button onClick={() => setShowChatModal(false)} className="rounded-lg p-2 text-muted-foreground hover:text-foreground hover:bg-muted transition-all">
                    <X className="h-5 w-5" />
                  </button>
                </div>

                {/* Messages */}
                <div className="relative z-10 flex-1 p-6 overflow-y-auto space-y-4 bg-muted/5">
                  {chatMessages.length === 0 && (
                    <div className="flex h-full flex-col items-center justify-center text-center">
                      <div className="relative mb-4">
                        <div className="absolute -inset-4 rounded-full bg-teal-500/20 blur-xl animate-pulse" />
                        <Sparkles className="relative h-10 w-10 text-teal-500 animate-pulse" />
                      </div>
                      <h4 className="text-sm font-extrabold text-foreground">Start the Conversation</h4>
                      <p className="text-xs text-muted-foreground mt-1 max-w-sm">
                        Ask questions about {selectedProject.name} — pricing, features, availability, or anything else.
                      </p>
                    </div>
                  )}
                  {chatMessages.map((msg, i) => {
                    const isAssistant = msg.role === "assistant"
                    return (
                      <div
                        key={i}
                        className={`flex gap-3 max-w-[80%] animate-fade-in ${isAssistant ? "" : "ml-auto flex-row-reverse"}`}
                        style={{ animationDelay: `${i * 0.05}s` }}
                      >
                        <div
                          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-xs font-bold ${
                            isAssistant ? "bg-gradient-to-tr from-teal-500/10 to-amber-500/10 text-teal-500" : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {isAssistant ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                        </div>
                        <div
                          className={`rounded-2xl px-4 py-3 text-xs shadow-premium border backdrop-blur-md ${
                            isAssistant
                              ? "bg-card/80 border-border text-foreground"
                              : "bg-gradient-to-r from-teal-500 to-amber-600 border-teal-500/20 text-white"
                          }`}
                        >
                          <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                        </div>
                      </div>
                    )
                  })}
                  {chatMutation.isPending && (
                    <div className="flex gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500/10 to-amber-500/10 text-teal-500">
                        <Bot className="h-4 w-4" />
                      </div>
                      <div className="rounded-2xl px-4 py-3 text-xs bg-card/80 border border-border text-muted-foreground">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                    </div>
                  )}
                </div>

                {/* Chat Input */}
                <form onSubmit={handleSendChat} className="relative z-10 border-t border-border p-4 bg-card/80 backdrop-blur-md flex gap-3 shrink-0">
                  <input
                    type="text"
                    required
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask about this project..."
                    className="flex-1 rounded-xl border border-border bg-muted/40 px-4 py-2.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all"
                  />
                  <button
                    type="submit"
                    disabled={chatMutation.isPending || !chatInput.trim()}
                    className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 text-white shadow-premium hover:shadow-premiumDark disabled:opacity-50 transition-all shrink-0"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Toast Notification */}
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

/* --- Sub-components --- */

function AddProjectForm({ step, setStep, formData, setFormData, onSubmit, isPending }) {
  const update = (field, value) => setFormData((prev) => ({ ...prev, [field]: value }))

  if (step === 1) {
    return (
      <div className="space-y-4">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Project Name *</label>
          <input type="text" required value={formData.name || ""} onChange={(e) => update("name", e.target.value)} placeholder="Enter project name" className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Description</label>
          <textarea value={formData.description || ""} onChange={(e) => update("description", e.target.value)} placeholder="Project description" rows={3} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all resize-none" />
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Cover Image URL</label>
          <input type="url" value={formData.image_url || ""} onChange={(e) => update("image_url", e.target.value)} placeholder="https://images.unsplash.com/photo-..." className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Status</label>
            <select
              value={formData.status || "DRAFT"}
              onChange={(e) => update("status", e.target.value)}
              className="w-full rounded-xl border border-border bg-card text-foreground px-4 py-2.5 text-sm font-medium shadow-sm hover:border-teal-500/50 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all cursor-pointer"
            >
              <option value="DRAFT" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Draft</option>
              <option value="ONGOING" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Ongoing</option>
              <option value="UPCOMING" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Upcoming</option>
              <option value="PAST" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Past</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Property Type</label>
            <select
              value={formData.property_type || ""}
              onChange={(e) => update("property_type", e.target.value)}
              className="w-full rounded-xl border border-border bg-card text-foreground px-4 py-2.5 text-sm font-medium shadow-sm hover:border-teal-500/50 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all cursor-pointer"
            >
              <option value="" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Select Type</option>
              <option value="APARTMENT" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Apartment</option>
              <option value="VILLA" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Villa</option>
              <option value="PLOT" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Plot</option>
              <option value="COMMERCIAL" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Commercial</option>
              <option value="PENTHOUSE" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Penthouse</option>
              <option value="TOWNHOUSE" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Townhouse</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">City</label>
            <input type="text" value={formData.city || ""} onChange={(e) => update("city", e.target.value)} placeholder="City" className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Builder</label>
            <input type="text" value={formData.builder || ""} onChange={(e) => update("builder", e.target.value)} placeholder="Builder name" className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={onSubmit} disabled={isPending} className="rounded-xl border border-teal-500/30 bg-teal-500/10 px-5 py-2.5 text-sm font-semibold text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-all disabled:opacity-50">
            {isPending ? <Loader2 className="h-4 w-4 animate-spin mx-auto" /> : "Save Project"}
          </button>
          <button type="button" onClick={() => setStep(2)} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all">
            Next Step
          </button>
        </div>
      </div>
    )
  }

  if (step === 2) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Starting Price</label>
            <input type="number" value={formData.starting_price || ""} onChange={(e) => update("starting_price", e.target.value ? Number(e.target.value) : null)} placeholder="0" className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Max Price</label>
            <input type="number" value={formData.max_price || ""} onChange={(e) => update("max_price", e.target.value ? Number(e.target.value) : null)} placeholder="0" className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
          </div>
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">RERA Registration Number</label>
          <input type="text" value={formData.rera_number || ""} onChange={(e) => update("rera_number", e.target.value)} placeholder="e.g. HRERA-GGM-2024-890" className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Short Description</label>
          <textarea value={formData.short_description || ""} onChange={(e) => update("short_description", e.target.value)} placeholder="Short description for listings" rows={2} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all resize-none" />
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">SEO Description</label>
          <textarea value={formData.seo_description || ""} onChange={(e) => update("seo_description", e.target.value)} placeholder="SEO-optimized description" rows={2} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all resize-none" />
        </div>
        <div className="flex justify-between pt-2">
          <button type="button" onClick={() => setStep(1)} className="rounded-xl border border-border bg-muted/20 px-5 py-2.5 text-sm font-semibold text-muted-foreground hover:text-foreground transition-all">
            Back
          </button>
          <button type="button" onClick={onSubmit} disabled={isPending} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all disabled:opacity-50">
            {isPending ? <Loader2 className="h-4 w-4 animate-spin mx-auto" /> : "Create Project"}
          </button>
        </div>
      </div>
    )
  }

  return null
}

function EditProjectForm({ step, setStep, editData, setEditData, onSubmit, isPending }) {
  const update = (field, value) => setEditData((prev) => ({ ...prev, [field]: value }))

  if (step === 1) {
    return (
      <div className="space-y-4">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Project Name *</label>
          <input type="text" required value={editData.name || ""} onChange={(e) => update("name", e.target.value)} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Description</label>
          <textarea value={editData.description || ""} onChange={(e) => update("description", e.target.value)} rows={3} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all resize-none" />
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Cover Image URL</label>
          <input type="url" value={editData.image_url || ""} onChange={(e) => update("image_url", e.target.value)} placeholder="https://images.unsplash.com/photo-..." className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Status</label>
            <select value={editData.status || "DRAFT"} onChange={(e) => update("status", e.target.value)} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all">
              <option value="DRAFT">Draft</option>
              <option value="ONGOING">Ongoing</option>
              <option value="UPCOMING">Upcoming</option>
              <option value="PAST">Past</option>
              <option value="ARCHIVED">Archived</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Property Type</label>
            <select value={editData.property_type || ""} onChange={(e) => update("property_type", e.target.value)} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all">
              <option value="">Select Type</option>
              <option value="APARTMENT">Apartment</option>
              <option value="VILLA">Villa</option>
              <option value="PLOT">Plot</option>
              <option value="COMMERCIAL">Commercial</option>
              <option value="PENTHOUSE">Penthouse</option>
              <option value="TOWNHOUSE">Townhouse</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">City</label>
            <input type="text" value={editData.city || ""} onChange={(e) => update("city", e.target.value)} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Builder</label>
            <input type="text" value={editData.builder || ""} onChange={(e) => update("builder", e.target.value)} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={onSubmit} disabled={isPending} className="rounded-xl border border-teal-500/30 bg-teal-500/10 px-5 py-2.5 text-sm font-semibold text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-all disabled:opacity-50">
            {isPending ? <Loader2 className="h-4 w-4 animate-spin mx-auto" /> : "Save Changes"}
          </button>
          <button type="button" onClick={() => setStep(2)} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all">
            Next Step
          </button>
        </div>
      </div>
    )
  }

  if (step === 2) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Starting Price</label>
            <input type="number" value={editData.starting_price || ""} onChange={(e) => update("starting_price", e.target.value ? Number(e.target.value) : null)} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Max Price</label>
            <input type="number" value={editData.max_price || ""} onChange={(e) => update("max_price", e.target.value ? Number(e.target.value) : null)} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
          </div>
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">RERA Registration Number</label>
          <input type="text" value={editData.rera_number || ""} onChange={(e) => update("rera_number", e.target.value)} placeholder="e.g. HRERA-GGM-2024-890" className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all" />
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Short Description</label>
          <textarea value={editData.short_description || ""} onChange={(e) => update("short_description", e.target.value)} rows={2} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all resize-none" />
        </div>
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1.5">SEO Description</label>
          <textarea value={editData.seo_description || ""} onChange={(e) => update("seo_description", e.target.value)} rows={2} className="w-full rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all resize-none" />
        </div>
        <div className="flex justify-between pt-2">
          <button onClick={() => setStep(1)} className="rounded-xl border border-border bg-muted/20 px-5 py-2.5 text-sm font-semibold text-muted-foreground hover:text-foreground transition-all">
            Back
          </button>
          <button onClick={onSubmit} disabled={isPending} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all disabled:opacity-50">
            {isPending ? <Loader2 className="h-4 w-4 animate-spin mx-auto" /> : "Save Changes"}
          </button>
        </div>
      </div>
    )
  }

  return null
}

function OverviewTab({ project }) {
  return (
    <div className="space-y-6">
      <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
        <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
        <div className="relative z-10">
          <h3 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
            <Info className="h-4 w-4 text-teal-500" /> Project Overview
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Name</p>
                <p className="text-sm font-semibold text-foreground">{project.name}</p>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Description</p>
                <p className="text-sm text-foreground/80">{truncate(project.description, 200) || "No description"}</p>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Short Description</p>
                <p className="text-sm text-foreground/80">{truncate(project.short_description, 150) || "N/A"}</p>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Builder</p>
                <p className="text-sm text-foreground">{project.builder || "N/A"}</p>
              </div>
            </div>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Status</p>
                  <p className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <span className={`h-2.5 w-2.5 rounded-full ${STATUS_DOT_COLORS[project.status] || STATUS_DOT_COLORS.DRAFT}`} />
                    {getStatusLabel(project.status)}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Type</p>
                  <p className="text-sm font-semibold text-foreground">{project.property_type || "N/A"}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">City</p>
                  <p className="text-sm text-foreground">{project.city || "N/A"}</p>
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">RERA Number</p>
                  <p className="text-sm text-foreground">{project.rera_number || "N/A"}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Starting Price</p>
                  <p className="text-sm font-semibold text-foreground">{formatPrice(project.starting_price)}</p>
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Max Price</p>
                  <p className="text-sm font-semibold text-foreground">{formatPrice(project.max_price)}</p>
                </div>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">AI Processed</p>
                <p className="text-sm text-foreground">{project.ai_processed ? "Yes" : "No"}</p>
              </div>
              {project.ai_generated_summary && (
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">AI Summary</p>
                  <p className="text-sm text-foreground/80">{truncate(project.ai_generated_summary, 200)}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* AI Generated Data */}
      {(project.ai_generated_keywords?.length > 0 || project.ai_generated_tags?.length > 0 || project.ai_generated_highlights?.length > 0 || project.ai_generated_investment_points?.length > 0) && (
        <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
          <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
          <div className="relative z-10">
            <h3 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-amber-500" /> AI Generated Data
            </h3>
            {project.ai_generated_keywords?.length > 0 && (
              <div className="mb-3">
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Keywords</p>
                <div className="flex flex-wrap gap-2">
                  {project.ai_generated_keywords.map((kw, i) => (
                    <span key={i} className="rounded-full bg-teal-500/10 px-2.5 py-1 text-[10px] font-bold text-teal-600 dark:text-teal-400">{kw}</span>
                  ))}
                </div>
              </div>
            )}
            {project.ai_generated_tags?.length > 0 && (
              <div className="mb-3">
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Tags</p>
                <div className="flex flex-wrap gap-2">
                  {project.ai_generated_tags.map((tag, i) => (
                    <span key={i} className="rounded-full bg-amber-500/10 px-2.5 py-1 text-[10px] font-bold text-amber-600 dark:text-amber-400">{tag}</span>
                  ))}
                </div>
              </div>
            )}
            {project.ai_generated_highlights?.length > 0 && (
              <div className="mb-3">
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Highlights</p>
                <ul className="space-y-1">
                  {project.ai_generated_highlights.map((h, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-foreground/80">
                      <CheckCircle className="h-3 w-3 text-teal-500 mt-0.5 shrink-0" />
                      {h}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {project.ai_generated_investment_points?.length > 0 && (
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Investment Points</p>
                <ul className="space-y-1">
                  {project.ai_generated_investment_points.map((ip, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-foreground/80">
                      <TrendingUp className="h-3 w-3 text-amber-500 mt-0.5 shrink-0" />
                      {ip}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function MediaTab({ project }) {
  const media = project.media || []
  return (
    <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
      <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      <div className="relative z-10">
        <h3 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
          <Image className="h-4 w-4 text-teal-500" /> Media ({media.length})
        </h3>
        {media.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">No media files uploaded yet.</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {media.map((m, i) => (
              <div key={m.id || i} className="rounded-xl border border-border bg-muted/20 overflow-hidden">
                {m.media_type === "IMAGE" ? (
                  <img src={m.file || ""} alt={m.caption || m.media_type} className="w-full h-32 object-cover" />
                ) : (
                  <div className="h-32 flex items-center justify-center bg-muted/30">
                    <File className="h-8 w-8 text-muted-foreground" />
                  </div>
                )}
                <div className="p-3">
                  <p className="text-xs font-semibold text-foreground">{m.caption || m.media_type}</p>
                  <p className="text-[10px] text-muted-foreground">{m.media_type} • Sort: {m.sort_order}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function DocumentsTab({ project }) {
  const docs = project.documents || []
  return (
    <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
      <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      <div className="relative z-10">
        <h3 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
          <FileText className="h-4 w-4 text-teal-500" /> Documents ({docs.length})
        </h3>
        {docs.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">No documents uploaded yet.</p>
        ) : (
          <div className="space-y-3">
            {docs.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between rounded-xl border border-border bg-muted/20 px-4 py-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <File className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">{doc.name}</p>
                    <p className="text-[10px] text-muted-foreground">{doc.document_type} • v{doc.version} • {(doc.file_size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {doc.processed && (
                    <span className="flex items-center gap-1 text-[10px] text-emerald-500 font-semibold">
                      <CheckCircle className="h-3 w-3" /> Processed
                    </span>
                  )}
                  <button className="rounded-lg p-2 text-muted-foreground hover:text-teal-500 hover:bg-teal-500/10 transition-all">
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function AITab({ project }) {
  const jobs = project.processing_jobs || []
  return (
    <div className="space-y-6">
      <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
        <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-extrabold text-foreground flex items-center gap-2">
              <FlaskConical className="h-4 w-4 text-teal-500" /> AI Processing
            </h3>
            <button
              onClick={() => {
                if (window.confirm(`Trigger AI generation for "${project.name}"?`)) {
                  // This would trigger AI generate - using the Django endpoint
                }
              }}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all"
            >
              <Sparkles className="h-3 w-3" /> Generate AI Content
            </button>
          </div>
          {jobs.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">No AI processing jobs yet.</p>
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => {
                const StatusIcon = JOB_STATUS_ICONS[job.status] || Clock
                return (
                  <div key={job.id} className="flex items-center justify-between rounded-xl border border-border bg-muted/20 px-4 py-3">
                    <div className="flex items-center gap-3">
                      <StatusIcon className={`h-4 w-4 ${JOB_STATUS_COLORS[job.status] || "text-muted-foreground"}`} />
                      <div>
                        <p className="text-sm font-semibold text-foreground">{job.job_type}</p>
                        <p className="text-[10px] text-muted-foreground">{job.status} • {job.progress}%</p>
                      </div>
                    </div>
                    <div className="w-24">
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            job.status === "COMPLETED" ? "bg-emerald-500" :
                            job.status === "FAILED" ? "bg-red-500" :
                            job.status === "PROCESSING" ? "bg-teal-500" : "bg-amber-500"
                          }`}
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* AI Generated Content Summary */}
      {(project.ai_generated_summary || project.ai_generated_keywords?.length > 0 || project.ai_generated_highlights?.length > 0) && (
        <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
          <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
          <div className="relative z-10">
            <h3 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
              <Bot className="h-4 w-4 text-amber-500" /> AI Generated Content
            </h3>
            {project.ai_generated_summary && (
              <div className="mb-4">
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Summary</p>
                <p className="text-sm text-foreground/80 leading-relaxed">{project.ai_generated_summary}</p>
              </div>
            )}
            {project.ai_generated_keywords?.length > 0 && (
              <div className="mb-3">
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Keywords</p>
                <div className="flex flex-wrap gap-2">
                  {project.ai_generated_keywords.map((kw, i) => (
                    <span key={i} className="rounded-full bg-teal-500/10 px-2.5 py-1 text-[10px] font-bold text-teal-600">{kw}</span>
                  ))}
                </div>
              </div>
            )}
            {project.ai_generated_highlights?.length > 0 && (
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Highlights</p>
                <ul className="space-y-1">
                  {project.ai_generated_highlights.map((h, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-foreground/80">
                      <CheckCircle className="h-3 w-3 text-teal-500 mt-0.5 shrink-0" />
                      {h}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function AnalyticsTab({ project }) {
  const analytics = project.analytics
  return (
    <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
      <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      <div className="relative z-10">
        <h3 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-teal-500" /> Analytics
        </h3>
        {!analytics ? (
          <p className="text-sm text-muted-foreground text-center py-8">No analytics data available yet.</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { label: "Interested Customers", value: analytics.interested_customers, icon: Users, color: "teal" },
              { label: "AI Recommendations", value: analytics.ai_recommendations, icon: Sparkles, color: "amber" },
              { label: "Brochure Downloads", value: analytics.brochure_downloads, icon: Download, color: "emerald" },
              { label: "Video Views", value: analytics.video_views, icon: Eye, color: "slate" },
              { label: "Site Visits", value: analytics.site_visits, icon: Home, color: "teal" },
              { label: "Bookings", value: analytics.bookings, icon: CheckCircle, color: "emerald" },
              { label: "Revenue", value: formatPrice(analytics.revenue), icon: DollarSign, color: "amber" },
              { label: "Conversion Rate", value: `${analytics.conversion_rate}%`, icon: TrendingUp, color: "teal" },
            ].map((stat, i) => {
              const Icon = stat.icon
              return (
                <div key={stat.label} className="rounded-xl border border-border bg-muted/20 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className="h-4 w-4 text-teal-500" />
                    <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{stat.label}</span>
                  </div>
                  <p className="text-lg font-extrabold text-foreground">{stat.value}</p>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

function VersionsTab({ project }) {
  const versions = project.versions || []
  return (
    <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
      <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      <div className="relative z-10">
        <h3 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
          <History className="h-4 w-4 text-teal-500" /> Version History ({versions.length})
        </h3>
        {versions.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">No version history available.</p>
        ) : (
          <div className="space-y-3">
            {versions.map((v) => (
              <div key={v.id} className="flex items-start gap-3 rounded-xl border border-border bg-muted/20 px-4 py-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-500/10 text-teal-500 shrink-0">
                  <History className="h-4 w-4" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-foreground">v{v.version_number}</p>
                    <span className="text-[10px] text-muted-foreground">{formatDate(v.created_at)}</span>
                  </div>
                  <p className="text-xs text-foreground/70 mt-1">{v.change_summary}</p>
                  {v.changed_fields?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {v.changed_fields.map((f, i) => (
                        <span key={i} className="rounded-full bg-amber-500/10 px-2 py-0.5 text-[10px] font-bold text-amber-600">{f}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function ChatTab({ project }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [sessions, setSessions] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const chatEndRef = useRef(null)

  useEffect(() => {
    api.get(`/api/knowledge-base/${project.id}/chat-sessions/`).then((res) => {
      setSessions(res.data.results || res.data || [])
    }).catch(() => {})
  }, [project.id])

  useEffect(() => {
    if (activeSession && sessions.length > 0) {
      const session = sessions.find((s) => s.id === activeSession) || sessions[0]
      if (session) {
        setActiveSession(session.id)
        api.get(`/api/knowledge-base/chat-sessions/${session.id}/messages/`).then((res) => {
          setMessages(res.data || [])
        }).catch(() => {})
      }
    }
  }, [activeSession, sessions])

  const sendMessage = () => {
    if (!input.trim() || !activeSession) return
    const userMsg = { role: "user", content: input, created_at: new Date().toISOString() }
    setMessages((prev) => [...prev, userMsg])
    api.post(`/api/knowledge-base/${project.id}/chat/`, { message: input }).then((res) => {
      setMessages((prev) => [...prev, { role: "assistant", content: res.data.response, created_at: new Date().toISOString() }])
      setInput("")
    }).catch(() => {
      setMessages((prev) => [...prev, { role: "assistant", content: "AI service unavailable.", created_at: new Date().toISOString() }])
    })
  }

  return (
    <div className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
      <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      <div className="relative z-10">
        <h3 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-teal-500" /> AI Chat
        </h3>
        {/* Session selector */}
        <div className="flex items-center gap-2 mb-4">
          <select
            value={activeSession || ""}
            onChange={(e) => setActiveSession(Number(e.target.value))}
            className="flex-1 rounded-xl border border-border bg-muted/30 px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500"
          >
            <option value="">Select a session</option>
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>{s.title}</option>
            ))}
          </select>
          <button
            onClick={() => {
              api.post(`/api/knowledge-base/${project.id}/chat-sessions/`, { title: "New Chat" }).then((res) => {
                setSessions((prev) => [...prev, res.data])
                setActiveSession(res.data.id)
              })
            }}
            className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-3 py-2 text-xs font-semibold text-white"
          >
            <Plus className="h-3 w-3" />
          </button>
        </div>

        {/* Messages */}
        <div className="h-64 overflow-y-auto space-y-3 mb-4 bg-muted/5 rounded-xl p-4">
          {messages.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-8">No messages yet. Start a conversation.</p>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`flex gap-2 ${msg.role === "user" ? "justify-end" : ""}`}>
                <div className={`rounded-xl px-3 py-2 text-xs max-w-[80%] ${msg.role === "user" ? "bg-gradient-to-r from-teal-500 to-amber-600 text-white" : "bg-card border border-border text-foreground"}`}>
                  {msg.content}
                </div>
              </div>
            ))
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={(e) => { e.preventDefault(); sendMessage() }} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 rounded-xl border border-border bg-muted/30 px-4 py-2.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500"
          />
          <button type="submit" disabled={!input.trim() || !activeSession} className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-4 py-2.5 text-xs font-semibold text-white shadow-lg disabled:opacity-50">
            <Send className="h-3 w-3" />
          </button>
        </form>
      </div>
    </div>
  )
}

function JobList({ projectId }) {
  const { data: jobs = [] } = useQuery({
    queryKey: ["projectJobs", projectId],
    queryFn: () => api.get(`/api/knowledge-base/jobs/?project_id=${projectId}`).then((res) => res.data.results || res.data),
  })

  if (jobs.length === 0) {
    return <p className="text-sm text-muted-foreground text-center py-8">No processing jobs found.</p>
  }

  return (
    <div className="space-y-3">
      {jobs.map((job) => {
        const StatusIcon = JOB_STATUS_ICONS[job.status] || Clock
        return (
          <div key={job.id} className="flex items-center justify-between rounded-xl border border-border bg-muted/20 px-4 py-3">
            <div className="flex items-center gap-3">
              <StatusIcon className={`h-4 w-4 ${JOB_STATUS_COLORS[job.status] || "text-muted-foreground"}`} />
              <div>
                <p className="text-sm font-semibold text-foreground">{job.job_type}</p>
                <p className="text-[10px] text-muted-foreground">{job.status} • {job.progress}% • {formatDate(job.created_at)}</p>
              </div>
            </div>
            <div className="w-24">
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    job.status === "COMPLETED" ? "bg-emerald-500" :
                    job.status === "FAILED" ? "bg-red-500" :
                    job.status === "PROCESSING" ? "bg-teal-500" : "bg-amber-500"
                  }`}
                  style={{ width: `${job.progress}%` }}
                />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}