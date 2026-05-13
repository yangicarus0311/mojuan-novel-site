<template>
  <div class="stats-page">
    <header class="page-header">
      <div class="container">
        <button class="back-btn" @click="$router.push('/')">← 返回</button>
        <h1>📊 阅读统计</h1>
      </div>
    </header>
    <div class="container">
      <div class="stats-grid">
        <div class="stat-card primary">
          <span class="stat-icon">⏱</span>
          <span class="stat-value">{{ stats.total_duration_minutes || 0 }}</span>
          <span class="stat-label">总阅读时长(分)</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">📖</span>
          <span class="stat-value">{{ stats.total_chars?.toLocaleString() || 0 }}</span>
          <span class="stat-label">总阅读字数</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">📚</span>
          <span class="stat-value">{{ stats.total_works || 0 }}</span>
          <span class="stat-label">阅读作品</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">🔥</span>
          <span class="stat-value">{{ stats.streak_days || 0 }}</span>
          <span class="stat-label">连续阅读(天)</span>
        </div>
      </div>
      <div class="today-card">
        <h3>今日阅读</h3>
        <div class="today-value">{{ stats.today_minutes || 0 }} 分钟</div>
      </div>
      <div class="daily-section">
        <h3>每日阅读</h3>
        <div class="daily-list">
          <div class="daily-item" v-for="d in stats.daily_stats || []" :key="d.date">
            <span class="daily-date">{{ d.date }}</span>
            <div class="daily-bar-bg"><div class="daily-bar" :style="{ width: Math.min(100, d.duration_minutes * 3) + '%' }"></div></div>
            <span class="daily-value">{{ d.duration_minutes }} 分</span>
          </div>
          <div class="empty-state" v-if="!stats.daily_stats?.length">
            <p>今天还没有阅读记录</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
const stats = ref({})
onMounted(async () => {
  try { const r = await api.get('/reading/stats'); stats.value = r.data || {} } catch(e) {}
})
</script>
<style scoped>
.stats-page { min-height: 100vh; background: #0a0c10; padding-bottom: 60px; }
.page-header { padding: 24px 0; border-bottom: 1px solid rgba(201,169,110,0.08); }
.container { max-width: 800px; margin: 0 auto; padding: 0 24px; }
.back-btn { background: none; border: none; color: #8a8678; font-size: 14px; cursor: pointer; margin-bottom: 12px; }
h1 { font-size: 24px; color: #e8e4dc; }
h3 { font-size: 16px; color: #e8e4dc; margin-bottom: 16px; }
.stats-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 12px; margin: 24px 0; }
.stat-card {
  background: #12151c; border: 1px solid rgba(201,169,110,0.08);
  border-radius: 12px; padding: 20px; text-align: center;
}
.stat-card.primary { grid-column: span 2; background: linear-gradient(135deg, #1a1e2e, #12151c); }
.stat-icon { display: block; font-size: 28px; margin-bottom: 8px; }
.stat-value { display: block; font-size: 28px; font-weight: 700; color: #c9a96e; }
.stat-label { display: block; font-size: 13px; color: #555248; margin-top: 4px; }
.today-card {
  background: linear-gradient(135deg, rgba(201,169,110,0.1), transparent);
  border: 1px solid rgba(201,169,110,0.15); border-radius: 12px;
  padding: 20px; text-align: center; margin-bottom: 24px;
}
.today-value { font-size: 36px; font-weight: 700; color: #c9a96e; }
.daily-section { margin-bottom: 40px; }
.daily-list { display: flex; flex-direction: column; gap: 8px; }
.daily-item { display: flex; align-items: center; gap: 12px; }
.daily-date { width: 80px; font-size: 13px; color: #8a8678; }
.daily-bar-bg { flex: 1; height: 8px; background: #1e2330; border-radius: 4px; overflow: hidden; }
.daily-bar { height: 100%; background: #c9a96e; border-radius: 4px; transition: width 0.5s; }
.daily-value { width: 60px; text-align: right; font-size: 12px; color: #555248; }
.empty-state { text-align: center; padding: 40px; color: #555248; }
</style>
