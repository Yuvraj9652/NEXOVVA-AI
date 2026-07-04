import React, { useEffect, useRef, useState } from "react"
import { Link } from "react-router-dom"
import { Sparkles, ArrowRight, Building2, Users, Rocket, Shield, BarChart3, Globe, Play, CheckCircle, Clock, AlertCircle, MessageSquare, Calendar, Phone, Target, Zap, TrendingUp, UserCheck } from "lucide-react"

const features = [
  {
    title: "AI Lead Management",
    desc: "Capture, score, and nurture leads with intelligent automation tailored for real estate.",
    icon: Users,
  },
  {
    title: "Company Workspace",
    desc: "Centralized project hub with knowledge base, broadcasting, and document management.",
    icon: Building2,
  },
  {
    title: "Smart Analytics",
    desc: "Real-time dashboards and AI-generated reports to accelerate decision-making.",
    icon: BarChart3,
  },
  {
    title: "AI Broadcasting",
    desc: "Multi-channel project announcements powered by natural language generation.",
    icon: Rocket,
  },
  {
    title: "Customer Matching",
    desc: "Match leads to the right projects using behavioral predictions and profiling.",
    icon: Shield,
  },
  {
    title: "Global Scale",
    desc: "Built for agencies, developers, and brokers operating across markets.",
    icon: Globe,
  },
]

const problemSolutions = [
  {
    id: "leads",
    problem: "Missed Leads & Slow Response",
    solution: "AI captures every inquiry instantly, responds within seconds",
    problemIcon: AlertCircle,
    solutionIcon: CheckCircle,
    stat: "73% call your competition when you don't answer fast",
  },
  {
    id: "followup",
    problem: "Manual Follow-ups Waste Time",
    solution: "Automated nurturing that converts leads while you focus on sales",
    problemIcon: Clock,
    solutionIcon: Calendar,
    stat: "Avg agent spends 2.5 hrs daily on follow-up calls",
  },
  {
    id: "qualification",
    problem: "No Lead Qualification",
    solution: "AI scores buyers instantly so your team only talks to hot leads",
    problemIcon: Users,
    solutionIcon: Shield,
    stat: "60% of your calls go to unqualified prospects",
  },
  {
    id: "revenue",
    problem: "Lost Revenue in Database",
    solution: "AI unlocks hidden sales from dormant leads",
    problemIcon: Building2,
    solutionIcon: Rocket,
    stat: "Your CRM has $3.2M in untapped opportunities",
  },
]

const chatScreens = [
  {
    id: "calling",
    icon: Phone,
    title: "AI Calling",
    chat: [
      { type: "ai", text: "Hello! This is NEXOVA AI calling about Skyline Heights. Interested in a property tour today?" },
      { type: "user", text: "Yes, I'd like to schedule a visit this weekend." },
      { type: "ai", text: "Perfect! I've booked you for Saturday 10 AM. Our agent will contact you shortly." },
    ],
  },
  {
    id: "whatsapp",
    icon: MessageSquare,
    title: "WhatsApp",
    chat: [
      { type: "ai", text: "Hi there! 👋 I saw you inquired about our properties." },
      { type: "user", text: "Looking for a 2BHK apartment under ₹1.5 Cr" },
      { type: "ai", text: "Great match! Check out Skyline Heights - exactly fits your budget. Shall I send details?" },
    ],
  },
  {
    id: "scheduling",
    icon: Calendar,
    title: "Smart Scheduling",
    chat: [
      { type: "ai", text: "Your calendar has 3 new appointment requests for tomorrow." },
      { type: "user", text: "Slot them for afternoon" },
      { type: "ai", text: "Done! Site visits scheduled for 2 PM, 3 PM, and 4 PM. All confirmed." },
    ],
  },
  {
    id: "availability",
    icon: Clock,
    title: "24/7 Availability",
    chat: [
      { type: "ai", text: "Late night inquiry received from a premium lead!" },
      { type: "ai", text: "I've captured their contact & requirements. They'll get a call first thing in the morning." },
      { type: "ai", text: "Lead saved from going cold. Your team will appreciate this tomorrow! 😊" },
    ],
  },
]

