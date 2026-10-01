import React, { useState, useEffect } from 'react'
import Header from './components/Header.jsx'
import ChatInterface from './components/ChatInterface.jsx'
import KnowledgeBase from './components/KnowledgeBase.jsx'
import GuardrailInspector from './components/GuardrailInspector.jsx'
import SettingsModal from './components/SettingsModal.jsx'
import ResumeModal from './components/ResumeModal.jsx'
import { getApiUrl } from './apiConfig.js'

export default function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [stats, setStats] = useState({
    total_documents: 0,
    total_chunks: 0,
    vector_dimension: 384,
    active_llm: 'Enterprise Grounded'
  })
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [isResumeOpen, setIsResumeOpen] = useState(false)

  const fetchStats = async () => {
    try {
      const res = await fetch(getApiUrl('/api/settings/stats'))
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (err) {
      console.error('Error loading stats:', err)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
      {/* Top Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        stats={stats}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenResume={() => setIsResumeOpen(true)}
      />

      {/* Main View Area */}
      <main className="flex-1">
        {activeTab === 'chat' && (
          <ChatInterface stats={stats} onRefreshStats={fetchStats} onOpenResume={() => setIsResumeOpen(true)} />
        )}
        {activeTab === 'knowledge' && (
          <KnowledgeBase stats={stats} onRefreshStats={fetchStats} />
        )}
        {activeTab === 'guardrails' && (
          <GuardrailInspector />
        )}
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSettingsUpdated={fetchStats}
      />

      {/* Resume Modal */}
      <ResumeModal
        isOpen={isResumeOpen}
        onClose={() => setIsResumeOpen(false)}
      />
    </div>
  )
}
