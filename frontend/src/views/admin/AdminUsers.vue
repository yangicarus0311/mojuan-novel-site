<template>
  <div class="admin-users">
    <h1>用户管理</h1>
    <div class="users-table">
      <div class="table-header">
        <span>ID</span><span>用户名</span><span>邮箱</span><span>注册时间</span><span>角色</span>
      </div>
      <div class="table-row" v-for="u in users" :key="u.id">
        <span>{{ u.id }}</span>
        <span class="username">{{ u.username }}</span>
        <span>{{ u.email }}</span>
        <span>{{ formatDate(u.created_at) }}</span>
        <span>{{ u.is_admin ? '管理员' : '用户' }}</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
const users = ref([])
const formatDate = (d) => d ? new Date(d).toLocaleDateString('zh-CN') : ''
onMounted(async () => {
  try { const r = await api.get('/admin/users'); users.value = r.data || [] } catch(e) {}
})
</script>
<style scoped>
h1 { font-size: 24px; color: #e8e4dc; margin-bottom: 24px; }
.users-table { background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 12px; overflow: hidden; }
.table-header, .table-row { display: grid; grid-template-columns: 60px 1.5fr 2fr 1fr 80px; padding: 12px 20px; align-items: center; }
.table-header { background: rgba(201,169,110,0.05); color: #555248; font-size: 12px; }
.table-row { border-bottom: 1px solid rgba(201,169,110,0.05); color: #8a8678; font-size: 13px; }
.table-row .username { color: #e8e4dc; }
</style>
