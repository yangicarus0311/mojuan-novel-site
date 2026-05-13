<template>
  <div class="bookshelf-page">
    <header class="page-header">
      <div class="container">
        <h1>📚 我的书架</h1>
        <span class="book-count">{{ bookshelf.length }} 本</span>
      </div>
    </header>
    <div class="container">
      <div class="empty-state" v-if="!bookshelf.length">
        <p>书架空空如也 📭</p>
        <router-link to="/" class="explore-btn">去发现好书</router-link>
      </div>
      <div class="bookshelf-grid" v-else>
        <div class="book-item" v-for="item in bookshelf" :key="item.id">
          <div class="book-cover" :style="{ background: getGradient(item.id || item.work?.id) }"
               @click="goWork(item.work?.id || item.work_id)">
            <div class="book-progress-bar" v-if="item.progress_pct">
              <div class="progress-fill" :style="{ width: item.progress_pct + '%' }"></div>
            </div>
          </div>
          <div class="book-info">
            <h3 @click="goWork(item.work?.id || item.work_id)">{{ item.work?.title || '作品' }}</h3>
            <p>{{ item.work?.author || '' }}</p>
            <div class="book-meta">
              <span class="book-category">{{ item.work?.category || '' }}</span>
              <span class="book-status" v-if="item.work?.status === 'completed'">完本</span>
            </div>
            <button class="remove-btn" @click="removeBook(item.work?.id || item.work_id)">移除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
const router = useRouter()
const bookshelf = ref([])
const getGradient = (id) => {
  const g = ['linear-gradient(135deg,#1a1e2e,#0f1118)','linear-gradient(135deg,#2d1f3d,#14101f)','linear-gradient(135deg,#1f2d30,#0f1414)'];
  return g[(id||0)%g.length]
}
const goWork = (id) => { if(id) router.push(`/works/${id}`) }
const removeBook = async (id) => {
  try { await api.delete(`/bookshelf/${id}`); bookshelf.value = bookshelf.value.filter(b => (b.work?.id || b.work_id) !== id) } catch(e) {}
}
onMounted(async () => {
  try { const r = await api.get('/bookshelf'); bookshelf.value = r.data || [] } catch(e) {}
})
</script>
<style scoped>
.bookshelf-page { min-height: 100vh; background: #0a0c10; padding-bottom: 80px; }
.page-header { padding: 24px 0; border-bottom: 1px solid rgba(201,169,110,0.08); }
.container { max-width: 1000px; margin: 0 auto; padding: 0 24px; }
h1 { font-size: 22px; color: #e8e4dc; display: inline; }
.book-count { margin-left: 12px; font-size: 14px; color: #555248; }
.empty-state { text-align: center; padding: 100px 0; color: #555248; }
.explore-btn { display: inline-block; margin-top: 16px; padding: 12px 32px; background: #c9a96e; color: #0a0c10; border-radius: 8px; text-decoration: none; font-weight: 600; }
.bookshelf-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; padding: 24px 0; }
.book-item { display: flex; gap: 16px; background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 12px; padding: 16px; }
.book-cover { width: 80px; height: 110px; border-radius: 8px; flex-shrink: 0; cursor: pointer; position: relative; overflow: hidden; }
.book-progress-bar { position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background: rgba(0,0,0,0.3); }
.progress-fill { height: 100%; background: #c9a96e; }
.book-info { flex: 1; min-width: 0; }
.book-info h3 { font-size: 15px; color: #e8e4dc; margin-bottom: 4px; cursor: pointer; }
.book-info p { font-size: 13px; color: #8a8678; margin-bottom: 8px; }
.book-meta { display: flex; gap: 8px; font-size: 11px; }
.book-category, .book-status { padding: 2px 8px; border-radius: 4px; background: rgba(201,169,110,0.1); color: #8a7445; }
.book-status { background: rgba(76,175,80,0.1); color: #4CAF50; }
.remove-btn { margin-top: 10px; padding: 4px 12px; background: transparent; border: 1px solid rgba(255,100,100,0.3); border-radius: 4px; color: #ff6b6b; font-size: 12px; cursor: pointer; }
</style>
