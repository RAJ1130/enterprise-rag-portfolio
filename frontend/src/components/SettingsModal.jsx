import React, { useState, useEffect } from 'react'
import { Sliders, X, Check, Key, Cpu, ShieldCheck, Database } from 'lucide-react'
import { getApiUrl } from '../apiConfig.js'

export default function SettingsModal({ isOpen, onClose, onSettingsUpdated }) {
  const [settings, setSettings] = useState({
    llm_provider: 'gemini',
    gemini_api_key: '',
    gemini_model: 'gemini-2.5-flash',
    ollama_base_url: 'http://localhost:11434',
    ollama_model: 'llama3.2',
    chunk_size: 800,
    chunk_overlap: 150,
    top_k: 4,
    similarity_threshold: 0.30,
    strict_anti_hallucination: true
  })
  const [saving, setSaving] = useState(false)
  const [savedSuccess, setSavedSuccess] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetch(getApiUrl('/api/settings'))
        .then(res => res.json())
        .then(data => {
          setSettings(prev => ({
            ...prev,
            ...data,
            gemini_api_key: '' // Keep secure
          }))
        })
        .catch(err => console.error('Error fetching settings:', err))
    }
  }, [isOpen])

  if (!isOpen) return null

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload = { ...settings }
      if (!payload.gemini_api_key) delete payload.gemini_api_key // don't wipe existing key if blank

      const res = await fetch(getApiUrl('/api/settings'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },

        body: JSON.stringify(payload)
      })
      if (res.ok) {
        setSavedSuccess(true)
        onSettingsUpdated()
        setTimeout(() => {
          setSavedSuccess(false)
          onClose()
        }, 1000)
      }
    } catch (err) {
      console.error('Error saving settings:', err)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-sky-400" />
            <h3 className="font-bold text-white text-base">Enterprise RAG Configuration</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs">
          
          {/* Section: LLM Model Provider */}
          <div className="space-y-4">
            <h4 className="font-bold text-sm text-slate-200 flex items-center space-x-1.5 pb-2 border-b border-slate-800">
              <Cpu className="w-4 h-4 text-sky-400" />
              <span>Generation Model & Provider</span>
            </h4>

            <div>
              <label className="block text-slate-400 font-semibold mb-1.5">Model Provider</label>
              <select
                value={settings.llm_provider}
                onChange={(e) => setSettings({ ...settings, llm_provider: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-sky-500"
              >
                <option value="gemini">Google Gemini API (Cloud / Multimodal)</option>
                <option value="ollama">Ollama (Local Open-Weight Models: Llama 3, Mistral, Qwen)</option>
                <option value="local_simulated">Built-in Enterprise Grounded Engine (Offline / Local Air-gap)</option>
              </select>
            </div>

            {settings.llm_provider === 'gemini' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Gemini API Key</label>
                  <input
                    type="password"
                    placeholder="Enter GEMINI_API_KEY (or set via .env)"
                    value={settings.gemini_api_key}
                    onChange={(e) => setSettings({ ...settings, gemini_api_key: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Gemini Model</label>
                  <input
                    type="text"
                    value={settings.gemini_model}
                    onChange={(e) => setSettings({ ...settings, gemini_model: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
              </div>
            )}

            {settings.llm_provider === 'ollama' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Ollama Base URL</label>
                  <input
                    type="text"
                    value={settings.ollama_base_url}
                    onChange={(e) => setSettings({ ...settings, ollama_base_url: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Ollama Model</label>
                  <input
                    type="text"
                    value={settings.ollama_model}
                    onChange={(e) => setSettings({ ...settings, ollama_model: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-sky-500 font-mono"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Section: Retrieval & Vector Store Tuning */}
          <div className="space-y-4">
            <h4 className="font-bold text-sm text-slate-200 flex items-center space-x-1.5 pb-2 border-b border-slate-800">
              <Database className="w-4 h-4 text-indigo-400" />
              <span>Vector Retrieval & Chunking Parameters</span>
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-400 font-semibold">Similarity Threshold</span>
                  <span className="font-mono text-sky-400 font-bold">{settings.similarity_threshold}</span>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.70"
                  step="0.05"
                  value={settings.similarity_threshold}
                  onChange={(e) => setSettings({ ...settings, similarity_threshold: parseFloat(e.target.value) })}
                  className="w-full accent-sky-500"
                />
                <span className="text-[10px] text-slate-500">
                  Minimum similarity required to pass anti-hallucination gate.
                </span>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-400 font-semibold">Top-K Chunks Retrieved</span>
                  <span className="font-mono text-sky-400 font-bold">{settings.top_k}</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={settings.top_k}
                  onChange={(e) => setSettings({ ...settings, top_k: parseInt(e.target.value) })}
                  className="w-full accent-sky-500"
                />
                <span className="text-[10px] text-slate-500">
                  Number of most relevant context chunks fed to LLM.
                </span>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Chunk Size (characters)</label>
                <input
                  type="number"
                  value={settings.chunk_size}
                  onChange={(e) => setSettings({ ...settings, chunk_size: parseInt(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Chunk Overlap (characters)</label>
                <input
                  type="number"
                  value={settings.chunk_overlap}
                  onChange={(e) => setSettings({ ...settings, chunk_overlap: parseInt(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
                />
              </div>
            </div>
          </div>

          {/* Section: Guardrails Compliance */}
          <div className="space-y-4">
            <h4 className="font-bold text-sm text-slate-200 flex items-center space-x-1.5 pb-2 border-b border-slate-800">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Anti-Hallucination & Security Policies</span>
            </h4>

            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-3">
              <label className="flex items-center justify-between cursor-pointer">
                <div>
                  <span className="font-semibold text-slate-200">Strict Anti-Hallucination Gate</span>
                  <p className="text-[11px] text-slate-400">Refuses generation if retrieved context is below threshold.</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.strict_anti_hallucination}
                  onChange={(e) => setSettings({ ...settings, strict_anti_hallucination: e.target.checked })}
                  className="w-4 h-4 accent-sky-500 rounded"
                />
              </label>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
          <span className="text-xs text-slate-500">Changes apply immediately to backend session.</span>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 text-xs font-semibold"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-5 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-md shadow-sky-600/30"
            >
              {savedSuccess ? (
                <>
                  <Check className="w-4 h-4 text-emerald-300" />
                  <span>Saved!</span>
                </>
              ) : (
                <span>Save Configuration</span>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}
