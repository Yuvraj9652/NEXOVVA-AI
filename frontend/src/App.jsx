import React, { useEffect } from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import useAuthStore from "./store/authStore"

// Layouts
import Sidebar from "./components/layout/Sidebar"

// Pages
import Home from "./pages/Home"
import Login from "./pages/Login"
import Register from "./pages/Register"
import OTPVerify from "./pages/OTPVerify"
import OAuthCallback from "./pages/OAuthCallback"
import Dashboard from "./pages/Dashboard"
import CRM from "./pages/CRM"
import AIChat from "./pages/AIChat"
import ReportsAnalytics from "./pages/ReportsAnalytics"
import CompanyWorkspace from "./pages/CompanyWorkspace"
import ProjectHub from "./pages/ProjectHub"
import ProjectKnowledgeBase from "./pages/ProjectKnowledgeBase"
import SmartProjectBroadcasting from "./pages/SmartProjectBroadcasting"
import AICustomerMatching from "./pages/AICustomerMatching"
import ProjectAnalytics from "./pages/ProjectAnalytics"
import ProjectDocumentManager from "./pages/ProjectDocumentManager"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function AppContent() {
  const { isAuthenticated, initialize, isLoading } = useAuthStore()

  useEffect(() => {
    initialize()
  }, [initialize])

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background text-foreground">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-sm font-medium tracking-wide text-muted-foreground">
            Initializing NEXOVA AI...
          </p>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-otp" element={<OTPVerify />} />
        <Route path="/oauth-callback" element={<OAuthCallback />} />

        {/* Protected Dashboard Layout */}
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground gradient-bg">
                <Sidebar />
                <main className="flex-1 overflow-y-auto px-6 py-6 lg:px-10">
                  <Routes>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/crm" element={<CRM />} />
                    <Route path="/reports-analytics" element={<ReportsAnalytics />} />
                    <Route path="/company-workspace" element={<CompanyWorkspace />} />
                    <Route path="/company-workspace/project-hub" element={<ProjectHub />} />
                    <Route path="/company-workspace/project-hub/knowledge-base" element={<ProjectKnowledgeBase />} />
                    <Route path="/company-workspace/project-hub/broadcasting" element={<SmartProjectBroadcasting />} />
                    <Route path="/company-workspace/project-hub/ai-matching" element={<AICustomerMatching />} />
                    <Route path="/company-workspace/project-hub/analytics" element={<ProjectAnalytics />} />
                    <Route path="/company-workspace/project-hub/documents" element={<ProjectDocumentManager />} />
                    <Route path="/ai-chat" element={<AIChat />} />
                    <Route path="*" element={<Navigate to="/dashboard" />} />
                  </Routes>
                </main>
              </div>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
      </Routes>
    </Router>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  )
}
