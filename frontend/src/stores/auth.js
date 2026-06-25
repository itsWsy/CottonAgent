import { defineStore } from 'pinia'
import { loginApi, profileApi } from '../api/auth'
import { storage } from '../utils/storage'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: storage.getToken() || '', userInfo: storage.getUser() }),
  actions: {
    async login(payload) {
      const data = await loginApi(payload)
      this.token = data.token
      this.userInfo = data.userInfo
      storage.setToken(data.token)
      storage.setUser(data.userInfo)
    },
    logout() {
      this.token = ''
      this.userInfo = null
      storage.removeToken()
      storage.removeUser()
    },
    async loadProfile() {
      this.userInfo = await profileApi()
      storage.setUser(this.userInfo)
    }
  }
})
