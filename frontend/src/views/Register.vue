<template>
  <div class="register-page">
    <div class="register-card">
      <h1>加入墨卷</h1>
      <p class="subtitle">开启沉浸式阅读之旅</p>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <input type="text" v-model="form.username" placeholder="用户名" required />
        </div>
        <div class="form-group">
          <input type="email" v-model="form.email" placeholder="邮箱" required />
        </div>
        <div class="form-group">
          <input type="password" v-model="form.password" placeholder="密码" required />
        </div>
        <button type="submit" class="register-btn" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
        <p class="error" v-if="error">{{ error }}</p>
      </form>
      <p class="login-link">已有账号？ <router-link to="/login">立即登录</router-link></p>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
const router = useRouter()
const form = ref({ username: '', email: '', password: '' })
const loading = ref(false)
const error = ref('')
const handleRegister = async () => {
  error.value = ''; loading.value = true
  try {
    const res = await api.post('/auth/register', form.value)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally { loading.value = false }
}
</script>
<style scoped>
.register-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #0a0c10; padding: 20px; }
.register-card { width: 100%; max-width: 380px; background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 16px; padding: 40px; }
h1 { font-size: 28px; color: #e8e4dc; text-align: center; }
.subtitle { font-size: 14px; color: #555248; text-align: center; margin-bottom: 32px; }
.form-group { margin-bottom: 16px; }
.form-group input { width: 100%; padding: 14px 16px; background: #0a0c10; border: 1px solid rgba(201,169,110,0.08); border-radius: 8px; color: #e8e4dc; font-size: 14px; outline: none; }
.form-group input:focus { border-color: rgba(201,169,110,0.25); }
.register-btn { width: 100%; padding: 14px; background: #c9a96e; border: none; border-radius: 8px; color: #0a0c10; font-size: 15px; font-weight: 600; cursor: pointer; }
.register-btn:disabled { opacity: 0.6; }
.error { margin-top: 12px; padding: 10px; background: rgba(255,100,100,0.1); border-radius: 8px; color: #ff6b6b; font-size: 13px; text-align: center; }
.login-link { margin-top: 24px; text-align: center; font-size: 14px; color: #555248; }
.login-link a { color: #c9a96e; text-decoration: none; }
</style>
