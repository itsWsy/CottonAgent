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
  (response) => {
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) return body.data
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return body
  },
  (error) => {
    if ([401, 403].includes(error.response?.status)) {
      storage.removeToken()
      storage.removeUser()
      if (location.pathname !== '/login') location.href = '/login'
    }
    const serverMessage = error.response?.data?.message || error.response?.data?.detail
    const networkMessage = error.code === 'ECONNABORTED' ? '请求超时，请检查后端服务是否正常运行' : '无法连接到后端服务'
    return Promise.reject(new Error(serverMessage || error.message || networkMessage))
  }
)

export default request
