<template>
  <div class="admin-works">
    <h1>作品管理</h1>
    <div class="works-table">
      <div class="table-header">
        <span>ID</span><span>标题</span><span>作者</span><span>分类</span><span>字数</span><span>点击</span><span>操作</span>
      </div>
      <div class="table-row" v-for="w in works" :key="w.id">
        <span>{{ w.id }}</span>
        <span class="title">{{ w.title }}</span>
        <span>{{ w.author }}</span>
        <span>{{ w.category }}</span>
        <span>{{ (w.word_count || 0).toLocaleString() }}</span>
        <span>{{ (w.clicks || 0).toLocaleString() }}</span>
        <span><button class="del-btn" @click="deleteWork(w.id)">删除</button></span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
const works = ref([])
const deleteWork = async (id) => {
  if (!confirm('确定删除？')) return
  try { await api.delete(`/admin/works/${id}`); works.value = works.value.filter(w => w.id !== id) } catch(e) {}
}
onMounted(async () => {
  try { const r = await api.get('/admin/works'); works.value = r.data || [] } catch(e) {}
})
</script>
<style scoped>
h1 { font-size: 24px; color: #e8e4dc; margin-bottom: 24px; }
.works-table { background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 12px; overflow: hidden; }
.table-header, .table-row { display: grid; grid-template-columns: 50px 2fr 1fr 80px 80px 80px 80px; padding: 12px 20px; align-items: center; }
.table-header { background: rgba(201,169,110,0.05); color: #555248; font-size: 12px; }
.table-row { border-bottom: 1px solid rgba(201,169,110,0.05); color: #8a8678; font-size: 13px; }
.table-row .title { color: #e8e4dc; }
.del-btn { padding: 4px 12px; background: transparent; border: 1px solid rgba(255,100,100,0.3); border-radius: 4px; color: #ff6b6b; font-size: 12px; cursor: pointer; }
</style>
