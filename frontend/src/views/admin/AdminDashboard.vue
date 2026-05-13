<template>
  <div class="admin-dashboard">
    <h1>仪表盘</h1>
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-value">{{ stats.total_users || 0 }}</span>
        <span class="stat-label">用户总数</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.total_works || 0 }}</span>
        <span class="stat-label">作品总数</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.total_chapters || 0 }}</span>
        <span class="stat-label">章节总数</span>
      </div>
      <div class="stat-card accent">
        <span class="stat-value">{{ stats.new_users_today || 0 }}</span>
        <span class="stat-label">今日新用户</span>
      </div>
      <div class="stat-card accent">
        <span class="stat-value">{{ stats.new_works_today || 0 }}</span>
        <span class="stat-label">今日新作品</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
const stats = ref({})
onMounted(async () => {
  try { const r = await api.get('/admin/stats'); stats.value = r.data } catch(e) {}
})
</script>
<style scoped>
h1 { font-size: 24px; color: #e8e4dc; margin-bottom: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px,1fr)); gap: 16px; }
.stat-card { background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 12px; padding: 24px; }
.stat-value { display: block; font-size: 32px; font-weight: 700; color: #c9a96e; }
.stat-label { display: block; font-size: 14px; color: #555248; margin-top: 8px; }
.stat-card.accent .stat-value { color: #4CAF50; }
</style>
