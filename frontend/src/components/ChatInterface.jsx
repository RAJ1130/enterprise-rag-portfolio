import React, { useState, useRef, useEffect } from 'react'
import {
  Send, Bot, User, ShieldCheck, ShieldAlert, FileText, ChevronDown,
  ChevronRight, Sparkles, ExternalLink, RefreshCw, AlertTriangle, Layers, Clock, UserCheck
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { getApiUrl } from '../apiConfig.js'

export default function ChatInterface({ stats, onRefreshStats, onOpenResume }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: `### Welcome to Enterprise RAG & Knowledge Base
Engineered by **Mummalar Raj A** *(B.Tech AI & Data Science)*. Every response is strictly grounded in indexed enterprise documentation with source citations and anti-hallucination guardrails.

**Try asking:**
- *"What are Mummalar Raj's technical skills, education, and internship experience?"* (from Resume)
- *"What are the mandatory password hygiene rules in the IT Security manual?"* (from Security Policy PDF)
- *"What are the API Gateway rate limits for Enterprise Tier?"* (from Cloud Specs)`,
      citations: [],
      retrieved_chunks: [],
      confidence_score: 1.0,
      faithfulness_score: 1.0,
      hallucination_risk: 'LOW',
      guardrail_report: { passed: true, reason: 'System initial welcome' },
      provider_used: 'Enterprise Grounded Engine'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [samplePrompts, setSamplePrompts] = useState([])
  const [selectedCitation, setSelectedCitation] = useState(null)
  const [expandedInspectId, setExpandedInspectId] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    // Fetch sample prompts
    fetch(getApiUrl('/api/chat/sample-prompts'))
      .then(res => res.json())
      .then(data => {
        if (data.prompts) setSamplePrompts(data.prompts)
      })
      .catch(err => console.error('Error fetching sample prompts:', err))
  }, [])


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = async (queryText = null) => {
    const textToSend = queryText || input
    if (!textToSend.trim() || loading) return

    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend.trim(),
      created_at: new Date().toLocaleTimeString()
    }

    setMessages(prev => [...prev, userMsg])
    if (!queryText) setInput('')
    setLoading(true)

    try {
      const res = await fetch(getApiUrl('/api/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: textToSend.trim() })
      })

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`)
      }

      const data = await res.json()
      const aiMsg = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        citations: data.citations || [],
        retrieved_chunks: data.retrieved_chunks || [],
        confidence_score: data.confidence_score,
        faithfulness_score: data.faithfulness_score,
        hallucination_risk: data.hallucination_risk,
        guardrail_report: data.guardrail_report || {},
        provider_used: data.provider_used,
        latency_ms: data.latency_ms
      }

      setMessages(prev => [...prev, aiMsg])
    } catch (err) {
      const errorMsg = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `**Error communicating with RAG backend**: ${err.message}. Please check if the backend is running and healthy.`,
        citations: [],
        retrieved_chunks: [],
        hallucination_risk: 'HIGH'
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = () => {
    setMessages(messages.slice(0, 1))
    setSelectedCitation(null)
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] max-w-7xl mx-auto overflow-hidden">
      
      {/* Left/Main: Chat Area */}
      <div className="flex-1 flex flex-col h-full bg-slate-950/40 relative">
        
        {/* Sample Prompt Pills */}
        {samplePrompts.length > 0 && messages.length <= 2 && (
          <div className="px-6 pt-4 pb-2 border-b border-slate-800/60 bg-slate-900/30">
            <p className="text-[11px] font-semibold text-slate-400 mb-2 flex items-center space-x-1.5">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Recommended Sample Queries Grounded in Indexed Documentation:</span>
            </p>
            <div className="flex flex-wrap gap-2">
              {samplePrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(p.prompt)}
                  className="text-xs text-left px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-slate-700/60 hover:border-sky-500/50 transition-all flex items-center space-x-2"
                >
                  <span className="font-medium text-sky-400">[{p.category}]</span>
                  <span className="truncate max-w-xs">{p.prompt}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-6">
          {messages.map((m) => {
            const isUser = m.role === 'user'
            const isInspectOpen = expandedInspectId === m.id

            return (
              <div
                key={m.id}
                className={`flex space-x-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-1 shadow-md shadow-sky-500/20">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}

                <div className={`max-w-3xl flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                  
                  {/* Message Bubble */}
                  <div
                    className={`rounded-2xl px-5 py-4 text-sm leading-relaxed shadow-sm ${
                      isUser
                        ? 'bg-sky-600 text-white rounded-tr-none'
                        : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
                    }`}
                  >
                    <div className="prose prose-invert prose-sm max-w-none prose-p:my-2 prose-headings:text-slate-100 prose-headings:font-semibold prose-code:bg-slate-950 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sky-300 prose-table:border-collapse prose-th:border-b prose-th:border-slate-700 prose-th:px-3 prose-th:py-1.5 prose-td:px-3 prose-td:py-1.5 prose-td:border-b prose-td:border-slate-800">
                      <ReactMarkdown>{m.content}</ReactMarkdown>
                    </div>

                    {/* Citations Chips for AI responses */}
                    {!isUser && m.citations && m.citations.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-slate-800/80">
                        <div className="text-[11px] font-semibold text-slate-400 mb-2 flex items-center space-x-1">
                          <FileText className="w-3.5 h-3.5 text-sky-400" />
                          <span>Verified Source Citations:</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {m.citations.map((c, idx) => (
                            <button
                              key={idx}
                              onClick={() => setSelectedCitation(c)}
                              className="text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-sky-300 border border-sky-500/30 hover:border-sky-400 transition-all flex items-center space-x-1.5"
                            >
                              <span className="font-bold text-[10px] bg-sky-500/20 text-sky-400 px-1 rounded">
                                #{idx + 1}
                              </span>
                              <span className="truncate max-w-[160px]">{c.doc_name}</span>
                              <span className="text-slate-400 text-[10px]">p.{c.page_number}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Metadata & Guardrail Footer for Assistant Messages */}
                  {!isUser && m.id !== 'welcome' && (
                    <div className="mt-2 flex flex-wrap items-center gap-3 text-[11px] text-slate-400 px-1">
                      
                      {/* Confidence Badge */}
                      <span className="flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                        <ShieldCheck className="w-3 h-3 text-emerald-400" />
                        <span>Relevance: <strong className="text-slate-200">{(m.confidence_score * 100).toFixed(0)}%</strong></span>
                      </span>

                      {/* Faithfulness Badge */}
                      <span className="flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                        <span className={`w-1.5 h-1.5 rounded-full ${m.hallucination_risk === 'LOW' ? 'bg-emerald-400' : m.hallucination_risk === 'MEDIUM' ? 'bg-amber-400' : 'bg-red-400'}`} />
                        <span>Risk: <strong className={m.hallucination_risk === 'LOW' ? 'text-emerald-300' : m.hallucination_risk === 'MEDIUM' ? 'text-amber-300' : 'text-red-300'}>{m.hallucination_risk}</strong></span>
                      </span>

                      {/* Latency */}
                      {m.latency_ms && (
                        <span className="flex items-center space-x-1 text-slate-400">
                          <Clock className="w-3 h-3" />
                          <span>{m.latency_ms} ms</span>
                        </span>
                      )}

                      {/* Toggle inspect context */}
                      {m.retrieved_chunks && m.retrieved_chunks.length > 0 && (
                        <button
                          onClick={() => setExpandedInspectId(isInspectOpen ? null : m.id)}
                          className="flex items-center space-x-1 text-sky-400 hover:text-sky-300 underline font-medium"
                        >
                          <Layers className="w-3 h-3" />
                          <span>{isInspectOpen ? 'Hide Retrieved Context' : `Inspect Chunks (${m.retrieved_chunks.length})`}</span>
                        </button>
                      )}
                    </div>
                  )}

                  {/* Expandable Retrieved Chunks Inspector */}
                  {isInspectOpen && m.retrieved_chunks && (
                    <div className="mt-3 w-full bg-slate-900/90 border border-slate-800 rounded-xl p-4 text-xs space-y-3 shadow-lg">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                        <span className="font-semibold text-slate-200 flex items-center space-x-1.5">
                          <Layers className="w-4 h-4 text-sky-400" />
                          <span>Retrieved Chunks & Vector Scores Fed to Model</span>
                        </span>
                        <span className="text-[10px] text-slate-400">Hybrid Search (Dense + BM25)</span>
                      </div>
                      <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
                        {m.retrieved_chunks.map((chunk, cIdx) => (
                          <div key={cIdx} className="bg-slate-950/70 p-3 rounded-lg border border-slate-800">
                            <div className="flex items-center justify-between text-slate-400 text-[10px] mb-1.5">
                              <span className="font-mono text-sky-300 font-semibold truncate max-w-sm">
                                {chunk.doc_name} (Page {chunk.page_number}, Chunk #{chunk.chunk_index})
                              </span>
                              <div className="flex space-x-2">
                                <span>Dense: {(chunk.dense_score || 0).toFixed(2)}</span>
                                <span>BM25: {(chunk.bm25_score || 0).toFixed(2)}</span>
                                <span className="text-emerald-400 font-bold">Total: {(chunk.score || 0).toFixed(2)}</span>
                              </div>
                            </div>
                            <p className="text-slate-300 whitespace-pre-wrap font-mono text-[11px] leading-relaxed bg-slate-900/60 p-2 rounded border border-slate-800/80">
                              {chunk.content}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0 mt-1">
                    <User className="w-4 h-4 text-slate-300" />
                  </div>
                )}
              </div>
            )
          })}

          {loading && (
            <div className="flex items-start space-x-3.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-1 animate-pulse">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-none px-5 py-4 text-sm text-slate-400 flex items-center space-x-3">
                <RefreshCw className="w-4 h-4 animate-spin text-sky-400" />
                <span>Retrieving verified document chunks & applying anti-hallucination guardrails...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/70 backdrop-blur-md">
          <div className="max-w-4xl mx-auto flex items-end space-x-2">
            <div className="flex-1 bg-slate-950 border border-slate-700/80 focus-within:border-sky-500 rounded-xl px-4 py-3 transition-all shadow-inner">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask questions about company policies, API gateway specs, or incident runbooks..."
                rows={1}
                className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 resize-none focus:outline-none max-h-32"
                style={{ minHeight: '24px' }}
              />
            </div>

            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              className={`p-3 rounded-xl flex items-center justify-center transition-all ${
                input.trim() && !loading
                  ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-lg shadow-sky-600/30'
                  : 'bg-slate-800 text-slate-600 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>

            {messages.length > 1 && (
              <button
                onClick={clearChat}
                className="p-3 rounded-xl bg-slate-800/60 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-700/60 transition-all text-xs"
                title="Clear conversation"
              >
                Clear
              </button>
            )}
          </div>
          <div className="text-center mt-2">
            <span className="text-[10px] text-slate-500 flex items-center justify-center space-x-1">
              <ShieldCheck className="w-3 h-3 text-emerald-400" />
              <span>Strict Anti-Hallucination active • PII Auto-Masked • Factual Citations Enforced</span>
            </span>
          </div>
        </div>

      </div>

      {/* Right Drawer: Citation Inspector Modal / Sidebar */}
      {selectedCitation && (
        <div className="w-96 border-l border-slate-800 bg-slate-900/95 backdrop-blur-md p-5 flex flex-col h-full animate-fadeIn shadow-2xl">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-sky-400" />
              <span className="font-semibold text-sm text-white">Source Citation Detail</span>
            </div>
            <button
              onClick={() => setSelectedCitation(null)}
              className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-800 hover:bg-slate-700"
            >
              Close
            </button>
          </div>

          <div className="mt-4 flex-1 overflow-y-auto space-y-4">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Document Name</span>
              <p className="font-medium text-sm text-sky-300 mt-0.5 break-words">{selectedCitation.doc_name}</p>
            </div>

            <div className="grid grid-cols-2 gap-3 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
              <div>
                <span className="text-[10px] text-slate-400 uppercase">Page Number</span>
                <p className="font-bold text-slate-200 text-sm mt-0.5">Page {selectedCitation.page_number}</p>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase">Similarity Score</span>
                <p className="font-bold text-emerald-400 text-sm mt-0.5">{(selectedCitation.score * 100).toFixed(1)}%</p>
              </div>
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Verified Source Excerpt</span>
              <div className="mt-1.5 bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 leading-relaxed max-h-80 overflow-y-auto whitespace-pre-wrap">
                {selectedCitation.snippet}
              </div>
            </div>

            <div className="bg-sky-950/30 border border-sky-500/20 p-3 rounded-lg text-xs text-sky-200">
              <span className="font-semibold block mb-1 flex items-center space-x-1">
                <ShieldCheck className="w-3.5 h-3.5 text-sky-400" />
                <span>Audit Grounding Guarantee</span>
              </span>
              This excerpt was verified by the vector similarity index and confirmed to ground the AI's claims.
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
