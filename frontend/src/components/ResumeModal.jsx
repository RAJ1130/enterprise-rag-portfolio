import React from 'react'
import { X, Mail, Phone, MapPin, Globe, GraduationCap, Briefcase, Code, Award, ExternalLink, FileText } from 'lucide-react'

export default function ResumeModal({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-800 bg-gradient-to-r from-sky-950/60 via-slate-900 to-indigo-950/60 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-bold text-lg text-white shadow-lg shadow-sky-500/20">
              MR
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-extrabold text-white text-lg">Mummalar Raj A</h3>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Full Stack / AI Fresher
                </span>
              </div>
              <p className="text-xs text-slate-400">B.Tech – Artificial Intelligence & Data Science (CGPA: 7.4)</p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs text-slate-300">
          
          {/* Contact Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
            <div className="flex items-center space-x-2 text-slate-300">
              <MapPin className="w-4 h-4 text-sky-400 flex-shrink-0" />
              <span>Chennai, Tamil Nadu</span>
            </div>
            <a href="tel:+916382061572" className="flex items-center space-x-2 text-sky-400 hover:underline">
              <Phone className="w-4 h-4 flex-shrink-0" />
              <span>+91 6382061572</span>
            </a>
            <a href="mailto:mummalarraj27@gmail.com" className="flex items-center space-x-2 text-sky-400 hover:underline truncate">
              <Mail className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">mummalarraj27@gmail.com</span>
            </a>
            <a
              href="https://linkedin.com/in/mummalar-raj-515293297"
              target="_blank"
              rel="noreferrer"
              className="flex items-center space-x-2 text-sky-400 hover:underline"
            >
              <Globe className="w-4 h-4 flex-shrink-0" />
              <span>LinkedIn Profile</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>


          {/* Professional Summary */}
          <div>
            <h4 className="font-bold text-sm text-white flex items-center space-x-2 mb-2">
              <Award className="w-4 h-4 text-amber-400" />
              <span>Professional Summary</span>
            </h4>
            <p className="bg-slate-950/50 p-4 rounded-xl border border-slate-800/80 leading-relaxed text-slate-300">
              A motivated frontend and full-stack developer fresher seeking an entry-level opportunity to apply skills in HTML, CSS, JavaScript, React.js, Python, and Django to design and develop responsive, scalable web applications. Successfully built projects including Cryptocurrency Tracker, Smart Health System, and an Enterprise RAG Knowledge Base. Eager to learn, grow, and contribute to dynamic engineering teams.
            </p>
          </div>

          {/* Technical Skills Grid */}
          <div>
            <h4 className="font-bold text-sm text-white flex items-center space-x-2 mb-2">
              <Code className="w-4 h-4 text-indigo-400" />
              <span>Technical Skills</span>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                <span className="text-[10px] uppercase font-bold text-sky-400 block mb-1">Languages & Frontend</span>
                <p className="font-medium text-slate-200">JavaScript (ES6+), Python, HTML5, CSS3, React.js, Tailwind CSS, Bootstrap</p>
              </div>
              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                <span className="text-[10px] uppercase font-bold text-indigo-400 block mb-1">Backend & Databases</span>
                <p className="font-medium text-slate-200">FastAPI, Django, Django REST Framework, MySQL, MongoDB, SQLite, Vector Stores</p>
              </div>
              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                <span className="text-[10px] uppercase font-bold text-amber-400 block mb-1">Architecture & AI</span>
                <p className="font-medium text-slate-200">RAG (Retrieval-Augmented Generation), Hybrid BM25/Vector Search, RESTful APIs, CRUD</p>
              </div>
              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-1">Tools & Platforms</span>
                <p className="font-medium text-slate-200">Git, GitHub, VS Code, Postman, Vite, Docker, Render, Vercel</p>
              </div>
            </div>
          </div>

          {/* Internship Experience */}
          <div>
            <h4 className="font-bold text-sm text-white flex items-center space-x-2 mb-2">
              <Briefcase className="w-4 h-4 text-emerald-400" />
              <span>Internship Experience</span>
            </h4>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-100">BDreamz Global Solutions – Chennai</span>
                <span className="text-slate-400 font-mono text-[11px]">Feb 2026 – Present</span>
              </div>
              <p className="text-sky-400 font-medium">Role: Full Stack Developer Intern (3 Months)</p>
              <ul className="list-disc list-inside space-y-1 text-slate-300">
                <li>Building end-to-end web applications using HTML, CSS, JavaScript, React, and backend technologies.</li>
                <li>Developing responsive interfaces, secure server-side logic, and database integration.</li>
                <li>Delivering scalable, user-centric solutions with RESTful API communication.</li>
              </ul>
            </div>
          </div>

          {/* Education */}
          <div>
            <h4 className="font-bold text-sm text-white flex items-center space-x-2 mb-2">
              <GraduationCap className="w-4 h-4 text-sky-400" />
              <span>Education</span>
            </h4>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
              <div>
                <p className="font-bold text-slate-100">Mahendra College of Engineering, Salem, Tamil Nadu</p>
                <p className="text-slate-400">B.Tech – Artificial Intelligence and Data Science</p>
              </div>
              <div className="text-right">
                <span className="px-2.5 py-1 rounded-lg bg-sky-500/10 text-sky-400 font-bold border border-sky-500/30">
                  CGPA: 7.4 / 10.0
                </span>
                <p className="text-[11px] text-slate-500 mt-1 font-mono">Nov 2022 – May 2026</p>
              </div>
            </div>
          </div>

          {/* Resume In RAG Notice */}
          <div className="bg-sky-950/40 border border-sky-500/30 p-4 rounded-xl flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <FileText className="w-5 h-5 text-sky-400 flex-shrink-0" />
              <div>
                <span className="font-bold text-white block">Resume Indexed in Live AI Assistant</span>
                <span className="text-slate-400 text-[11px]">You can ask the AI any question about Mummalar's projects, experience, or skills!</span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs shadow-md shadow-sky-600/30"
            >
              Ask AI About Resume
            </button>
          </div>

        </div>

      </div>
    </div>
  )
}
