import React, { useState, useEffect, useRef } from 'react'
import {
  Upload, FileText, Trash2, Eye, RefreshCw, Plus, CheckCircle2,
  AlertCircle, Layers, File, Database, DownloadCloud, Sparkles
} from 'lucide-react'
import { getApiUrl } from '../apiConfig.js'

export default function KnowledgeBase({ stats, onRefreshStats }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [selectedDocChunks, setSelectedDocChunks] = useState(null)
  const [loadingChunks, setLoadingChunks] = useState(false)
  const [chunkModalOpen, setChunkModalOpen] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [actionNotice, setActionNotice] = useState(null)
  const fileInputRef = useRef(null)

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      const res = await fetch(getApiUrl('/api/documents'))
      const data = await res.json()
      setDocuments(data.documents || [])
    } catch (err) {

      console.error('Error fetching documents:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return
    setUploading(true)
    setActionNotice({ type: 'info', text: 'Extracting text, formatting tables, and generating vector embeddings...' })

    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }

    try {
      const res = await fetch(getApiUrl('/api/documents/upload'), {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      if (res.ok) {
        setActionNotice({ type: 'success', text: `Successfully indexed ${data.uploaded.length} document(s)!` })
        fetchDocuments()
        onRefreshStats()
      } else {
        setActionNotice({ type: 'error', text: data.detail || 'Upload failed' })
      }
    } catch (err) {
      setActionNotice({ type: 'error', text: `Upload error: ${err.message}` })
    } finally {
      setUploading(false)
      setTimeout(() => setActionNotice(null), 5000)
    }
  }

  const handleLoadSamples = async () => {
    setLoading(true)
    setActionNotice({ type: 'info', text: 'Loading enterprise sample documents (PDF, Markdown Specs, Runbooks)...' })
    try {
      const res = await fetch(getApiUrl('/api/documents/load-sample'), { method: 'POST' })
      const data = await res.json()
      if (res.ok) {
        setActionNotice({ type: 'success', text: `Loaded ${data.loaded_samples?.length || 0} sample enterprise documents!` })
        fetchDocuments()
        onRefreshStats()
      }
    } catch (err) {
      setActionNotice({ type: 'error', text: `Failed to load samples: ${err.message}` })
    } finally {
      setLoading(false)
      setTimeout(() => setActionNotice(null), 5000)
    }
  }

  const handleDelete = async (docId, docName) => {
    if (!confirm(`Are you sure you want to delete '${docName}' from the knowledge base?`)) return

    try {
      const res = await fetch(getApiUrl(`/api/documents/${docId}`), { method: 'DELETE' })
      if (res.ok) {
        fetchDocuments()
        onRefreshStats()
      }
    } catch (err) {
      console.error('Error deleting document:', err)
    }
  }

  const handleViewChunks = async (docId, docName) => {
    setLoadingChunks(true)
    setChunkModalOpen(true)
    try {
      const res = await fetch(getApiUrl(`/api/documents/${docId}/chunks`))
      const data = await res.json()
      setSelectedDocChunks({ docName, chunks: data.chunks || [] })
    } catch (err) {

      console.error('Error fetching chunks:', err)
    } finally {
      setLoadingChunks(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const formatDate = (timestamp) => {
    if (!timestamp) return '-'
    return new Date(timestamp * 1000).toLocaleDateString(undefined, {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Banner / Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Database className="w-5 h-5 text-sky-400" />
            <span>Enterprise Knowledge Base Ingestion</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Upload multi-format internal files (PDF, DOCX, CSV, Markdown, TXT) for recursive semantic chunking and vector indexing.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleLoadSamples}
            disabled={loading || uploading}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-300 hover:text-white border border-slate-700 text-xs font-semibold transition-all shadow-sm"
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Load Sample Enterprise Docs</span>
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold transition-all shadow-md shadow-sky-600/30"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Documents</span>
          </button>
          <input
            type="file"
            ref={fileInputRef}
            multiple
            accept=".pdf,.txt,.md,.markdown,.csv,.json,.docx"
            onChange={(e) => handleFileUpload(e.target.files)}
            className="hidden"
          />
        </div>
      </div>

      {/* Action Notification Alert */}
      {actionNotice && (
        <div className={`p-4 rounded-xl text-sm flex items-center space-x-3 border ${
          actionNotice.type === 'success' ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30' :
          actionNotice.type === 'error' ? 'bg-red-950/40 text-red-300 border-red-500/30' :
          'bg-sky-950/40 text-sky-300 border-sky-500/30'
        }`}>
          {actionNotice.type === 'success' ? <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-400" /> :
           actionNotice.type === 'error' ? <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-400" /> :
           <RefreshCw className="w-5 h-5 flex-shrink-0 animate-spin text-sky-400" />}
          <span>{actionNotice.text}</span>
        </div>
      )}

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragActive(false)
          handleFileUpload(e.dataTransfer.files)
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-sky-400 bg-sky-950/20'
            : 'border-slate-800 hover:border-slate-700 bg-slate-900/30 hover:bg-slate-900/50'
        }`}
      >
        <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center mx-auto mb-3 text-slate-400">
          <Upload className="w-6 h-6 text-sky-400" />
        </div>
        <p className="text-sm font-semibold text-slate-200">
          Drag and drop technical manuals, policies, or specs here
        </p>
        <p className="text-xs text-slate-500 mt-1">
          Supports PDF, Markdown (.md), CSV tables, TXT, JSON • Automatic Recursive Chunking & Hybrid Vector Indexing
        </p>
      </div>

      {/* Documents Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-sky-400" />
            <h3 className="font-semibold text-sm text-white">Indexed Documents & Knowledge Assets</h3>
            <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
              {documents.length}
            </span>
          </div>

          <button
            onClick={fetchDocuments}
            disabled={loading}
            className="text-xs text-slate-400 hover:text-white flex items-center space-x-1"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {documents.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <FileText className="w-10 h-10 mx-auto mb-2 opacity-40" />
            <p className="text-sm font-medium">No documents currently indexed in the knowledge base.</p>
            <p className="text-xs mt-1">Click "Load Sample Enterprise Docs" or upload a file above to begin.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 uppercase font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3.5">Document Name</th>
                  <th className="px-6 py-3.5">Type</th>
                  <th className="px-6 py-3.5">Pages</th>
                  <th className="px-6 py-3.5">Chunks</th>
                  <th className="px-6 py-3.5">Size</th>
                  <th className="px-6 py-3.5">Indexed At</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {documents.map((doc) => (
                  <tr key={doc.doc_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-medium text-white flex items-center space-x-2.5">
                      <File className="w-4 h-4 text-sky-400 flex-shrink-0" />
                      <span className="truncate max-w-sm">{doc.doc_name}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded font-mono uppercase text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                        {doc.file_type ? doc.file_type.replace('.', '') : 'doc'}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono">{doc.page_count}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 font-mono font-semibold border border-sky-500/20">
                        {doc.chunk_count} chunks
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-400 font-mono">{formatFileSize(doc.file_size)}</td>
                    <td className="px-6 py-4 text-slate-400">{formatDate(doc.upload_time)}</td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button
                        onClick={() => handleViewChunks(doc.doc_id, doc.doc_name)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-400 hover:text-white transition-all"
                        title="Inspect Extracted Chunks"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(doc.doc_id, doc.doc_name)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-red-950/60 text-slate-400 hover:text-red-400 transition-all"
                        title="Delete Document & Vectors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Chunk Explorer Modal */}
      {chunkModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl">
            
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Layers className="w-5 h-5 text-sky-400" />
                <div>
                  <h3 className="font-bold text-white text-sm">Chunk Explorer</h3>
                  <p className="text-xs text-slate-400 truncate max-w-md">{selectedDocChunks?.docName}</p>
                </div>
              </div>
              <button
                onClick={() => setChunkModalOpen(false)}
                className="text-slate-400 hover:text-white text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700"
              >
                Close
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {loadingChunks ? (
                <div className="py-16 text-center text-slate-400 flex items-center justify-center space-x-2">
                  <RefreshCw className="w-5 h-5 animate-spin text-sky-400" />
                  <span>Loading document chunks...</span>
                </div>
              ) : selectedDocChunks?.chunks.length === 0 ? (
                <p className="text-center text-slate-500 py-12">No chunks found for this document.</p>
              ) : (
                selectedDocChunks?.chunks.map((chunk, idx) => (
                  <div key={idx} className="bg-slate-950 p-4 rounded-xl border border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span className="font-mono text-sky-300 font-semibold">
                        Chunk #{chunk.chunk_index} • Page {chunk.page_number}
                      </span>
                      <div className="flex items-center space-x-3 text-[11px]">
                        <span>{chunk.char_count} chars</span>
                        <span>~{chunk.token_estimate} tokens</span>
                        <span className="font-mono text-slate-500 text-[10px]">{chunk.chunk_id}</span>
                      </div>
                    </div>
                    <p className="text-slate-300 text-xs font-mono whitespace-pre-wrap leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                      {chunk.content}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="px-6 py-3 border-t border-slate-800 bg-slate-950 text-right">
              <span className="text-xs text-slate-400">
                Total Chunks: <strong className="text-white">{selectedDocChunks?.chunks.length || 0}</strong>
              </span>
            </div>

          </div>
        </div>
      )}

    </div>
  )
}
