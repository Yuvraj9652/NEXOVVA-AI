import React, { useState, useEffect, useRef } from "react"
import {
  UserCheck,
  Star,
  Target,
  ArrowRight,
  ChevronLeft,
  Search,
  Plus,
  Upload,
  Download,
  Filter,
  Edit3,
  Trash2,
  Eye,
  Phone,
  Mail,
  Building2,
  MapPin,
  DollarSign,
  Briefcase,
  X,
  Loader2,
  Sparkles,
  CheckCircle,
  FileText,
  User,
} from "lucide-react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "../api/client"

export default function AICustomerMatching() {
  const queryClient = useQueryClient()
  const pageRef = useRef(null)
  const detailRef = useRef(null)

  // State filters & tabs
  const [activeTab, setActiveTab] = useState("ALL") // "ALL", "NEW", "PAST"
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [typeFilter, setTypeFilter] = useState("")
  const [priorityFilter, setPriorityFilter] = useState("")
  const [sortBy, setSortBy] = useState("newest")

  // Selected customer for details view
  const [selectedCustomer, setSelectedCustomer] = useState(null)

  // Modals state
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const [csvFile, setCsvFile] = useState(null)
  const [importStatus, setImportStatus] = useState(null)

  // Customer Form Data
  const defaultForm = {
    first_name: "",
    last_name: "",
    phone: "",
    email: "",
    lead_status: "NEW",
    priority: "MEDIUM",
    company: "",
    occupation: "",
    city: "",
    property_type: "APARTMENT",
    budget_min: "",
    budget_max: "",
    purpose: "SELF_USE",
  }
  const [formData, setFormData] = useState(defaultForm)
  const [editData, setEditData] = useState(null)

  // Mouse tracking for cards glass gradient
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
  }, [])

  // Fetch Customers from DB
  const { data: customers = [], isLoading: isLoadingCustomers } = useQuery({
    queryKey: ["customersList"],
    queryFn: () => api.get("/api/customers/").then((res) => res.data.results || res.data),
  })

  // Fetch Projects from DB for AI Matching
  const { data: projects = [] } = useQuery({
    queryKey: ["allProjectsMatching"],
    queryFn: () => api.get("/api/knowledge-base/projects/").then((res) => res.data.results || res.data),
  })

  // Helper to invalidate queries
  const invalidateQueries = () => {
    queryClient.invalidateQueries(["customersList"])
  }

  const [formError, setFormError] = useState(null)

  // Create Customer Mutation
  const createCustomerMutation = useMutation({
    mutationFn: (data) => api.post("/api/customers/", data),
    onSuccess: () => {
      invalidateQueries()
      setShowAddModal(false)
      setFormData(defaultForm)
      setFormError(null)
    },
    onError: (err) => {
      const data = err?.response?.data
      let msg = "Failed to add customer. Please check fields."
      if (data && typeof data === "object") {
        msg = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`).join(" | ")
      }
      setFormError(msg)
    }
  })

  // Update Customer Mutation
  const updateCustomerMutation = useMutation({
    mutationFn: ({ id, data }) => api.patch(`/api/customers/${id}/`, data),
    onSuccess: () => {
      invalidateQueries()
      setShowEditModal(false)
      setEditData(null)
    },
  })

  // Delete Customer Mutation
  const deleteCustomerMutation = useMutation({
    mutationFn: (id) => api.delete(`/api/customers/${id}/`),
    onSuccess: () => {
      invalidateQueries()
      if (selectedCustomer) setSelectedCustomer(null)
    },
  })

  // Bulk Import Mutation
  const bulkImportMutation = useMutation({
    mutationFn: (formData) => api.post("/api/customers/bulk_import/", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    }),
    onSuccess: (res) => {
      setImportStatus(res.data)
      invalidateQueries()
    },
    onError: (err) => {
      setImportStatus({ error: err?.response?.data?.detail || "Import failed. Please check CSV format." })
    }
  })

  // Handle Create Customer Submit
  const handleCreateSubmit = (e) => {
    e.preventDefault()
    setFormError(null)
    const payload = {
      ...formData,
      first_name: formData.first_name.trim(),
      last_name: formData.last_name ? formData.last_name.trim() : "",
      phone: formData.phone.trim(),
      email: formData.email ? formData.email.trim() : "",
      budget_min: formData.budget_min ? Number(formData.budget_min) : null,
      budget_max: formData.budget_max ? Number(formData.budget_max) : null,
    }
    createCustomerMutation.mutate(payload)
  }

  // Handle Edit Customer Submit
  const handleEditSubmit = (e) => {
    e.preventDefault()
    if (!editData) return
    const payload = { ...editData }
    delete payload.customer_code
    delete payload.created_at
    delete payload.updated_at
    delete payload.created_by
    delete payload.address
    delete payload.requirements
    delete payload.source_detail
    updateCustomerMutation.mutate({ id: editData.id, data: payload })
  }

  // Handle CSV Import
  const handleImportSubmit = (e) => {
    e.preventDefault()
    if (!csvFile) return
    const fd = new FormData()
    fd.append("file", csvFile)
    bulkImportMutation.mutate(fd)
  }

  // AI Matching algorithm: calculates match score between customer and project
  const calculateAIMatches = (customer) => {
    if (!projects || projects.length === 0) return []

    const req = customer.requirements?.[0] || customer.requirement || {}
    const prefType = (req.property_type || customer.property_type || "").toUpperCase()
    const prefCity = (req.preferred_city || customer.address?.city || customer.city || "").toLowerCase()
    const bMin = Number(req.budget_min || customer.budget_min || 0)
    const bMax = Number(req.budget_max || customer.budget_max || 999999999)

    return projects.map((proj) => {
      let score = 50 // Base score
      const matchReasons = []

      // Property type match (+25%)
      if (prefType && proj.property_type && proj.property_type.toUpperCase() === prefType) {
        score += 25
        matchReasons.push(`Property Type (${proj.property_type}) matches customer preference`)
      }

      // City match (+15%)
      if (prefCity && proj.city && proj.city.toLowerCase().includes(prefCity)) {
        score += 15
        matchReasons.push(`Located in preferred city (${proj.city})`)
      }

      // Budget fit (+10%)
      const pPrice = Number(proj.starting_price || 0)
      if (pPrice > 0 && bMin > 0 && bMax > 0) {
        if (pPrice >= bMin * 0.8 && pPrice <= bMax * 1.2) {
          score += 10
          matchReasons.push(`Pricing fits customer budget range`)
        }
      }

      // RERA / Verified (+5%)
      if (proj.rera_number) {
        score += 5
        matchReasons.push(`RERA Verified Project`)
      }

      return {
        project: proj,
        score: Math.min(score, 99),
        reasons: matchReasons.length > 0 ? matchReasons : ["General AI Recommendation"],
      }
    }).sort((a, b) => b.score - a.score)
  }

  // Filter Customers
  const filteredCustomers = customers.filter((c) => {
    const fullName = `${c.first_name || ""} ${c.last_name || ""}`.toLowerCase()
    const phone = (c.phone || "").toLowerCase()
    const email = (c.email || "").toLowerCase()
    const company = (c.company || "").toLowerCase()
    const city = (c.address?.city || c.city || "").toLowerCase()

    // Tab Filter
    if (activeTab === "NEW" && !["NEW", "HOT", "WARM", "COLD"].includes(c.lead_status)) {
      return false
    }
    if (activeTab === "PAST" && ["NEW", "HOT", "WARM", "COLD"].includes(c.lead_status)) {
      return false
    }

    // Search Query
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      const match = fullName.includes(q) || phone.includes(q) || email.includes(q) || company.includes(q) || city.includes(q)
      if (!match) return false
    }

    // Dropdown Status Filter
    if (statusFilter && c.lead_status !== statusFilter) return false

    // Priority Filter
    if (priorityFilter && c.priority !== priorityFilter) return false

    return true
  })

  // Sort Customers
  const sortedCustomers = [...filteredCustomers].sort((a, b) => {
    if (sortBy === "newest") return new Date(b.created_at || 0) - new Date(a.created_at || 0)
    if (sortBy === "oldest") return new Date(a.created_at || 0) - new Date(b.created_at || 0)
    if (sortBy === "name_asc") return `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`)
    if (sortBy === "name_desc") return `${b.first_name} ${b.last_name}`.localeCompare(`${a.first_name} ${a.last_name}`)
    return 0
  })

  // Tab counts
  const newCount = customers.filter(c => ["NEW", "HOT", "WARM", "COLD"].includes(c.lead_status)).length
  const pastCount = customers.filter(c => !["NEW", "HOT", "WARM", "COLD"].includes(c.lead_status)).length

  // Scroll to customer details
  const handleSelectCustomer = (customer) => {
    setSelectedCustomer(customer)
    setTimeout(() => {
      detailRef.current?.scrollIntoView({ behavior: "smooth" })
    }, 100)
  }

  // Format currency
  const formatINR = (val) => {
    if (!val) return "N/A"
    const num = Number(val)
    if (num >= 10000000) return `₹${(num / 10000000).toFixed(2)} Cr`
    if (num >= 100000) return `₹${(num / 100000).toFixed(2)} Lakh`
    return `₹${num.toLocaleString("en-IN")}`
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={pageRef}>
      {/* Background Image & Effects */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1920&h=1080&fit=crop"
          alt="Modern Real Estate Building"
          className="w-full h-full object-cover opacity-30"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/60 to-background/80" />
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

      {/* Main Content */}
      <div className="relative z-10 mx-auto max-w-7xl px-6 pt-8 pb-16 lg:px-12 space-y-8">
        
        {/* Header Section */}
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
                <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">AI Customer Matching</span>
              </h1>
              <p className="text-muted-foreground text-sm mt-1">
                Intelligent lead-to-project matching engine powered by behavioral requirements & AI score matching.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowImportModal(true)}
              className="flex items-center gap-2 rounded-xl border border-teal-500/30 bg-teal-500/10 px-4 py-2.5 text-sm font-semibold text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-all shadow-sm"
            >
              <Upload className="h-4 w-4" /> Import CSV
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 hover:shadow-premiumDark transition-all duration-300 hover:-translate-y-0.5"
            >
              <Plus className="h-4 w-4" /> Add Customer
            </button>
          </div>
        </div>

        {/* Tabs Bar */}
        <div className="flex items-center gap-3 border-b border-border/80 pb-3 animate-fade-in overflow-x-auto">
          <button
            onClick={() => setActiveTab("ALL")}
            className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-all ${
              activeTab === "ALL"
                ? "bg-teal-500/10 text-teal-500 border border-teal-500/30 shadow-sm"
                : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
            }`}
          >
            <User className="h-4 w-4" /> All Customers
            <span className="rounded-full bg-teal-500/20 text-teal-500 text-xs px-2 py-0.5">{customers.length}</span>
          </button>
          <button
            onClick={() => setActiveTab("NEW")}
            className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-all ${
              activeTab === "NEW"
                ? "bg-teal-500/10 text-teal-500 border border-teal-500/30 shadow-sm"
                : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
            }`}
          >
            <Sparkles className="h-4 w-4" /> New Customers
            <span className="rounded-full bg-teal-500/20 text-teal-500 text-xs px-2 py-0.5">{newCount}</span>
          </button>
          <button
            onClick={() => setActiveTab("PAST")}
            className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition-all ${
              activeTab === "PAST"
                ? "bg-teal-500/10 text-teal-500 border border-teal-500/30 shadow-sm"
                : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
            }`}
          >
            <CheckCircle className="h-4 w-4" /> Past / Matched
            <span className="rounded-full bg-amber-500/20 text-amber-500 text-xs px-2 py-0.5">{pastCount}</span>
          </button>
        </div>

        {/* Search, Filter & Sort Bar */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between animate-fade-in">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name, phone (e.g. 8980133121), email, or city..."
              className="w-full rounded-xl border border-border bg-card/60 pl-10 pr-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all placeholder:text-muted-foreground"
            />
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-xl border border-border bg-card text-foreground px-3.5 py-2.5 text-sm font-medium shadow-sm hover:border-teal-500/50 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all cursor-pointer"
            >
              <option value="" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">All Lead Statuses</option>
              <option value="NEW" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">New</option>
              <option value="HOT" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Hot Lead</option>
              <option value="WARM" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Warm Lead</option>
              <option value="CONTACTED" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Contacted</option>
              <option value="VISITED" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Visited</option>
              <option value="BOOKED" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Booked</option>
              <option value="CLOSED" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Closed</option>
            </select>

            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="rounded-xl border border-border bg-card text-foreground px-3.5 py-2.5 text-sm font-medium shadow-sm hover:border-teal-500/50 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all cursor-pointer"
            >
              <option value="" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">All Priorities</option>
              <option value="HIGH" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">High Priority</option>
              <option value="MEDIUM" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Medium Priority</option>
              <option value="LOW" className="bg-background text-foreground dark:bg-slate-900 dark:text-slate-100">Low Priority</option>
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
            </select>
          </div>
        </div>

        {/* Customer Cards List */}
        {isLoadingCustomers ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-teal-500" />
          </div>
        ) : sortedCustomers.length === 0 ? (
          <div className="rounded-2xl border border-border bg-card/60 p-12 text-center backdrop-blur-md">
            <User className="h-12 w-12 text-muted-foreground mx-auto mb-3 opacity-50" />
            <h3 className="text-lg font-bold">No customers found</h3>
            <p className="text-sm text-muted-foreground mt-1">Try adjusting your filters or import a customer CSV file.</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="mt-4 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-4 py-2 text-sm font-semibold text-white shadow-md"
            >
              <Plus className="h-4 w-4" /> Add First Customer
            </button>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {sortedCustomers.map((customer) => {
              const aiMatches = calculateAIMatches(customer)
              const topMatch = aiMatches[0]
              const req = customer.requirements?.[0] || customer.requirement || {}

              return (
                <div
                  key={customer.id}
                  className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-premiumDark overflow-hidden flex flex-col justify-between"
                >
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

                  <div className="relative z-10 space-y-4">
                    {/* Customer Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500/20 to-amber-500/20 text-teal-400 font-bold text-base shadow-sm">
                          {customer.first_name?.[0]}{customer.last_name?.[0]}
                        </div>
                        <div>
                          <h3 className="text-base font-bold text-foreground group-hover:text-teal-400 transition-colors">
                            {customer.first_name} {customer.last_name}
                          </h3>
                          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                            <Phone className="h-3 w-3 text-teal-500" /> {customer.phone}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-1">
                        <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                          customer.priority === "HIGH" ? "bg-rose-500/10 text-rose-500 border border-rose-500/20" :
                          customer.priority === "MEDIUM" ? "bg-amber-500/10 text-amber-500 border border-amber-500/20" :
                          "bg-blue-500/10 text-blue-500 border border-blue-500/20"
                        }`}>
                          {customer.priority || "MEDIUM"}
                        </span>
                      </div>
                    </div>

                    {/* Contact & Preference Snippets */}
                    <div className="grid grid-cols-2 gap-2 rounded-xl bg-muted/20 p-3 text-xs">
                      <div>
                        <span className="text-muted-foreground block text-[10px] uppercase tracking-wider">City</span>
                        <span className="font-semibold">{customer.address?.city || customer.city || "Not Specified"}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground block text-[10px] uppercase tracking-wider">Preferred Type</span>
                        <span className="font-semibold">{req.property_type || customer.property_type || "Any"}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground block text-[10px] uppercase tracking-wider">Budget Range</span>
                        <span className="font-semibold text-emerald-500 dark:text-emerald-400">
                          {req.budget_min ? formatINR(req.budget_min) : "N/A"} - {req.budget_max ? formatINR(req.budget_max) : "N/A"}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground block text-[10px] uppercase tracking-wider">Company</span>
                        <span className="font-semibold truncate block">{customer.company || customer.occupation || "N/A"}</span>
                      </div>
                    </div>

                    {/* Top AI Match Badge */}
                    {topMatch ? (
                      <div className="rounded-xl border border-teal-500/20 bg-teal-500/5 p-3 text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="flex items-center gap-1 font-bold text-teal-400">
                            <Sparkles className="h-3.5 w-3.5 text-teal-400 animate-pulse" /> AI Match: {topMatch.project.name}
                          </span>
                          <span className="rounded-full bg-emerald-500/20 text-emerald-400 font-extrabold px-2 py-0.5 text-[11px]">
                            {topMatch.score}%
                          </span>
                        </div>
                        <p className="text-[11px] text-muted-foreground line-clamp-1">{topMatch.reasons[0]}</p>
                      </div>
                    ) : null}
                  </div>

                  {/* Actions Footer */}
                  <div className="relative z-10 flex items-center justify-between pt-4 mt-4 border-t border-border/60">
                    <button
                      onClick={() => handleSelectCustomer(customer)}
                      className="flex items-center gap-1.5 rounded-lg border border-border bg-card/60 px-3 py-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-all"
                    >
                      <Eye className="h-3.5 w-3.5 text-teal-500" /> View Details
                    </button>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => {
                          setEditData({
                            ...customer,
                            city: customer.address?.city || customer.city || "",
                            property_type: req.property_type || customer.property_type || "APARTMENT",
                            budget_min: req.budget_min || customer.budget_min || "",
                            budget_max: req.budget_max || customer.budget_max || "",
                            purpose: req.purpose || customer.purpose || "SELF_USE",
                          })
                          setShowEditModal(true)
                        }}
                        className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:text-teal-500 hover:bg-teal-500/10 transition-all"
                        title="Edit Customer"
                      >
                        <Edit3 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          if (window.confirm(`Are you sure you want to delete ${customer.first_name} ${customer.last_name}?`)) {
                            deleteCustomerMutation.mutate(customer.id)
                          }
                        }}
                        className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:text-rose-500 hover:bg-rose-500/10 transition-all"
                        title="Delete Customer"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Customer Details Drawer / Bottom View */}
        {selectedCustomer && (
          <div ref={detailRef} className="rounded-2xl border border-teal-500/30 bg-card/90 p-6 md:p-8 backdrop-blur-md shadow-2xl space-y-6 animate-fade-in">
            <div className="flex items-start justify-between border-b border-border/80 pb-4">
              <div className="flex items-center gap-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-teal-500/30 to-amber-500/30 text-teal-300 font-extrabold text-xl shadow-md">
                  {selectedCustomer.first_name?.[0]}{selectedCustomer.last_name?.[0]}
                </div>
                <div>
                  <h2 className="text-2xl font-extrabold text-foreground">
                    {selectedCustomer.first_name} {selectedCustomer.last_name}
                  </h2>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                    <span className="flex items-center gap-1 text-teal-400 font-semibold">
                      <Phone className="h-3.5 w-3.5" /> {selectedCustomer.phone}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Mail className="h-3.5 w-3.5" /> {selectedCustomer.email || "No Email"}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setSelectedCustomer(null)}
                className="rounded-xl border border-border p-2 text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-all"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Grid Information */}
            <div className="grid gap-6 md:grid-cols-3">
              {/* Personal & Profile Info */}
              <div className="rounded-xl bg-muted/30 p-4 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-teal-400 flex items-center gap-1.5">
                  <User className="h-4 w-4" /> Personal Profile
                </h4>
                <div className="text-xs space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Occupation:</span>
                    <span className="font-semibold">{selectedCustomer.occupation || "N/A"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Company:</span>
                    <span className="font-semibold">{selectedCustomer.company || "N/A"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">City:</span>
                    <span className="font-semibold">{selectedCustomer.address?.city || selectedCustomer.city || "N/A"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Lead Status:</span>
                    <span className="font-semibold text-teal-400">{selectedCustomer.lead_status}</span>
                  </div>
                </div>
              </div>

              {/* Property Requirements */}
              <div className="rounded-xl bg-muted/30 p-4 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                  <Building2 className="h-4 w-4" /> Requirements
                </h4>
                <div className="text-xs space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Preferred Type:</span>
                    <span className="font-semibold">{selectedCustomer.requirements?.[0]?.property_type || selectedCustomer.property_type || "Any"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Purpose:</span>
                    <span className="font-semibold">{selectedCustomer.requirements?.[0]?.purpose || selectedCustomer.purpose || "SELF_USE"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Budget Min:</span>
                    <span className="font-semibold text-emerald-400">{formatINR(selectedCustomer.requirements?.[0]?.budget_min || selectedCustomer.budget_min)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Budget Max:</span>
                    <span className="font-semibold text-emerald-400">{formatINR(selectedCustomer.requirements?.[0]?.budget_max || selectedCustomer.budget_max)}</span>
                  </div>
                </div>
              </div>

              {/* AI Matching Overview */}
              <div className="rounded-xl border border-teal-500/30 bg-teal-500/10 p-4 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-teal-400 flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4" /> Top AI Project Match
                </h4>
                {calculateAIMatches(selectedCustomer)[0] ? (
                  <div className="text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-extrabold text-foreground text-sm">{calculateAIMatches(selectedCustomer)[0].project.name}</span>
                      <span className="rounded-full bg-emerald-500/20 text-emerald-400 font-extrabold px-2.5 py-1 text-xs">
                        {calculateAIMatches(selectedCustomer)[0].score}% Score
                      </span>
                    </div>
                    <p className="text-muted-foreground text-[11px]">
                      {calculateAIMatches(selectedCustomer)[0].reasons.join(" • ")}
                    </p>
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">No projects available for matching.</p>
                )}
              </div>
            </div>

            {/* AI Project Recommendations Table */}
            <div className="space-y-3 pt-2">
              <h3 className="text-base font-bold flex items-center gap-2">
                <Target className="h-5 w-5 text-teal-400" /> AI Recommended Projects for {selectedCustomer.first_name}
              </h3>
              <div className="grid gap-3 md:grid-cols-2">
                {calculateAIMatches(selectedCustomer).map((m, idx) => (
                  <div key={idx} className="rounded-xl border border-border/80 bg-card/80 p-4 flex items-center justify-between gap-4">
                    <div>
                      <h4 className="font-bold text-sm text-foreground">{m.project.name}</h4>
                      <p className="text-xs text-muted-foreground">{m.project.city} • {m.project.property_type} • Starting {formatINR(m.project.starting_price)}</p>
                      <div className="flex items-center gap-1 mt-1.5 flex-wrap">
                        {m.reasons.map((r, ri) => (
                          <span key={ri} className="rounded-md bg-teal-500/10 text-teal-400 px-2 py-0.5 text-[10px] font-medium">
                            {r}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="rounded-full bg-emerald-500/20 text-emerald-400 font-extrabold px-3 py-1 text-xs">
                        {m.score}% Match
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>

      {/* Add Customer Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-xl rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <Plus className="h-5 w-5 text-teal-500" /> Add New Customer
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            {formError && (
              <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-500 font-semibold">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">First Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    placeholder="e.g. Sarinah"
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground focus:ring-1 focus:ring-teal-500"
                  />
                </div>
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Last Name</label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    placeholder="e.g. Shah"
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground focus:ring-1 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Phone Number *</label>
                  <input
                    type="text"
                    required
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="e.g. 8980133121"
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground focus:ring-1 focus:ring-teal-500"
                  />
                </div>
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="e.g. sarinah@example.com"
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground focus:ring-1 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">City</label>
                  <input
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    placeholder="e.g. Gurugram"
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground focus:ring-1 focus:ring-teal-500"
                  />
                </div>
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Company / Occupation</label>
                  <input
                    type="text"
                    value={formData.company}
                    onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                    placeholder="e.g. Tech Corp"
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground focus:ring-1 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Lead Status</label>
                  <select
                    value={formData.lead_status}
                    onChange={(e) => setFormData({ ...formData, lead_status: e.target.value })}
                    className="w-full rounded-xl border border-border bg-card text-foreground px-3 py-2 cursor-pointer"
                  >
                    <option value="NEW" className="bg-slate-900 text-slate-100">New</option>
                    <option value="HOT" className="bg-slate-900 text-slate-100">Hot Lead</option>
                    <option value="WARM" className="bg-slate-900 text-slate-100">Warm Lead</option>
                    <option value="CONTACTED" className="bg-slate-900 text-slate-100">Contacted</option>
                    <option value="BOOKED" className="bg-slate-900 text-slate-100">Booked</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Priority</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    className="w-full rounded-xl border border-border bg-card text-foreground px-3 py-2 cursor-pointer"
                  >
                    <option value="HIGH" className="bg-slate-900 text-slate-100">High</option>
                    <option value="MEDIUM" className="bg-slate-900 text-slate-100">Medium</option>
                    <option value="LOW" className="bg-slate-900 text-slate-100">Low</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Property Type</label>
                  <select
                    value={formData.property_type}
                    onChange={(e) => setFormData({ ...formData, property_type: e.target.value })}
                    className="w-full rounded-xl border border-border bg-card text-foreground px-3 py-2 cursor-pointer"
                  >
                    <option value="APARTMENT" className="bg-slate-900 text-slate-100">Apartment</option>
                    <option value="VILLA" className="bg-slate-900 text-slate-100">Villa</option>
                    <option value="PLOT" className="bg-slate-900 text-slate-100">Plot</option>
                    <option value="COMMERCIAL" className="bg-slate-900 text-slate-100">Commercial</option>
                    <option value="PENTHOUSE" className="bg-slate-900 text-slate-100">Penthouse</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Budget Min (₹)</label>
                  <input
                    type="number"
                    value={formData.budget_min}
                    onChange={(e) => setFormData({ ...formData, budget_min: e.target.value })}
                    placeholder="15000000"
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground"
                  />
                </div>
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Budget Max (₹)</label>
                  <input
                    type="number"
                    value={formData.budget_max}
                    onChange={(e) => setFormData({ ...formData, budget_max: e.target.value })}
                    placeholder="35000000"
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-border/80">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="rounded-xl border border-border px-4 py-2 text-muted-foreground hover:text-foreground"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createCustomerMutation.isPending}
                  className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2 font-semibold text-white shadow-md disabled:opacity-50"
                >
                  {createCustomerMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save Customer"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Customer Modal */}
      {showEditModal && editData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-xl rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <Edit3 className="h-5 w-5 text-teal-500" /> Edit Customer
              </h3>
              <button onClick={() => setShowEditModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">First Name *</label>
                  <input
                    type="text"
                    required
                    value={editData.first_name || ""}
                    onChange={(e) => setEditData({ ...editData, first_name: e.target.value })}
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground"
                  />
                </div>
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Last Name</label>
                  <input
                    type="text"
                    value={editData.last_name || ""}
                    onChange={(e) => setEditData({ ...editData, last_name: e.target.value })}
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Phone Number *</label>
                  <input
                    type="text"
                    required
                    value={editData.phone || ""}
                    onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground"
                  />
                </div>
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Email</label>
                  <input
                    type="email"
                    value={editData.email || ""}
                    onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                    className="w-full rounded-xl border border-border bg-muted/30 px-3 py-2 text-foreground"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Lead Status</label>
                  <select
                    value={editData.lead_status || "NEW"}
                    onChange={(e) => setEditData({ ...editData, lead_status: e.target.value })}
                    className="w-full rounded-xl border border-border bg-card text-foreground px-3 py-2 cursor-pointer"
                  >
                    <option value="NEW" className="bg-slate-900 text-slate-100">New</option>
                    <option value="HOT" className="bg-slate-900 text-slate-100">Hot Lead</option>
                    <option value="WARM" className="bg-slate-900 text-slate-100">Warm Lead</option>
                    <option value="CONTACTED" className="bg-slate-900 text-slate-100">Contacted</option>
                    <option value="BOOKED" className="bg-slate-900 text-slate-100">Booked</option>
                    <option value="CLOSED" className="bg-slate-900 text-slate-100">Closed</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1">Priority</label>
                  <select
                    value={editData.priority || "MEDIUM"}
                    onChange={(e) => setEditData({ ...editData, priority: e.target.value })}
                    className="w-full rounded-xl border border-border bg-card text-foreground px-3 py-2 cursor-pointer"
                  >
                    <option value="HIGH" className="bg-slate-900 text-slate-100">High</option>
                    <option value="MEDIUM" className="bg-slate-900 text-slate-100">Medium</option>
                    <option value="LOW" className="bg-slate-900 text-slate-100">Low</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-border/80">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="rounded-xl border border-border px-4 py-2 text-muted-foreground hover:text-foreground"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateCustomerMutation.isPending}
                  className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2 font-semibold text-white shadow-md disabled:opacity-50"
                >
                  {updateCustomerMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Import CSV Modal */}
      {showImportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border/80 pb-3">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <Upload className="h-5 w-5 text-teal-500" /> Import Customers CSV
              </h3>
              <button onClick={() => setShowImportModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="rounded-xl bg-teal-500/10 border border-teal-500/20 p-3.5 text-xs text-teal-400 space-y-2">
              <p className="font-semibold">Sample CSV Available for Testing:</p>
              <a
                href="/sample_customers.csv"
                download="sample_customers.csv"
                className="inline-flex items-center gap-1.5 font-bold text-amber-400 underline hover:text-amber-300 transition-all"
              >
                <Download className="h-3.5 w-3.5" /> Download Sample CSV (sample_customers.csv)
              </a>
            </div>

            <form onSubmit={handleImportSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold uppercase tracking-wider text-muted-foreground mb-1.5">Select CSV File</label>
                <input
                  type="file"
                  accept=".csv"
                  required
                  onChange={(e) => setCsvFile(e.target.files[0])}
                  className="w-full rounded-xl border border-border bg-muted/30 p-2 text-foreground cursor-pointer"
                />
              </div>

              {importStatus && (
                <div className={`rounded-xl p-3 text-xs ${importStatus.error ? "bg-rose-500/10 text-rose-500" : "bg-emerald-500/10 text-emerald-400"}`}>
                  {importStatus.error ? importStatus.error : `Success! Imported ${importStatus.created} customers (${importStatus.duplicates} duplicates skipped).`}
                </div>
              )}

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowImportModal(false)}
                  className="rounded-xl border border-border px-4 py-2 text-muted-foreground hover:text-foreground"
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={bulkImportMutation.isPending}
                  className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-5 py-2 font-semibold text-white shadow-md disabled:opacity-50"
                >
                  {bulkImportMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Upload & Import"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  )
}
