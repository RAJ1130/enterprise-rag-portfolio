import React from 'react'
import { ShieldCheck, Database, MessageSquare, Sliders, ShieldAlert, Cpu, UserCheck } from 'lucide-react'

export default function Header({ activeTab, setActiveTab, stats, onOpenSettings, onOpenResume }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Left: Branding & Author Tag */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20 border border-sky-400/30">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-base sm:text-lg text-white tracking-tight">Enterprise RAG</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20">
                v1.0 Factual
              </span>
            </div>
            <p className="text-[11px] text-slate-400 truncate">
              By <strong className="text-slate-200">Mummalar Raj A</strong> • B.Tech AI & Data Science
            </p>
          </div>
        </div>

        {/* Center: Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'chat'
                ? 'bg-sky-600 text-white shadow-md shadow-sky-600/25'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>AI Assistant</span>
          </button>

          <button
            onClick={() => setActiveTab('knowledge')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'knowledge'
                ? 'bg-sky-600 text-white shadow-md shadow-sky-600/25'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>Knowledge Base</span>
            {stats && stats.total_documents > 0 && (
              <span className="ml-1 px-1.5 py-0.2 bg-slate-800 text-sky-300 rounded text-[10px]">
                {stats.total_documents}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('guardrails')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'guardrails'
                ? 'bg-sky-600 text-white shadow-md shadow-sky-600/25'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" />
            <span>Guardrail Lab</span>
          </button>
        </nav>

        {/* Right: Resume Button, Status & Settings */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          
          {/* Resume & Portfolio Button */}
          <button
            onClick={onOpenResume}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold transition-all shadow-sm"
            title="View Mummalar Raj Resume & Profile"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Resume / Profile</span>
          </button>

          <button
            onClick={onOpenSettings}
            className="p-2 rounded-lg text-slate-400 hover:text-white bg-slate-800/50 hover:bg-slate-700/60 border border-slate-700/50 transition-all"
            title="Configure System Settings"
          >
            <Sliders className="w-4 h-4" />
          </button>
        </div>

      </div>
    </header>
  )
}
