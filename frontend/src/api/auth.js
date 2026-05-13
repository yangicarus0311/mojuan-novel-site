import { authAPI } from './index'

export const login = (data) => authAPI.login(data)
export const register = (data) => authAPI.register(data)
export const getMe = () => authAPI.getMe()
