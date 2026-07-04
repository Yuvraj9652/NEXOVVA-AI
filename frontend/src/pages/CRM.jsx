import React, { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  Plus,
  Search,
  Filter,
  User,
  Building,
  Briefcase,
  DollarSign,
  ArrowRight,
  Trash,
  MoveRight,
  LayoutGrid,
  Kanban,
  Notebook,
} from "lucide-react"
import api from "../api/client"

export default function CRM() {
  const [activeTab, setActiveTab] = useState("board") // 'board' or 'contacts'
  const [showContactModal, setShowContactModal] = useState(false)
  const [showDealModal, setShowDealModal] = useState(false)
  
  // Form states
  const [contactForm, setContactForm] = useState({ first_name: "", last_name: "", email: "", phone: "" })
  const [dealForm, setDealForm] = useState({ title: "", amount: "", stage: "", contact: "" })

  const queryClient = useQueryClient()

  // Queries
  const { data: contacts, isLoading: loadingContacts } = useQuery({
    queryKey: ["contacts"],
    queryFn: () => api.get("/api/contacts/").then((res) => res.data.results || []),
  })

  const { data: stages, isLoading: loadingStages } = useQuery({
    queryKey: ["stages"],
    queryFn: () => api.get("/api/pipeline/stages/").then((res) => res.data.results || []),
  })

  const { data: deals, isLoading: loadingDeals } = useQuery({
    queryKey: ["deals"],
    queryFn: () => api.get("/api/pipeline/deals/").then((res) => res.data.results || []),
  })

  // Mutations
  const contactMutation = useMutation({
    mutationFn: (newContact) => api.post("/api/contacts/", newContact),
    onSuccess: () => {
      queryClient.invalidateQueries(["contacts"])
      setShowContactModal(false)
      setContactForm({ first_name: "", last_name: "", email: "", phone: "" })
    },
  })

  const dealMutation = useMutation({
    mutationFn: (newDeal) => api.post("/api/pipeline/deals/", newDeal),
    onSuccess: () => {
      queryClient.invalidateQueries(["deals"])
      setShowDealModal(false)
      setDealForm({ title: "", amount: "", stage: "", contact: "" })
    },
  })

  const deleteDealMutation = useMutation({
    mutationFn: (dealId) => api.delete(`/api/pipeline/deals/${dealId}/`),
    onSuccess: () => {
      queryClient.invalidateQueries(["deals"])
    },
  })

  const updateDealStageMutation = useMutation({
    mutationFn: ({ dealId, stageId }) =>
      api.patch(`/api/pipeline/deals/${dealId}/`, { stage: stageId }),
    onSuccess: () => {
      queryClient.invalidateQueries(["deals"])
    },
  })

  const handleContactSubmit = (e) => {
    e.preventDefault()
    contactMutation.mutate(contactForm)
  }

  const handleDealSubmit = (e) => {
    e.preventDefault()
    dealMutation.mutate({
      title: dealForm.title,
      amount: parseFloat(dealForm.amount),
      stage: parseInt(dealForm.stage),
      contact: dealForm.contact ? parseInt(dealForm.contact) : null,
    })
  }

  // Pre-seed default stages if none exist
  const seedStagesMutation = useMutation({
    mutationFn: async () => {
      const defaultStages = ["New", "Contacted", "Proposal", "Negotiation", "Closed Won"]
      for (let i = 0; i < defaultStages.length; i++) {
        await api.post("/api/pipeline/stages/", { name: defaultStages[i], order: i })
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(["stages"])
    },
  })

  const handleSeedStages = () => {
    seedStagesMutation.mutate()
  }

  return (
    <div className="space-y-6 pb-12">
      {/* CRM Actions Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            Sales CRM
          </h1>
          <p className="text-muted-foreground text-sm">
            Manage contacts, log interactions, and track deal pipelines.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => setShowContactModal(true)}
            className="flex items-center gap-2 rounded-lg bg-card border border-border px-4 py-2 text-sm font-semibold hover:bg-muted"
          >
            <Plus className="h-4 w-4" /> Contact
          </button>
          <button
            onClick={() => setShowDealModal(true)}
            disabled={!stages || stages.length === 0}
            className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/95 disabled:opacity-50"
          >
            <Plus className="h-4 w-4" /> Deal
          </button>
        </div>
      </div>

      {/* Tabs Switcher */}
      <div className="flex border-b border-border">
        <button
          onClick={() => setActiveTab("board")}
          className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-all ${
            activeTab === "board"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Kanban className="h-4 w-4" /> Kanban Board
        </button>
        <button
          onClick={() => setActiveTab("contacts")}
          className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-all ${
            activeTab === "contacts"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <LayoutGrid className="h-4 w-4" /> Contacts Directory
        </button>
      </div>

      {/* Tab: Kanban Board */}
      {activeTab === "board" && (
        <div className="space-y-4">
          {(!stages || stages.length === 0) && (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-card p-12 text-center">
              <Notebook className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-base font-bold text-foreground">No Pipeline Stages Found</h3>
              <p className="text-sm text-muted-foreground mt-1 mb-6">
                Get started by seeding default stages for your sales pipeline.
              </p>
              <button
                onClick={handleSeedStages}
                disabled={seedStagesMutation.isPending}
                className="rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground"
              >
                {seedStagesMutation.isPending ? "Generating..." : "Seed Default Pipeline Stages"}
              </button>
            </div>
          )}

          {stages && stages.length > 0 && (
            <div className="flex gap-4 overflow-x-auto pb-4">
              {stages.map((stage) => {
                const stageDeals = deals?.filter((d) => d.stage === stage.id) || []
                const stageTotal = stageDeals.reduce((sum, d) => sum + parseFloat(d.amount), 0)

                return (
                  <div key={stage.id} className="w-80 shrink-0 flex flex-col rounded-xl bg-card border border-border p-4">
                    {/* Stage Header */}
                    <div className="mb-4 flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-bold text-foreground">{stage.name}</h3>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          ${stageTotal.toLocaleString(undefined, { minimumFractionDigits: 0 })}
                        </p>
                      </div>
                      <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-semibold text-muted-foreground">
                        {stageDeals.length}
                      </span>
                    </div>

                    {/* Stage Cards */}
                    <div className="flex-1 space-y-3 min-h-[300px] overflow-y-auto">
                      {stageDeals.map((deal) => (
                        <div
                          key={deal.id}
                          className="group relative rounded-lg border border-border bg-muted/40 p-4 hover:border-primary/50 transition-all duration-200"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <h4 className="text-xs font-bold text-foreground leading-tight">
                              {deal.title}
                            </h4>
                            <button
                              onClick={() => deleteDealMutation.mutate(deal.id)}
                              className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive transition-all"
                            >
                              <Trash className="h-3.5 w-3.5" />
                            </button>
                          </div>

                          <div className="mt-2 flex items-center gap-1.5 text-xs font-extrabold text-foreground">
                            <DollarSign className="h-3.5 w-3.5 text-emerald-500" />
                            {parseFloat(deal.amount).toLocaleString()}
                          </div>

                          {deal.contact_details && (
                            <div className="mt-3 flex items-center gap-1.5 text-[10px] text-muted-foreground border-t border-border/50 pt-2">
                              <User className="h-3 w-3" />
                              <span className="truncate">
                                {deal.contact_details.first_name} {deal.contact_details.last_name}
                              </span>
                            </div>
                          )}

                          {/* Quick stage transition button */}
                          <div className="mt-3 flex justify-end gap-1.5">
                            {stages
                              .filter((s) => s.id !== stage.id)
                              .map((nextStage) => (
                                <button
                                  key={nextStage.id}
                                  onClick={() =>
                                    updateDealStageMutation.mutate({
                                      dealId: deal.id,
                                      stageId: nextStage.id,
                                    })
                                  }
                                  title={`Move to ${nextStage.name}`}
                                  className="flex h-5 w-5 items-center justify-center rounded bg-muted hover:bg-primary hover:text-primary-foreground text-[10px] transition-all"
                                >
                                  {nextStage.name.substring(0, 1)}
                                </button>
                              ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Tab: Contacts Directory */}
      {activeTab === "contacts" && (
        <div className="rounded-xl border border-border bg-card overflow-hidden shadow-premium">
          <div className="flex items-center justify-between border-b border-border bg-muted/20 px-6 py-4">
            <div className="relative w-80">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-muted-foreground">
                <Search className="h-4 w-4" />
              </span>
              <input
                type="text"
                placeholder="Search contacts..."
                className="block w-full rounded-lg border border-border bg-background py-1.5 pl-10 pr-4 text-xs placeholder-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <button className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-semibold bg-background hover:bg-muted">
              <Filter className="h-3.5 w-3.5" /> Filters
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-sm">
              <thead className="bg-muted/40 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4">Name</th>
                  <th className="px-6 py-4">Email</th>
                  <th className="px-6 py-4">Phone</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Created At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {contacts && contacts.length > 0 ? (
                  contacts.map((contact) => (
                    <tr key={contact.id} className="hover:bg-muted/20">
                      <td className="px-6 py-4 font-medium text-foreground flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary text-xs font-bold">
                          {contact.first_name[0]}
                          {contact.last_name[0]}
                        </div>
                        {contact.first_name} {contact.last_name}
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">{contact.email}</td>
                      <td className="px-6 py-4 text-muted-foreground">{contact.phone || "-"}</td>
                      <td className="px-6 py-4">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                            contact.status === "ACTIVE"
                              ? "bg-emerald-500/10 text-emerald-500"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {contact.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">
                        {new Date(contact.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="px-6 py-12 text-center text-xs text-muted-foreground">
                      No contacts registered. Create your first contact to start profiling.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modal: Create Contact */}
      {showContactModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-premium relative">
            <h3 className="text-lg font-bold text-foreground mb-4">New Contact Card</h3>
            <form onSubmit={handleContactSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1">First Name</label>
                  <input
                    type="text"
                    required
                    value={contactForm.first_name}
                    onChange={(e) => setContactForm({ ...contactForm, first_name: e.target.value })}
                    className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1">Last Name</label>
                  <input
                    type="text"
                    required
                    value={contactForm.last_name}
                    onChange={(e) => setContactForm({ ...contactForm, last_name: e.target.value })}
                    className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-muted-foreground mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={contactForm.email}
                  onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                  className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-muted-foreground mb-1">Phone Number</label>
                <input
                  type="text"
                  value={contactForm.phone}
                  onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
                  className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              <div className="flex justify-end gap-3 mt-6 border-t border-border pt-4">
                <button
                  type="button"
                  onClick={() => setShowContactModal(false)}
                  className="rounded-lg border border-border bg-background px-4 py-2 text-sm font-semibold hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={contactMutation.isPending}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/95"
                >
                  {contactMutation.isPending ? "Creating..." : "Save Contact"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Create Deal */}
      {showDealModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-premium relative">
            <h3 className="text-lg font-bold text-foreground mb-4">New Deal Card</h3>
            <form onSubmit={handleDealSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-muted-foreground mb-1">Deal Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 52 Oakwood Ave Purchase"
                  value={dealForm.title}
                  onChange={(e) => setDealForm({ ...dealForm, title: e.target.value })}
                  className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-muted-foreground mb-1">Deal Amount (USD)</label>
                <input
                  type="number"
                  required
                  placeholder="500000"
                  value={dealForm.amount}
                  onChange={(e) => setDealForm({ ...dealForm, amount: e.target.value })}
                  className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1">Initial Stage</label>
                  <select
                    required
                    value={dealForm.stage}
                    onChange={(e) => setDealForm({ ...dealForm, stage: e.target.value })}
                    className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary text-foreground"
                  >
                    <option value="">Select Stage</option>
                    {stages?.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1">Link Contact</label>
                  <select
                    value={dealForm.contact}
                    onChange={(e) => setDealForm({ ...dealForm, contact: e.target.value })}
                    className="block w-full rounded-lg border border-border bg-muted/40 py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary text-foreground"
                  >
                    <option value="">No Contact</option>
                    {contacts?.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.first_name} {c.last_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6 border-t border-border pt-4">
                <button
                  type="button"
                  onClick={() => setShowDealModal(false)}
                  className="rounded-lg border border-border bg-background px-4 py-2 text-sm font-semibold hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={dealMutation.isPending}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/95"
                >
                  {dealMutation.isPending ? "Creating..." : "Save Deal"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
