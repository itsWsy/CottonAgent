import axios from 'axios'
import { storage } from './storage'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 12000
})

request.interceptors.request.use((config) => {
  const token = storage.getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use(
  (response) => response.data.data,
  (error) => {
    if (error.response?.status === 401) {
      storage.removeToken()
      storage.removeUser()
      if (location.pathname !== '/login') location.href = '/login'
    }
    return Promise.reject(new Error(error.response?.data?.message || error.response?.data?.detail || '请求失败'))
  }
)

export default request