export default function Home() {
  const heroRef = useRef(null)
  const [activeScreen, setActiveScreen] = useState(0)

  useEffect(() => {
    const boxElements = document.querySelectorAll(".feature-box, .problem-solution-table")
    
    const handleMouseMove = (e) => {
      const element = e.target.closest(".feature-box") || e.target.closest(".problem-solution-table")
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
      const element = e.target.closest(".feature-box") || e.target.closest(".problem-solution-table")
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

  const currentChat = chatScreens[activeScreen]

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground">
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

      {/* Navigation */}
      <nav className="relative z-20 flex items-center justify-between px-6 py-5 lg:px-12">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500 to-amber-500 text-white shadow-premium">
            <Sparkles className="h-5 w-5" />
          </div>
          <span className="font-bold text-xl tracking-tight">
            NEXOVA <span className="text-teal-500">AI</span>
          </span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="rounded-lg border border-border bg-card/80 px-4 py-2 text-sm font-semibold hover:bg-muted transition-all backdrop-blur-md"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="rounded-lg bg-gradient-to-r from-teal-500 to-amber-500 px-4 py-2 text-sm font-semibold text-white shadow-premium hover:opacity-90 transition-all"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section ref={heroRef} className="relative z-10 mx-auto max-w-7xl px-6 pt-20 pb-32 lg:px-12">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          {/* Left Content */}
          <div className="flex-1 text-center lg:text-left">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card/80 px-4 py-1.5 text-xs font-semibold backdrop-blur-md animate-fade-in">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-teal-500 opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-teal-500"></span>
              </span>
              AI-Powered Real Estate Solution
            </div>

            <h1 className="max-w-4xl text-5xl font-extrabold tracking-tight lg:text-7xl leading-tight">
              <span className="block animate-slide-up">Your AI Employee</span>
              <span className="block bg-gradient-to-r from-teal-500 via-amber-500 to-emerald-500 bg-clip-text text-transparent animate-slide-up" style={{ animationDelay: "0.1s" }}>
                Closes Deals 24/7
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed animate-slide-up" style={{ animationDelay: "0.2s" }}>
              Never lose a lead again. Our AI responds instantly, qualifies buyers, and books appointments while you sleep.
            </p>

            <div className="mt-10 flex flex-wrap items-center justify-center lg:justify-start gap-4 animate-slide-up" style={{ animationDelay: "0.3s" }}>
              <Link
                to="/register"
                className="group relative inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-8 py-3.5 text-sm font-bold text-white shadow-premium transition-all hover:shadow-premiumDark hover:scale-105 transform-gpu"
              >
                Watch Demo - See How It Works
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
            </div>

            {/* Clickable Feature badges */}
            <div className="mt-10 flex flex-wrap items-center justify-center lg:justify-start gap-3 animate-slide-up" style={{ animationDelay: "0.4s" }}>
              {chatScreens.map((screen, i) => {
                const Icon = screen.icon
                const isActive = activeScreen === i
                return (
                  <button
                    key={i}
                    onClick={() => setActiveScreen(i)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-all text-sm font-semibold backdrop-blur-md transform-gpu
                      ${isActive 
                        ? 'border-teal-500 bg-teal-500/10 text-teal-500 scale-105 shadow-lg' 
                        : 'border-border bg-card/60 text-muted-foreground hover:bg-muted hover:scale-105'
                      }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{screen.title}</span>
                  </button>
                )
              })}
            </div>

            {/* Stats */}
            <div className="mt-12 grid grid-cols-3 gap-6 animate-slide-up" style={{ animationDelay: "0.5s" }}>
              {[
                { value: "8,200+", label: "Leads Converted" },
                { value: "95%", label: "Response Rate" },
                { value: "$2.1M+", label: "Revenue Generated" },
              ].map((stat, i) => (
                <div key={i} className="text-center lg:text-left">
                  <p className="text-2xl font-extrabold bg-gradient-to-r from-teal-500 to-amber-500 bg-clip-text text-transparent">
                    {stat.value}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right - Interactive Chat Demo */}
          <div className="flex-1 relative max-w-lg w-full">
            <div className="relative mx-auto max-w-md">
              <div className="rounded-3xl border border-border bg-card/90 p-6 shadow-2xl backdrop-blur-xl overflow-hidden transform-gpu">
                <div className="flex items-center gap-3 mb-4 pb-3 border-b border-border">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-r from-teal-500 to-amber-600 text-white shadow-premium">
                    <Sparkles className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-foreground">AI Assistant</p>
                    <p className="text-xs text-muted-foreground">Online • Ready to help</p>
                  </div>
                </div>

                <div className="space-y-3 min-h-[200px]">
                  {currentChat.chat.map((msg, idx) => (
                    <div
                      key={idx}
                      className="animate-fade-in"
                      style={{ animationDelay: `${idx * 0.1}s` }}
                    >
                      <div className={`rounded-2xl px-4 py-3 max-w-[80%] ${msg.type === 'ai' 
                        ? 'rounded-tl-none bg-muted/80 mr-auto' 
                        : 'rounded-tr-none bg-gradient-to-r from-teal-500 to-amber-600 ml-auto'}`}>
                        <p className={`text-sm ${msg.type === 'ai' ? 'text-foreground' : 'text-white'}`}>
                          {msg.text}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="absolute -inset-4 rounded-3xl border-2 border-teal-500/30 animate-pulse-ring pointer-events-none"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 mx-auto max-w-7xl px-6 pb-24 lg:px-12">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-extrabold tracking-tight lg:text-4xl animate-fade-in">
            <span className="bg-gradient-to-r from-teal-500 to-emerald-500 bg-clip-text text-transparent">Why Top Developers Choose Us</span>
          </h2>
          <p className="mt-3 text-muted-foreground animate-fade-in" style={{ animationDelay: "0.1s" }}>
            Transform your business with AI that sells 24/7
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, idx) => {
            const Icon = feature.icon
            return (
              <div
                key={idx}
                className="feature-box group relative rounded-2xl border border-border bg-card/60 p-6 backdrop-blur-md transition-all duration-300 hover:-translate-y-2 hover:shadow-premiumDark animate-fade-in overflow-hidden"
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-teal-500/0 via-teal-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                <div className="relative z-10">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-500/10 text-teal-500 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="mt-4 text-base font-bold text-foreground">{feature.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{feature.desc}</p>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* Problem-Solution Comparison - Responsive Side-by-Side */}
      <section className="relative z-10 mx-auto max-w-7xl px-6 pb-24 lg:px-12">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-extrabold tracking-tight lg:text-4xl">
            <span className="bg-gradient-to-r from-red-500 to-rose-600 bg-clip-text text-transparent">Real Estate Challenges</span>
          </h2>
        </div>

        <div className="relative rounded-3xl border border-border bg-card/60 backdrop-blur-xl problem-solution-table shadow-2xl overflow-hidden">
          {problemSolutions.map((item, idx) => {
            const ProblemIcon = item.problemIcon
            const SolutionIcon = item.solutionIcon
            return (
              <div key={idx} className={`border-b border-border/50 last:border-0 ${idx % 2 === 0 ? 'bg-muted/[0.02]' : ''}`}>
                {/* Desktop: Side by side, Mobile: Stacked */}
                <div className="grid grid-cols-1 lg:grid-cols-2">
                  {/* Problem - Left on desktop */}
                  <div className="flex items-start gap-4 p-6 lg:p-8 border-r-0 lg:border-r border-border/30">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/10 text-red-500 flex-shrink-0 shadow-lg">
                      <ProblemIcon className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-lg font-bold text-red-500 mb-2">{item.problem}</p>
                      <p className="text-sm text-muted-foreground bg-red-500/5 px-4 py-2 rounded-lg inline-block border border-red-500/10">
                        {item.stat}
                      </p>
                    </div>
                  </div>
                  
                  {/* Solution - Right on desktop */}
                  <div className="flex items-start gap-4 p-6 lg:p-8 bg-teal-500/5 dark:bg-teal-500/10 lg:bg-transparent lg:dark:bg-transparent">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-500/10 text-teal-500 flex-shrink-0 shadow-lg">
                      <SolutionIcon className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="text-lg font-bold text-teal-500 mb-2">{item.solution}</p>
                      <Link
                        to="/register"
                        className="inline-flex items-center gap-1 text-sm font-semibold text-teal-500 hover:underline"
                      >
                        See how we fix this <ArrowRight className="h-3 w-3" />
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* Showcase Section */}
      <section className="relative z-10 mx-auto max-w-7xl px-6 pb-24 lg:px-12">
        <div className="relative rounded-3xl border border-border bg-card/40 overflow-hidden backdrop-blur-md shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-r from-teal-500/10 via-amber-500/5 to-emerald-500/10" />

          <div className="relative z-10 p-6 lg:p-12">
            <div className="flex flex-col lg:flex-row items-center gap-6">
              <div className="flex-1 space-y-4">
                <h3 className="text-2xl font-extrabold">
                  <span className="text-teal-500">Turn Interest Into</span> Booked Appointments
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  Our AI captures, qualifies, and schedules every interested prospect automatically. No missed opportunities, no manual work.
                </p>
                <ul className="space-y-3">
                  {[
                    "Automated lead capture from all channels",
                    "Instant qualification & scoring",
                    "Smart appointment scheduling",
                    "Automated follow-up sequences",
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-3 text-sm">
                      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-teal-500/10 text-teal-500">
                        <CheckCircle className="h-4 w-4" />
                      </div>
                      <span className="text-muted-foreground font-medium">{item}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-amber-600 px-6 py-3 text-sm font-bold text-white shadow-premium hover:shadow-premiumDark transition-all mt-4"
                >
                  Watch Demo <Play className="h-4 w-4" />
                </Link>
              </div>

              <div className="flex-1 w-full">
                <div className="relative rounded-2xl overflow-hidden shadow-2xl transform-gpu aspect-video bg-gradient-to-br from-teal-500/20 to-amber-500/20">
                  <video
                    className="w-full h-full object-cover"
                    autoPlay
                    muted
                    loop
                    playsInline
                    preload="metadata"
                  >
                    <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" type="video/mp4" />
                    <img
                      src="https://images.unsplash.com/photo-1560518883-ceecd441d930?w=800&h=450&fit=crop"
                      alt="Real Estate Demo"
                      className="w-full h-full object-cover"
                    />
                  </video>
                  <div className="absolute inset-0 bg-gradient-to-t from-background/60 to-transparent" />
                  <div className="absolute bottom-4 left-4 right-4 text-center">
                    <p className="text-white font-bold text-sm bg-black/30 px-3 py-1 rounded-full inline-block backdrop-blur-sm">
                      Demo Video - AI in Action
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border bg-card/40 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 py-8 lg:flex-row lg:px-12">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-teal-500" />
            <span className="text-sm font-bold">NEXOVA AI</span>
          </div>
          <p className="text-xs text-muted-foreground">
            AI employees for the future of real estate.
          </p>
        </div>
      </footer>
    </div>
  )
}