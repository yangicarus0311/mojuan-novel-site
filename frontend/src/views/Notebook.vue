<template>
  <div class="notebook-page">
    <header class="page-header">
      <div class="container">
        <button class="back-btn" @click="$router.push('/')">← 返回</button>
        <h1>📝 划线本</h1>
        <p class="subtitle">所有带想法的划线汇聚于此</p>
      </div>
    </header>
    <div class="container">
      <div class="notebook-list">
        <div class="notebook-item" v-for="h in highlights" :key="h.id">
          <div class="highlight-content">
            <p class="highlight-text">"{{ h.content }}"</p>
            <p class="highlight-note" v-if="h.note">💭 {{ h.note }}</p>
          </div>
          <div class="highlight-meta">
            <span class="highlight-source">📖 来自作品</span>
            <span class="highlight-time">{{ formatDate(h.created_at) }}</span>
          </div>
        </div>
        <div class="empty-state" v-if="!highlights.length">
          <p>暂无带想法的划线</p>
          <p class="hint">在阅读中选中文字 → 添加想法</p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
const highlights = ref([])
const formatDate = (d) => d ? new Date(d).toLocaleDateString('zh-CN') : ''
onMounted(async () => {
  try { const r = await api.get('/highlights/notebook'); highlights.value = r.data || [] } catch(e) {}
})
</script>
<style scoped>
.notebook-page { min-height: 100vh; background: #0a0c10; }
.page-header {
  background: linear-gradient(to bottom, #0a0c10, #12151c);
  padding: 24px 0; border-bottom: 1px solid rgba(201,169,110,0.08);
}
.container { max-width: 800px; margin: 0 auto; padding: 0 24px; }
.back-btn { background: none; border: none; color: #8a8678; font-size: 14px; cursor: pointer; margin-bottom: 12px; }
h1 { font-size: 24px; color: #e8e4dc; }
.subtitle { font-size: 14px; color: #555248; margin-top: 4px; }
.notebook-list { padding: 24px 0; }
.notebook-item {
  background: #12151c; border: 1px solid rgba(201,169,110,0.08);
  border-radius: 12px; padding: 20px; margin-bottom: 12px;
}
.highlight-text { font-size: 15px; color: #e8e4dc; line-height: 1.7; font-style: italic; margin-bottom: 8px; }
.highlight-note {
  font-size: 14px; color: #8a8678; padding: 10px 14px;
  background: rgba(201,169,110,0.05); border-radius: 8px; line-height: 1.6;
}
.highlight-meta { display: flex; justify-content: space-between; margin-top: 12px; font-size: 12px; color: #555248; }
.empty-state { text-align: center; padding: 80px 0; color: #555248; }
.empty-state .hint { font-size: 13px; margin-top: 8px; opacity: 0.6; }
</style>
