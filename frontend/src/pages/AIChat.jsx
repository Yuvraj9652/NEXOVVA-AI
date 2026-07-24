import React, { useState, useEffect, useRef } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  MessageSquare,
  Send,
  Plus,
  Sparkles,
  Bot,
  User,
  Zap,
  Terminal,
  Notebook,
  ClipboardList,
} from "lucide-react"
import api from "../api/client"

export default function AIChat() {
  const [activeSession, setActiveSession] = useState(null)
  const [inputMessage, setInputMessage] = useState("")
  const queryClient = useQueryClient()
  const chatRef = useRef(null)

  // Mouse tracking for dashboard cards
  useEffect(() => {
    const boxElements = document.querySelectorAll(".dashboard-card, .chart-box")
    
    const handleMouseMove = (e) => {
      const element = e.target.closest(".dashboard-card") || e.target.closest(".chart-box")
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
      const element = e.target.closest(".dashboard-card") || e.target.closest(".chart-box")
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

  // Queries
  const { data: sessions, isLoading: loadingSessions } = useQuery({
    queryKey: ["aiSessions"],
    queryFn: () => api.get("/api/ai/sessions/").then((res) => res.data.results || []),
  })

  const { data: messages, refetch: refetchMessages } = useQuery({
    queryKey: ["aiMessages", activeSession],
    queryFn: () =>
      api.get(`/api/ai/sessions/${activeSession}/messages/`).then((res) => res.data || []),
    enabled: !!activeSession,
  })

  const { data: templates } = useQuery({
    queryKey: ["promptTemplates"],
    queryFn: () => api.get("/api/ai/templates/").then((res) => res.data.results || []),
  })

  // Mutations
  const createSessionMutation = useMutation({
    mutationFn: () => api.post("/api/ai/sessions/", { title: "Real Estate Discussion" }),
    onSuccess: (res) => {
      queryClient.invalidateQueries(["aiSessions"])
      setActiveSession(res.data.id)
    },
  })

  const sendMessageMutation = useMutation({
    mutationFn: (msg) => api.post(`/api/ai/sessions/${activeSession}/chat/`, { message: msg }),
    onSuccess: () => {
      queryClient.invalidateQueries(["aiMessages", activeSession])
      setInputMessage("")
    },
  })

  const seedTemplatesMutation = useMutation({
    mutationFn: async () => {
      const defaultTemplates = [
        {
          name: "Lead Follow-up Email",
          template: "Draft a highly professional real estate follow up email for a buyer looking for {{bedrooms}} bedrooms and budget around {{budget}}.",
          purpose: "Sales follow-up copy templates",
        },
        {
          name: "Property Description Outline",
          template: "Analyze and structure a premium real estate description. Highlight: {{features}}.",
          purpose: "Property listings advertising copies",
        },
      ]
      for (let t of defaultTemplates) {
        await api.post("/api/ai/templates/", t)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(["promptTemplates"])
    },
  })

  const handleSend = (e) => {
    e.preventDefault()
    if (!inputMessage.trim() || sendMessageMutation.isPending) return
    sendMessageMutation.mutate(inputMessage)
  }

  const handlePresetSelect = (presetText) => {
    setInputMessage(presetText)
  }

  const handleSeedTemplates = () => {
    seedTemplatesMutation.mutate()
  }

  useEffect(() => {
    if (sessions && sessions.length > 0 && !activeSession) {
      setActiveSession(sessions[0].id)
    }
  }, [sessions, activeSession])

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={chatRef}>
      {/* Static Background Image */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1920&h=1080&fit=crop"
          alt="Modern Real Estate Building"
          className="w-full h-full object-cover opacity-30"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/60 to-background/80" />
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

      {/* Main Chat Content */}
      <div className="relative z-10 flex flex-col lg:flex-row gap-6 overflow-hidden px-6 lg:px-12 pt-8 pb-16 h-full">
        
        {/* Session List Left panel */}
        <div className="dashboard-card group relative w-full lg:w-80 rounded-3xl border border-border bg-card/60 p-5 flex flex-col shadow-2xl backdrop-blur-xl shrink-0 overflow-hidden animate-fade-in">
          <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
          <div className="relative z-10 flex items-center justify-between mb-4">
            <h2 className="text-sm font-extrabold text-foreground flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-500/10 text-teal-500">
                <MessageSquare className="h-4 w-4" />
              </div>
              Discussions
            </h2>
            <button
              onClick={() => createSessionMutation.mutate()}
              className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-premium hover:shadow-premiumDark transition-all"
              title="Start New Thread"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          <div className="relative z-10 flex-1 space-y-2 overflow-y-auto pr-1">
            {sessions && sessions.length > 0 ? (
              sessions.map((sess, i) => (
                <button
                  key={sess.id}
                  onClick={() => setActiveSession(sess.id)}
                  className={`dashboard-card w-full flex items-start gap-3 rounded-2xl px-3 py-3 text-left text-xs transition-all duration-300 overflow-hidden
                    ${activeSession === sess.id
                      ? 'border-teal-500 bg-teal-500/10 shadow-lg shadow-teal-500/20' 
                      : 'border-border bg-card/40 hover:bg-card/60 hover:-translate-y-0.5'
                    }`}
                  style={{ animationDelay: `${i * 0.05}s` }}
                >
                  <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-lg bg-muted/40 text-muted-foreground">
                    <Bot className="h-3.5 w-3.5" />
                  </div>
                  <div className="overflow-hidden">
                    <p className="font-bold truncate text-foreground">{sess.title}</p>
                    <span className="text-[10px] text-muted-foreground">
                      {new Date(sess.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </button>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-muted/50 text-muted-foreground mb-3">
                  <MessageSquare className="h-6 w-6" />
                </div>
                <p className="text-xs text-muted-foreground">
                  No threads started. Click + to begin.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Chat Conversation Feed panel */}
        <div className="dashboard-card group relative flex-1 rounded-3xl border border-border bg-card/60 flex flex-col shadow-2xl backdrop-blur-xl overflow-hidden animate-fade-in" style={{ animationDelay: "0.1s" }}>
          <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
          
          {/* Header */}
          <div className="relative z-10 border-b border-border bg-muted/10 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-premium">
                <Bot className="h-5 w-5 animate-pulse" />
              </div>
              <div>
                <h3 className="text-sm font-extrabold text-foreground">Gemini Real Estate Assistant</h3>
                <p className="text-[10px] text-muted-foreground">Active model: gemini-1.5-flash</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 rounded-full bg-violet-500/10 px-3 py-1 text-xs text-violet-500 font-bold border border-violet-500/20">
              <Zap className="h-3.5 w-3.5" /> Server Connected
            </div>
          </div>

          {/* Messages feed */}
          <div className="relative z-10 flex-1 p-6 overflow-y-auto space-y-4 bg-muted/5">
            {activeSession ? (
              messages && messages.length > 0 ? (
                messages.map((msg, i) => {
                  const isAssistant = msg.role === "assistant"
                  return (
                    <div
                      key={msg.id}
                      className={`flex gap-3 max-w-[80%] animate-fade-in ${
                        isAssistant ? "" : "ml-auto flex-row-reverse"
                      }`}
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
                })
              ) : (
                <div className="flex h-full flex-col items-center justify-center text-center">
                  <div className="relative mb-4">
                    <div className="absolute -inset-4 rounded-full bg-teal-500/20 blur-xl animate-pulse" />
                    <Sparkles className="relative h-10 w-10 text-teal-500 animate-pulse" />
                  </div>
                  <h4 className="text-sm font-extrabold text-foreground">Start the Conversation</h4>
                  <p className="text-xs text-muted-foreground mt-1 max-w-sm">
                    Ask details about real estate sales tactics, drafting property brochures, or query formulas.
                  </p>
                </div>
              )
            ) : (
              <div className="flex h-full flex-col items-center justify-center text-center">
                <div className="inline-flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-tr from-teal-500/10 to-amber-500/10 text-muted-foreground mb-4 shadow-lg">
                  <MessageSquare className="h-8 w-8" />
                </div>
                <h4 className="text-sm font-extrabold text-foreground">Select a Discussion Session</h4>
                <p className="text-xs text-muted-foreground mt-1">
                  Choose a session thread from the left pane or spawn a new conversation.
                </p>
              </div>
            )}
          </div>

          {/* Input area */}
          {activeSession && (
            <form onSubmit={handleSend} className="relative z-10 border-t border-border p-4 bg-card/80 backdrop-blur-md flex gap-3">
              <input
                type="text"
                required
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask anything or request property matchmaker..."
                className="flex-1 rounded-xl border border-border bg-muted/40 px-4 py-2.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500 transition-all"
              />
              <button
                type="submit"
                disabled={sendMessageMutation.isPending || !inputMessage.trim()}
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 text-white shadow-premium hover:shadow-premiumDark disabled:opacity-50 transition-all shrink-0"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          )}
        </div>

        {/* Preset Library Right panel */}
        <div className="dashboard-card group relative w-full lg:w-80 rounded-3xl border border-border bg-card/60 p-5 flex flex-col shadow-2xl backdrop-blur-xl shrink-0 overflow-hidden animate-fade-in" style={{ animationDelay: "0.2s" }}>
          <div className="absolute inset-0 bg-gradient-to-r from-amber-500/10 via-teal-500/5 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
          <div className="relative z-10">
            <h3 className="text-sm font-extrabold text-foreground mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-500/10 text-amber-500">
                <Terminal className="h-4 w-4" />
              </div>
              AI Presets Registry
            </h3>

            {(!templates || templates.length === 0) && (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-4 border border-dashed border-border rounded-2xl">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-muted/50 text-muted-foreground mb-3">
                  <ClipboardList className="h-6 w-6" />
                </div>
                <p className="text-xs text-muted-foreground mb-4">No presets defined.</p>
                <button
                  onClick={handleSeedTemplates}
                  className="rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-4 py-2 text-xs font-bold text-white shadow-premium hover:shadow-premiumDark transition-all"
                >
                  Seed Presets
                </button>
              </div>
            )}

            {templates && templates.length > 0 && (
              <div className="flex-1 space-y-3 overflow-y-auto pr-1">
                {templates.map((temp, i) => (
                  <button
                    key={temp.id}
                    onClick={() => handlePresetSelect(temp.template)}
                    className="dashboard-card w-full text-left p-4 rounded-2xl border border-border bg-card/40 hover:border-teal-500/30 hover:bg-card/60 transition-all duration-300 group overflow-hidden"
                    style={{ animationDelay: `${0.3 + i * 0.05}s` }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-extrabold text-foreground leading-none">
                        {temp.name}
                      </span>
                      <span className="text-[8px] bg-gradient-to-r from-teal-500/20 to-amber-500/20 text-teal-500 px-2 py-0.5 rounded-lg font-bold uppercase border border-teal-500/20">
                        Preset
                      </span>
                    </div>
                    <p className="text-[10px] text-muted-foreground line-clamp-3 leading-relaxed">
                      {temp.template}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
