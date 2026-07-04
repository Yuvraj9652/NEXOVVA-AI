import React, { useState, useEffect } from "react"
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
    <div className="flex h-[calc(100vh-6rem)] gap-6 overflow-hidden">
      {/* Session List Left panel */}
      <div className="w-80 rounded-2xl border border-border bg-card p-4 flex flex-col shadow-premium shrink-0">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-bold text-foreground flex items-center gap-1.5">
            <MessageSquare className="h-4 w-4 text-primary" /> Discussions
          </h2>
          <button
            onClick={() => createSessionMutation.mutate()}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-all"
            title="Start New Thread"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 space-y-2 overflow-y-auto pr-1">
          {sessions && sessions.length > 0 ? (
            sessions.map((sess) => (
              <button
                key={sess.id}
                onClick={() => setActiveSession(sess.id)}
                className={`w-full flex items-start gap-3 rounded-lg px-3 py-2.5 text-left text-xs transition-all ${
                  activeSession === sess.id
                    ? "bg-primary text-primary-foreground shadow-premium"
                    : "hover:bg-muted text-muted-foreground hover:text-foreground"
                }`}
              >
                <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded bg-muted/40">
                  <Bot className="h-3.5 w-3.5" />
                </div>
                <div className="overflow-hidden">
                  <p className="font-semibold truncate">{sess.title}</p>
                  <span className="text-[10px] opacity-75">
                    {new Date(sess.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </button>
            ))
          ) : (
            <p className="text-center py-8 text-xs text-muted-foreground">
              No threads started. Click + to begin.
            </p>
          )}
        </div>
      </div>

      {/* Chat Conversation Feed panel */}
      <div className="flex-1 rounded-2xl border border-border bg-card flex flex-col shadow-premium overflow-hidden">
        {/* Header */}
        <div className="border-b border-border bg-muted/10 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Bot className="h-5 w-5 animate-pulse" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-foreground">Gemini Real Estate Assistant</h3>
              <p className="text-[10px] text-muted-foreground">Active model: gemini-1.5-flash</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 rounded-full bg-violet-500/10 px-3 py-1 text-xs text-violet-500 font-bold">
            <Zap className="h-3.5 w-3.5" /> Server Connected
          </div>
        </div>

        {/* Messages feed */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-muted/5">
          {activeSession ? (
            messages && messages.length > 0 ? (
              messages.map((msg) => {
                const isAssistant = msg.role === "assistant"
                return (
                  <div
                    key={msg.id}
                    className={`flex gap-3 max-w-[80%] ${
                      isAssistant ? "" : "ml-auto flex-row-reverse"
                    }`}
                  >
                    <div
                      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${
                        isAssistant ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {isAssistant ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                    </div>
                    <div
                      className={`rounded-xl px-4 py-2.5 text-xs shadow-premium border ${
                        isAssistant
                          ? "bg-card border-border text-foreground"
                          : "bg-primary border-primary/20 text-primary-foreground"
                      }`}
                    >
                      <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="flex h-full flex-col items-center justify-center text-center">
                <Sparkles className="h-10 w-10 text-primary animate-pulse mb-3" />
                <h4 className="text-sm font-bold text-foreground">Start the Conversation</h4>
                <p className="text-xs text-muted-foreground mt-1 max-w-sm">
                  Ask details about real estate sales tactics, drafting property brochures, or query formulas.
                </p>
              </div>
            )
          ) : (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <MessageSquare className="h-10 w-10 text-muted-foreground mb-3" />
              <h4 className="text-sm font-bold text-foreground">Select a Discussion Session</h4>
              <p className="text-xs text-muted-foreground mt-1">
                Choose a session thread from the left pane or spawn a new conversation.
              </p>
            </div>
          )}
        </div>

        {/* Input area */}
        {activeSession && (
          <form onSubmit={handleSend} className="border-t border-border p-4 bg-card flex gap-3">
            <input
              type="text"
              required
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask anything or request property matchmaker..."
              className="flex-1 rounded-lg border border-border bg-muted/40 px-4 py-2.5 text-xs focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button
              type="submit"
              disabled={sendMessageMutation.isPending || !inputMessage.trim()}
              className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground hover:bg-primary/95 disabled:opacity-50 transition-all shrink-0"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        )}
      </div>

      {/* Preset Library Right panel */}
      <div className="w-80 rounded-2xl border border-border bg-card p-4 flex flex-col shadow-premium shrink-0">
        <h3 className="text-sm font-bold text-foreground mb-4 flex items-center gap-1.5">
          <Terminal className="h-4 w-4 text-primary" /> AI Presets Registry
        </h3>

        {(!templates || templates.length === 0) && (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-4 border border-dashed border-border rounded-xl">
            <ClipboardList className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-xs text-muted-foreground mb-4">No presets defined.</p>
            <button
              onClick={handleSeedTemplates}
              className="rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-primary-foreground"
            >
              Seed Presets
            </button>
          </div>
        )}

        {templates && templates.length > 0 && (
          <div className="flex-1 space-y-3 overflow-y-auto pr-1">
            {templates.map((temp) => (
              <button
                key={temp.id}
                onClick={() => handlePresetSelect(temp.template)}
                className="w-full text-left p-3 rounded-lg border border-border bg-muted/20 hover:border-primary/50 transition-all group"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-foreground leading-none">
                    {temp.name}
                  </span>
                  <span className="text-[8px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-bold uppercase">
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
  )
}
