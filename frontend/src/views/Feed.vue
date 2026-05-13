<template>
  <div class="feed-page">
    <header class="page-header">
      <div class="container">
        <button class="back-btn" @click="$router.push('/')">← 返回</button>
        <h1>🌊 好友动态</h1>
      </div>
    </header>
    <div class="container">
      <div class="feed-list">
        <div class="feed-item" v-for="(event, idx) in feed" :key="idx">
          <div class="feed-user">
            <span class="feed-avatar">{{ event.user?.username?.[0]?.toUpperCase() || '?' }}</span>
            <div class="feed-user-info">
              <span class="feed-username">{{ event.user?.username || '匿名' }}</span>
              <span class="feed-type">{{ typeLabel(event.type) }}</span>
            </div>
            <span class="feed-time">{{ timeAgo(event.created_at) }}</span>
          </div>
          <div class="feed-content">{{ event.content }}</div>
          <div class="feed-work" v-if="event.work">
            <span class="feed-work-icon">{{ typeIcon(event.type) }}</span>
            <span>{{ event.work.title }}</span>
          </div>
          <div class="feed-rating" v-if="event.rating">
            {{ '★'.repeat(event.rating) }}{{ '☆'.repeat(5-event.rating) }}
          </div>
        </div>
        <div class="empty-state" v-if="!feed.length">
          <p>暂无动态</p>
          <p class="hint">关注更多好友，发现精彩阅读动态</p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
const feed = ref([])
const typeLabel = (t) => ({ reading: '在读', review: '写了书评', bookshelf: '收藏了作品' }[t] || t)
const typeIcon = (t) => ({ reading: '📖', review: '📝', bookshelf: '📚' }[t] || '•')
const timeAgo = (d) => {
  if (!d) return ''
  const diff = Math.floor((Date.now() - new Date(d).getTime()) / 60000)
  if (diff < 1) return '刚刚'
  if (diff < 60) return diff + '分钟前'
  if (diff < 1440) return Math.floor(diff / 60) + '小时前'
  return Math.floor(diff / 1440) + '天前'
}
onMounted(async () => {
  try { const r = await api.get('/social/feed'); feed.value = r.data || [] } catch(e) {}
})
</script>
<style scoped>
.feed-page { min-height: 100vh; background: #0a0c10; padding-bottom: 60px; }
.page-header { padding: 24px 0; border-bottom: 1px solid rgba(201,169,110,0.08); }
.container { max-width: 700px; margin: 0 auto; padding: 0 24px; }
.back-btn { background: none; border: none; color: #8a8678; font-size: 14px; cursor: pointer; margin-bottom: 12px; }
h1 { font-size: 22px; color: #e8e4dc; }
.feed-list { padding: 20px 0; }
.feed-item { background: #12151c; border: 1px solid rgba(201,169,110,0.06); border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; }
.feed-user { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.feed-avatar { width: 36px; height: 36px; border-radius: 50%; background: #1e2330; display: flex; align-items: center; justify-content: center; color: #c9a96e; font-weight: 700; }
.feed-user-info { flex: 1; }
.feed-username { display: block; font-size: 14px; color: #e8e4dc; }
.feed-type { display: block; font-size: 12px; color: #555248; }
.feed-time { font-size: 12px; color: #555248; }
.feed-content { font-size: 14px; color: #8a8678; line-height: 1.6; margin-bottom: 8px; }
.feed-work { font-size: 13px; color: #c9a96e; }
.feed-rating { font-size: 13px; color: #ffb300; margin-top: 4px; }
.empty-state { text-align: center; padding: 80px 0; color: #555248; }
.empty-state .hint { font-size: 13px; margin-top: 8px; opacity: 0.6; }
</style>
