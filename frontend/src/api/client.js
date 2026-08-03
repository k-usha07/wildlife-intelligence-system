import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({ baseURL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export async function login(email, password) {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const res = await api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return res.data
}

export async function register(payload) {
  const res = await api.post('/auth/register', payload)
  return res.data
}

export async function fetchMe() {
  const res = await api.get('/auth/me')
  return res.data
}

export async function fetchSummary() {
  const res = await api.get('/surveys/me/summary')
  return res.data
}

export async function fetchSurveys() {
  const res = await api.get('/surveys')
  return res.data
}

export async function createSurvey(payload) {
  const res = await api.post('/surveys', payload)
  return res.data
}

export async function fetchSites() {
  const res = await api.get('/monitoring-sites')
  return res.data
}

export async function createSite(payload) {
  const res = await api.post('/monitoring-sites', payload)
  return res.data
}

export async function fetchDevices() {
  const res = await api.get('/devices')
  return res.data
}

export async function createDevice(payload) {
  const res = await api.post('/devices', payload)
  return res.data
}

export async function fetchUsers() {
  const res = await api.get('/users')
  return res.data
}
