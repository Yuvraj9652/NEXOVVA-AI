import React, { useEffect, useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useQuery } from "@tanstack/react-query"
import {
  Phone,
  MessageSquare,
  Calendar,
  Building2,
  Sparkles,
  ArrowRight,
  Users,
  TrendingUp,
  Zap,
  Clock,
  Send,
  Bot,
  User,
  Play,
  Pause,
  CheckCircle,
  ChevronRight,
  FileText,
  Radio,
  UserCheck,
  Folder,
  Plus,
  Search,
  DollarSign,
  Home,
  BarChart3,
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
  const dashboardRef = useRef(null)
  const [activeSection, setActiveSection] = useState("calling")
  const [chatMessages, setChatMessages] = useState([
    { id: 1, role: "assistant", text: "Hello! I'm your NEXOVA AI assistant. How can I help you today?" },
  ])
  const [chatInput, setChatInput] = useState("")
  const [isChatOpen, setIsChatOpen] = useState(true)
  const [chatSessionId, setChatSessionId] = useState(null)
  const [workflowRunning, setWorkflowRunning] = useState(false)
  const [workflowMessages, setWorkflowMessages] = useState([])
  const workflowEndRef = useRef(null)
  const workflowChatRef = useRef(null)

  const ensureChatSession = async () => {
    if (chatSessionId) return chatSessionId
    try {
      const res = await api.post("/api/ai/sessions/", { title: "Dashboard Float Chat" })
      setChatSessionId(res.data.id)
      return res.data.id
    } catch (err) {
      console.error("Failed to create chat session:", err)
      return null
    }
  }

  useEffect(() => {
    if (isChatOpen) {
      ensureChatSession()
    }
  }, [isChatOpen])
  useEffect(() => {
    workflowChatRef.current?.scrollTo({
      top: workflowChatRef.current.scrollHeight,
      behavior: "smooth",
    })
  }, [workflowMessages])

  const sectionRefs = {
    calling: useRef(null),
    messaging: useRef(null),
    scheduling: useRef(null),
    workspace: useRef(null),
  }

  // Queries
  const { data: dashboardData, refetch } = useQuery({
    queryKey: ["dashboardData"],
    queryFn: () => api.get("/api/dashboard/").then((res) => res.data),
  })

  const contacts = dashboardData?.contacts || []
  const deals = dashboardData?.deals || []
  const tasks = dashboardData?.tasks || []
  const aiUsage = dashboardData?.aiUsage || {}

  // Computed stats
  const totalContacts = contacts?.length || 0
  const activeDeals = deals?.length || 0
  const pipelineValue = deals?.reduce((acc, deal) => acc + parseFloat(deal.amount || 0), 0) || 0
  const completedTasks = tasks?.filter((t) => t.completed).length || 0
  const pendingTasks = tasks?.filter((t) => !t.completed).length || 0
  const taskCompletionRate = tasks?.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0

  const stats = [
    { value: totalContacts.toString(), label: "Active Contacts", icon: Users },
    { value: `$${(pipelineValue / 1000).toFixed(0)}K`, label: "Pipeline Value", icon: TrendingUp },
    { value: `${taskCompletionRate}%`, label: "Task Execution", icon: CheckCircle },
    { value: aiUsage?.total_requests?.toString() || "0", label: "AI Operations", icon: Zap },
  ]

  // Mouse tracking
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

  // Chat handler
  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!chatInput.trim()) return

    const userText = chatInput
    const userMsg = { id: Date.now(), role: "user", text: userText }
    setChatMessages((prev) => [...prev, userMsg])
    setChatInput("")

    try {
      const sessionId = await ensureChatSession()
      if (!sessionId) throw new Error("No active session")
      
      const res = await api.post(`/api/ai/sessions/${sessionId}/chat/`, { message: userText })
      const reply = res.data.content || res.data.message || "I've processed your instruction."
      
      const aiMsg = {
        id: Date.now() + 1,
        role: "assistant",
        text: reply,
      }
      setChatMessages((prev) => [...prev, aiMsg])
    } catch (err) {
      console.error("Chat error:", err)
      const errorMsg = {
        id: Date.now() + 1,
        role: "assistant",
        text: "Sorry, I am having trouble connecting to AI services. Please verify the AI microservice is active.",
      }
      setChatMessages((prev) => [...prev, errorMsg])
    }
  }

  const scrollToSection = (sectionId) => {
    setActiveSection(sectionId)
    sectionRefs[sectionId]?.current?.scrollIntoView({ behavior: "smooth", block: "start" })
  }

  // AI Workflow Messages
  const workflowPhaseMessages = [
    { step: 1, sender: "ai", text: "Hi 👋\n\nWelcome!\n\nI'm your AI Assistant.\n\nHow can I help you today?" },
    { step: 2, sender: "ai", text: "Let me understand your needs:\n\n• Buy or Rent?\n• Budget?\n• Preferred Area?\n• Beds?\n• Timeline?\n• Cash or Mortgage?" },
    { step: 2, sender: "customer", text: "Buying\nBudget: 50L\nDowntown\n3 Beds\n2 months\nMortgage" },
    { step: 3, sender: "ai", text: "Great match!\n\n🏠 Project A — $48L (Downtown)\n🏠 Project B — $49L (Green Hills)\n🏠 Project C — $52L (Lake View)\n\nAll with brochure & virtual tour." },
    { step: 4, sender: "customer", text: "Does Project A have a pool?" },
    { step: 4, sender: "ai", text: "Yes! 🏊\n\nPool ✓ Gym ✓ Security ✓ Clubhouse\n\nWould you like a site visit?" },
    { step: 5, sender: "customer", text: "Yes, book tomorrow!" },
    { step: 5, sender: "ai", text: "Checking...\n\n✅ Company Calendar clear\n✅ Salesperson available\n\nBooked: Tomorrow 3 PM\nConfirmation sent to your email." },
    { step: 6, sender: "ai", text: "Assigned: Priya Sharma\nSenior Agent · 8 yrs exp\n95% closing rate\nSpecialist: Downtown" },
    { step: 7, sender: "ai", text: "Reminders set:\n🔔 24 hrs → Email/SMS\n🔔 12 hrs → WhatsApp\n🔔 2 hrs → Phone call\n🔔 30 min → Final alert" },
    { step: 8, sender: "ai", text: "How was the visit?\n⭐⭐⭐⭐⭐\n\nThank you for your feedback!" },
    { step: 9, sender: "ai", text: "Smart Follow-up Active:\n5 min → Reminder\n2 hrs → Alternative\n3 days → Special offer\nFestival → Wishes + discount\nPrice drop → Alert" },
    { step: 10, sender: "ai", text: "❤️ Retaining you as a valued customer!\n\nNew projects · Market reports\nBirthday wishes · Festival offers\nReferral rewards · Exclusive deals" },
  ]

 const toggleWorkflow = async () => {
  if (workflowRunning) return;

  setWorkflowRunning(true);
  setWorkflowMessages([]);

  try {
    const res = await api.post("/api/automation/run-workflow/");
    const realSteps = res.data;

    let idx = 0;

    const interval = setInterval(() => {
      if (idx >= realSteps.length) {
        clearInterval(interval);
        setWorkflowRunning(false);
        refetch();
        return;
      }

      const message = realSteps[idx];

      setWorkflowMessages((prev) => [...prev, message]);

      idx++;
    }, 1000);
  } catch (error) {
    console.error("Workflow run failed:", error);
    setWorkflowRunning(false);
  }
};

  const sections = [
    { id: "calling", label: "AI Calling", icon: Phone },
    { id: "messaging", label: "AI Messaging", icon: MessageSquare },
    { id: "scheduling", label: "Scheduling", icon: Calendar },
    { id: "workspace", label: "Workspace", icon: Building2 },
  ]

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={dashboardRef}>
      {/* Background Effects */}
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
      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-8 pb-16 lg:px-12 space-y-12">
        
        {/* Header */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between animate-fade-in">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground">
              NEXOVA <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">AI</span>
            </h1>
            <p className="text-muted-foreground text-sm mt-2">
              Hello, {user?.first_name || user?.username}. Your AI employees are ready.
            </p>
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-teal-500/30 bg-teal-500/10 px-4 py-2.5 shadow-premium backdrop-blur-md animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <Sparkles className="h-4 w-4 text-teal-500 animate-pulse" />
            <span className="text-xs font-bold text-teal-500">AI Assistant Active</span>
          </div>
        </div>

        {/* Section Navigation / Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2 animate-fade-in" style={{ animationDelay: "0.1s" }}>
          {sections.map((section) => {
            const Icon = section.icon
            return (
              <button
                key={section.id}
                onClick={() => scrollToSection(section.id)}
                className={`dashboard-card flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold whitespace-nowrap transition-all duration-300 ${
                  activeSection === section.id
                    ? "border-teal-500 bg-teal-500/10 text-teal-500 shadow-lg shadow-teal-500/20"
                    : "border-border bg-card/60 text-muted-foreground hover:text-foreground"
                }`}
              >
                <Icon className="h-4 w-4" />
                {section.label}
              </button>
            )
          })}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-fade-in" style={{ animationDelay: "0.15s" }}>
          {stats.map((stat, i) => {
            const Icon = stat.icon
            return (
              <div
                key={i}
                className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark overflow-hidden text-center"
                style={{ animationDelay: `${0.15 + i * 0.05}s` }}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <div className="flex justify-center mb-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-500/10 text-teal-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                      <Icon className="h-5 w-5" />
                    </div>
                  </div>
                  <p className="text-2xl font-extrabold bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">
                    {stat.value}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1 font-medium uppercase tracking-wider">{stat.label}</p>
                </div>
              </div>
            )
          })}
        </div>

        {/* ==================== AI CALLING SECTION ==================== */}
        <section ref={sectionRefs.calling} className="scroll-mt-24 space-y-6">
          <div className="dashboard-card group relative rounded-3xl border border-border bg-card/60 p-8 backdrop-blur-xl shadow-2xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-start gap-6 mb-8">
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-teal-500/10 to-amber-500/10 text-teal-500 border border-teal-500/10">
                  <Phone className="h-8 w-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-extrabold text-foreground">AI Calling Employee</h2>
                  <p className="text-sm text-muted-foreground mt-2 max-w-2xl">
                    Automated outbound calls that qualify leads, answer questions, and book appointments 24/7. Just like your best sales rep, but never sleeps.
                  </p>
                </div>
              </div>

              {/* How It Works - Animated Steps */}
              <div className="grid md:grid-cols-4 gap-4 mb-8">
                {[
                  { step: "1", title: "Lead Inbound", desc: "AI receives call/lead instantly", color: "teal" },
                  { step: "2", title: "Qualify", desc: "AI asks qualifying questions", color: "amber" },
                  { step: "3", title: "Book", desc: "Schedules appointment automatically", color: "emerald" },
                  { step: "4", title: "Notify", desc: "Sends confirmation to team", color: "teal" },
                ].map((item, i) => (
                  <div key={i} className="dashboard-card relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md text-center overflow-hidden">
                    <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none
                      ${item.color === 'teal' ? 'from-teal-500/0 via-teal-500/10 to-teal-500/0' : item.color === 'amber' ? 'from-amber-500/0 via-amber-500/10 to-amber-500/0' : 'from-emerald-500/0 via-emerald-500/10 to-emerald-500/0'}`} />
                    <div className="relative z-10">
                      <div className="flex justify-center mb-3">
                        <div className={`flex h-10 w-10 items-center justify-center rounded-xl text-sm font-bold ${
                          item.color === 'teal' ? 'bg-teal-500/10 text-teal-500' : item.color === 'amber' ? 'bg-amber-500/10 text-amber-500' : 'bg-emerald-500/10 text-emerald-500'
                        }`}>
                          {item.step}
                        </div>
                      </div>
                      <h3 className="text-sm font-bold text-foreground mb-1">{item.title}</h3>
                      <p className="text-[10px] text-muted-foreground">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Deals Pipeline */}
              <div className="rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
                <h3 className="text-base font-bold text-foreground mb-4">Live Deals Pipeline</h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-left text-sm">
                    <thead className="bg-muted/40 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      <tr>
                        <th className="px-4 py-3">Deal</th>
                        <th className="px-4 py-3">Amount</th>
                        <th className="px-4 py-3">Stage</th>
                        <th className="px-4 py-3">Contact</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {deals?.slice(0, 5).map((deal) => (
                        <tr key={deal.id} className="hover:bg-muted/20">
                          <td className="px-4 py-3 font-medium text-foreground">{deal.title}</td>
                          <td className="px-4 py-3 text-emerald-500 font-semibold">${parseFloat(deal.amount).toLocaleString()}</td>
                          <td className="px-4 py-3">
                            <span className="rounded-full bg-teal-500/10 px-2.5 py-0.5 text-xs font-semibold text-teal-500">
                              {deal.stage_details?.name || "New"}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-muted-foreground">
                            {deal.contact_details ? `${deal.contact_details.first_name} ${deal.contact_details.last_name}` : "-"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ==================== AI MESSAGING WORKFLOW SECTION ==================== */}
        <section ref={sectionRefs.messaging} className="scroll-mt-24 space-y-6">
          <div className="dashboard-card group relative rounded-3xl border border-border bg-card/60 backdrop-blur-xl shadow-2xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-amber-500/10 via-teal-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-start gap-6 px-8 pt-8 pb-6">
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-amber-500/10 to-teal-500/10 text-amber-500 border border-amber-500/10">
                  <MessageSquare className="h-7 w-7" />
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-extrabold text-foreground">AI Messaging</h2>
                  <p className="text-sm text-muted-foreground mt-1 max-w-2xl">
                    Automated conversations from first greeting to post-sale retention — fully handled by AI.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={toggleWorkflow}
                    className={`flex items-center gap-2 rounded-xl px-5 py-2.5 text-xs font-bold transition-all duration-300 ${workflowRunning ? 'bg-gradient-to-r from-teal-500 to-amber-500 text-white shadow-lg shadow-teal-500/20' : 'bg-muted/50 text-muted-foreground hover:text-foreground border border-border'}`}
                    disabled={workflowRunning}
                  >
                    {workflowRunning ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
                    {workflowRunning ? 'Running...' : 'Run Demo'}
                  </button>
                </div>
              </div>

               <div className="mx-8 mb-8 grid lg:grid-cols-5 gap-4 rounded-2xl border border-border bg-background/50" style={{ height: '420px' }}>
                {/* Left side - descriptions */}
                <div className="lg:col-span-2 border-r border-border bg-muted/10 flex flex-col min-h-0">
                  <div className="px-5 py-4 border-b border-border bg-muted/20">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Workflow Phases</span>
                  </div>
                  <div className="flex-1 min-h-0 overflow-y-auto px-5 py-4 space-y-3 bg-muted/5 hide-scrollbar">
                    {[
                      { num: 1, title: "Welcome", desc: "AI greets the lead" },
                      { num: 2, title: "Qualify", desc: "Asks qualifying questions" },
                      { num: 3, title: "Recommend", desc: "Shows matching projects" },
                      { num: 4, title: "QA", desc: "Answers customer questions" },
                      { num: 5, title: "Book", desc: "Checks calendars, books slot" },
                      { num: 6, title: "Assign", desc: "Assigns best salesperson" },
                      { num: 7, title: "Remind", desc: "Sends timed reminders" },
                      { num: 8, title: "Rate", desc: "Collects feedback" },
                      { num: 9, title: "Follow-up", desc: "Smart follow-up engine" },
                      { num: 10, title: "Retain", desc: "Long-term relationship" },
                    ].map((step) => {

                      const currentStep = workflowMessages[workflowMessages.length - 1]?.step ?? 0;
                      // const currentStep = workflowMessages.length > 0 ? workflowMessages[workflowMessages.length - 1].step : 0
                      const isCompleted = workflowRunning && currentStep >= step.num
                      const isActive = workflowRunning && currentStep === step.num

                      return (
                        <div key={step.num} className={`flex items-start gap-3 transition-all duration-300 ${isActive ? 'text-foreground' : 'text-muted-foreground'}`}>
                          <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-[10px] font-bold mt-0.5 transition-all duration-300 ${
                            isActive ? 'bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-sm' : 'bg-muted/50 text-muted-foreground'
                          }`}>
                            {isCompleted ? <CheckCircle className="h-3.5 w-3.5" /> : step.num}
                          </div>
                          <div>
                            <p className="text-xs font-bold">{step.title}</p>
                            <p className="text-[10px] text-muted-foreground">{step.desc}</p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Right side - chat messages */}
                <div className="lg:col-span-3 flex flex-col min-h-0">
                  <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/20">
                    <div className="flex h-2.5 w-2.5 rounded-full bg-red-500/80" />
                    <div className="flex h-2.5 w-2.5 rounded-full bg-yellow-500/80" />
                    <div className="flex h-2.5 w-2.5 rounded-full bg-green-500/80" />
                    <span className="ml-2 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">NEXOVA AI Assistant</span>
                  </div>
                  <div ref={workflowChatRef} className="flex-1 min-h-0 overflow-y-auto p-4 space-y-3 bg-muted/5 hide-scrollbar scrollbar-thin scrollbar-thumb-teal-500/40 scrollbar-track-transparent" >
                    {!workflowRunning && workflowMessages.length === 0 && (
                      <div className="flex h-full flex-col items-center justify-center text-center">
                        <MessageSquare className="h-8 w-8 text-muted-foreground/20 mx-auto mb-2" />
                        <p className="text-xs text-muted-foreground">Click "Run Demo" to watch</p>
                      </div>
                    )}
                    {workflowMessages.map((msg, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: msg.sender === "ai" ? -20 : 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.35, ease: "easeOut" }}
                        className={`flex gap-2 ${msg.sender === "ai" ? "" : "flex-row-reverse"}`}
                      >
                        <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-[10px] font-bold ${
                          msg.sender === "ai" ? "bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-sm" : "bg-muted text-muted-foreground border border-border"
                        }`}>
                          {msg.sender === "ai" ? <Bot className="h-3.5 w-3.5" /> : <User className="h-3.5 w-3.5" />}
                        </div>
                        <div className={`flex-1 max-w-[90%] rounded-xl px-3 py-2 text-[11px] leading-relaxed ${
                          msg.sender === "ai"
                            ? "bg-card/80 border border-teal-500/15 text-foreground shadow-sm"
                            : "bg-gradient-to-r from-teal-500/90 to-amber-500/90 text-white shadow-sm"
                        }`}>
                          <p className="whitespace-pre-wrap">{msg.text}</p>
                        </div>
                      </motion.div>
                    ))}
                    {workflowRunning && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex gap-2"
                      >
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-sm">
                          <Bot className="h-3.5 w-3.5" />
                        </div>
                        <div className="rounded-xl px-3 py-2 bg-card/80 border border-teal-500/15">
                          <div className="flex gap-1">
                            <div className="h-1.5 w-1.5 rounded-full bg-teal-500 animate-pulse" />
                            <div className="h-1.5 w-1.5 rounded-full bg-teal-500 animate-pulse" style={{ animationDelay: '0.2s' }} />
                            <div className="h-1.5 w-1.5 rounded-full bg-teal-500 animate-pulse" style={{ animationDelay: '0.4s' }} />
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ==================== SMART SCHEDULING SECTION ==================== */}
        <section ref={sectionRefs.scheduling} className="scroll-mt-24 space-y-6">
          <div className="dashboard-card group relative rounded-3xl border border-border bg-card/60 p-8 backdrop-blur-xl shadow-2xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 via-teal-500/5 to-amber-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-start gap-6 mb-8">
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-emerald-500/10 to-teal-500/10 text-emerald-500 border border-emerald-500/10">
                  <Calendar className="h-8 w-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-extrabold text-foreground">Smart Scheduling Employee</h2>
                  <p className="text-sm text-muted-foreground mt-2 max-w-2xl">
                    AI manages your calendar, schedules site visits, sends reminders, and optimizes appointments around the clock.
                  </p>
                </div>
              </div>

              {/* Scheduling Animation Steps */}
              <div className="grid md:grid-cols-4 gap-4 mb-8">
                {[
                  { step: "1", title: "Request", desc: "Lead requests visit", icon: Calendar, color: "emerald" },
                  { step: "2", title: "Check", desc: "AI checks calendar", icon: CheckCircle, color: "teal" },
                  { step: "3", title: "Book", desc: "Confirms appointment", icon: Calendar, color: "amber" },
                  { step: "4", title: "Remind", desc: "Sends SMS/Email reminder", icon: Send, color: "emerald" },
                ].map((item, i) => {
                  const Icon = item.icon
                  return (
                    <div key={i} className="dashboard-card relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md text-center overflow-hidden">
                      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none
                        ${item.color === 'teal' ? 'from-teal-500/0 via-teal-500/10 to-teal-500/0' : item.color === 'amber' ? 'from-amber-500/0 via-amber-500/10 to-amber-500/0' : 'from-emerald-500/0 via-emerald-500/10 to-emerald-500/0'}`} />
                      <div className="relative z-10">
                        <div className="flex justify-center mb-3">
                          <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${
                            item.color === 'teal' ? 'bg-teal-500/10 text-teal-500' : item.color === 'amber' ? 'bg-amber-500/10 text-amber-500' : 'bg-emerald-500/10 text-emerald-500'
                          }`}>
                            <Icon className="h-6 w-6" />
                          </div>
                        </div>
                        <h3 className="text-sm font-bold text-foreground mb-1">{item.title}</h3>
                        <p className="text-[10px] text-muted-foreground">{item.desc}</p>
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Tasks */}
              <div className="rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md">
                <h3 className="text-base font-bold text-foreground mb-4">Upcoming Appointments</h3>
                <div className="space-y-3">
                  {tasks?.filter(t => !t.completed).slice(0, 4).map((task, i) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-xl bg-muted/30 hover:bg-muted/50 transition-all">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500">
                          <Calendar className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-foreground">{task.title}</p>
                          <p className="text-[10px] text-muted-foreground">{task.due_date ? new Date(task.due_date).toLocaleDateString() : "No date"}</p>
                        </div>
                      </div>
                      <span className="text-[10px] font-bold text-amber-500 bg-amber-500/10 px-2 py-1 rounded-full">Pending</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ==================== COMPANY WORKSPACE SECTION ==================== */}
        <section ref={sectionRefs.workspace} className="scroll-mt-24 space-y-6">
          <div className="dashboard-card group relative rounded-3xl border border-border bg-card/60 p-8 backdrop-blur-xl shadow-2xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
            <div className="relative z-10">
              <div className="flex items-start gap-6 mb-8">
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-teal-500/10 to-amber-500/10 text-teal-500 border border-teal-500/10">
                  <Building2 className="h-8 w-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-extrabold text-foreground">Company Workspace</h2>
                  <p className="text-sm text-muted-foreground mt-2 max-w-2xl">
                    Centralized project hub with knowledge base, broadcasting, documents, and AI-powered customer matching.
                  </p>
                </div>
              </div>

              {/* Workspace Modules */}
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {[
                  { title: "Project Knowledge Base", desc: "Documentation & references", icon: FileText, color: "teal" },
                  { title: "Smart Broadcasting", desc: "AI announcements across channels", icon: Radio, color: "amber" },
                  { title: "AI Customer Matching", desc: "Lead-to-project matching", icon: UserCheck, color: "emerald" },
                  { title: "Project Analytics", desc: "Performance insights", icon: BarChart3, color: "teal" },
                  { title: "Document Manager", desc: "Organize project files", icon: Folder, color: "amber" },
                  { title: "More Modules", desc: "Coming soon...", icon: Plus, color: "emerald" },
                ].map((item, i) => {
                  const Icon = item.icon
                  return (
                    <div key={i} className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark overflow-hidden cursor-pointer">
                      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none
                        ${item.color === 'teal' ? 'from-teal-500/0 via-teal-500/10 to-teal-500/0' : item.color === 'amber' ? 'from-amber-500/0 via-amber-500/10 to-amber-500/0' : 'from-emerald-500/0 via-emerald-500/10 to-emerald-500/0'}`} />
                      <div className="relative z-10">
                        <div className={`flex h-10 w-10 items-center justify-center rounded-xl mb-3 ${
                          item.color === 'teal' ? 'bg-teal-500/10 text-teal-500' : item.color === 'amber' ? 'bg-amber-500/10 text-amber-500' : 'bg-emerald-500/10 text-emerald-500'
                        }`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <h3 className="text-sm font-bold text-foreground mb-1">{item.title}</h3>
                        <p className="text-[10px] text-muted-foreground">{item.desc}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </section>

      </div>

      {/* Sticky AI Chat Panel */}
      {isChatOpen && (
        <div className="fixed bottom-6 right-6 z-40 w-[360px] max-h-[500px] rounded-3xl border border-border bg-card/80 backdrop-blur-2xl shadow-2xl overflow-hidden animate-fade-in flex flex-col">
          {/* Chat Header */}
          <div className="flex items-center justify-between p-4 border-b border-border bg-muted/10">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-premium">
                <Bot className="h-5 w-5 animate-pulse" />
              </div>
              <div>
                <h3 className="text-sm font-extrabold text-foreground">NEXOVA AI Assistant</h3>
                <p className="text-[10px] text-emerald-500 font-medium">Online • Ready to help</p>
              </div>
            </div>
            <button
              onClick={() => setIsChatOpen(false)}
              className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted/50 text-muted-foreground hover:text-foreground transition-all"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-3 max-h-[320px] bg-muted/5 hide-scrollbar">
            {chatMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[85%] animate-fade-in ${
                  msg.role === "assistant" ? "" : "ml-auto flex-row-reverse"
                }`}
              >
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${
                    msg.role === "assistant" ? "bg-teal-500/10 text-teal-500" : "bg-muted text-muted-foreground"
                  }`}
                >
                  {msg.role === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                </div>
                <div
                  className={`rounded-2xl px-4 py-2.5 text-xs shadow-premium border backdrop-blur-md ${
                    msg.role === "assistant"
                      ? "bg-card/80 border-border text-foreground"
                      : "bg-gradient-to-r from-teal-500 to-amber-600 border-teal-500/20 text-white"
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-3 border-t border-border bg-card/80 backdrop-blur-md flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask AI anything..."
              className="flex-1 rounded-xl border border-border bg-muted/40 px-4 py-2.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all bg-muted/5 hide-scrollbar"
            />
            <button
              type="submit"
              disabled={!chatInput.trim()}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 text-white shadow-premium hover:shadow-premiumDark disabled:opacity-50 transition-all"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}

      {/* Chat Toggle Button (when closed) */}
      {!isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-teal-500 to-amber-500 text-white shadow-premium hover:shadow-premiumDark transition-all animate-pulse"
        >
          <MessageSquare className="h-6 w-6" />
        </button>
      )}
    </div>
  )
}
