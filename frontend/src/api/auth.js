import request from '../utils/request'

export const loginApi = (data) => request.post('/auth/login', data)
export const profileApi = () => request.get('/auth/profile')
