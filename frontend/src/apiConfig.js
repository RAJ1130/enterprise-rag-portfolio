// Dynamic API URL for Vercel + Render deployments
export const API_BASE = import.meta.env.VITE_API_URL || ''

export const getApiUrl = (path) => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE}${cleanPath}`
}
