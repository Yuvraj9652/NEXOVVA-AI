import React, { useEffect, useRef, useState } from "react"
import { FileText, Search, BarChart3, Upload, FolderOpen, Clock, X, Send } from "lucide-react"
import { useQuery } from "@tanstack/react-query"
import api from "../api/client"

export default function ProjectKnowledgeBase() {
  const knowledgeBaseRef = useRef(null)
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [question, setQuestion] = useState("")
  const [chatHistory, setChatHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")

  const { data: documents = [] } = useQuery({
    queryKey: ["documents"],
    queryFn: () => api.get("/api/documents/").then((res) => res.data.results || res.data || []),
  })

  // Filter documents based on search input
  const filteredDocs = documents.filter((doc) =>
    doc.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

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
  }, [documents])

  const handleAskQuestion = async (e) => {
    e.preventDefault()
    if (!question.trim() || !selectedDoc) return

    const userQ = question
    setQuestion("")
    setChatHistory((prev) => [...prev, { role: "user", text: userQ }])
    setLoading(true)

    try {
      const filename = selectedDoc.file.split("/").pop()
      const res = await api.post("/api/ai/ask-document/", {
        filename: filename,
        question: userQ,
      })
      const answer = res.data.answer || "No response details generated."
      setChatHistory((prev) => [...prev, { role: "assistant", text: answer }])
    } catch (err) {
      console.error(err)
      setChatHistory((prev) => [
        ...prev,
        { role: "assistant", text: "Failed to fetch response from vector search database." },
      ])
    } finally {
      setLoading(false)
    }
  }

  const openDocChat = (doc) => {
    setSelectedDoc(doc)
    setChatHistory([
      { role: "assistant", text: `Hello! Ask me anything about "${doc.name}". I've indexed its contents.` },
    ])
  }

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground" ref={knowledgeBaseRef}>
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

      {/* Floating orbs */}
      <div className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-teal-400/20 blur-[100px] animate-pulse" />
      <div className="absolute top-1/3 -right-32 h-80 w-80 rounded-full bg-amber-500/15 blur-[100px] animate-pulse" style={{ animationDelay: "1s" }} />

      {/* Main Content */}
      <div className="relative z-10 mx-auto max-w-7xl px-6 pt-8 pb-16 lg:px-12 space-y-8">
        {/* Header Section */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between animate-fade-in">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
              <span className="bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">
                Project Knowledge Base
              </span>
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              Centralized repository for project documentation, specifications, and reference materials.
            </p>
          </div>
          <div className="flex items-center gap-3 animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search materials..."
                className="h-10 w-64 rounded-lg border border-border bg-muted/40 py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>
        </div>

        {/* Knowledge Items Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredDocs.map((item, idx) => {
            const docType = item.file ? item.file.split(".").pop().toUpperCase() : "PDF"
            const updatedStr = new Date(item.updated_at).toLocaleDateString()
            return (
              <div
                key={item.id}
                onClick={() => openDocChat(item)}
                className="dashboard-card group relative rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden cursor-pointer"
                style={{ animationDelay: `${0.1 + idx * 0.1}s` }}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <div className="flex items-start justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10 text-teal-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                      <FileText className="h-5 w-5" />
                    </div>
                    <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-bold text-muted-foreground">{docType}</span>
                  </div>
                  <h3 className="mt-4 text-sm font-bold text-foreground group-hover:text-primary transition-colors">{item.name}</h3>
                  <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {updatedStr}</span>
                    <span>2.5 MB</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* RAG Chatbot Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-lg rounded-3xl border border-border bg-card/95 p-6 shadow-2xl backdrop-blur-md">
            <button
              onClick={() => setSelectedDoc(null)}
              className="absolute right-4 top-4 rounded-xl p-2 text-muted-foreground hover:bg-muted transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
            <h2 className="text-lg font-bold text-foreground pr-8 flex items-center gap-2">
              <FileText className="h-5 w-5 text-teal-500" />
              Ask AI: {selectedDoc.name}
            </h2>
            <p className="text-xs text-muted-foreground mt-1">NEXOVA AI Document Vector Search Chat</p>

            <div className="mt-4 h-64 overflow-y-auto rounded-2xl bg-muted/20 p-4 space-y-3 border border-border">
              {chatHistory.map((msg, i) => (
                <div
                  key={i}
                  className={`flex flex-col max-w-[85%] rounded-2xl p-3 text-sm ${
                    msg.role === "user"
                      ? "ml-auto bg-gradient-to-r from-teal-500 to-teal-600 text-white"
                      : "bg-muted/50 text-foreground border border-border"
                  }`}
                >
                  <span className="text-[10px] font-bold opacity-60 uppercase mb-1">
                    {msg.role === "user" ? "You" : "AI Assistant"}
                  </span>
                  <p className="whitespace-pre-line leading-relaxed">{msg.text}</p>
                </div>
              ))}
              {loading && (
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <div className="h-2 w-2 animate-ping rounded-full bg-teal-500" />
                  AI is analyzing document text...
                </div>
              )}
            </div>

            <form onSubmit={handleAskQuestion} className="mt-4 flex gap-2">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about this file..."
                className="flex-1 h-11 rounded-xl border border-border bg-muted/40 px-4 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              />
              <button
                type="submit"
                disabled={loading}
                className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 text-white hover:opacity-90 transition-all shadow-md"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
