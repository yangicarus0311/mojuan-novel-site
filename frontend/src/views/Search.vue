<template>
  <div class="search-page">
    <header class="page-header">
      <div class="container">
        <div class="search-box">
          <input type="text" v-model="keyword" placeholder="搜索作品、作者..."
            @keyup.enter="doSearch" @input="onInput" ref="searchInput" autofocus />
          <button @click="doSearch">🔍</button>
        </div>
        <!-- 搜索联想 -->
        <div class="suggestions" v-if="suggestions.length && !hasSearched">
          <div class="suggestion-item" v-for="s in suggestions" :key="s" @click="keyword = s; doSearch()">
            🔍 {{ s }}
          </div>
        </div>
      </div>
    </header>
    <div class="container">
      <div class="result-info" v-if="hasSearched">
        <span>找到 {{ total }} 个结果</span>
        <div class="sort-options">
          <button :class="{ active: sortBy === 'relevance' }" @click="sortBy = 'relevance'; doSearch()">相关度</button>
          <button :class="{ active: sortBy === 'clicks' }" @click="sortBy = 'clicks'; doSearch()">人气</button>
          <button :class="{ active: sortBy === 'updated_at' }" @click="sortBy = 'updated_at'; doSearch()">最近更新</button>
        </div>
      </div>
      <p v-if="loading" role="status">搜索中...</p>
      <div v-else-if="errorMessage" role="alert">{{ errorMessage }} <button @click="doSearch">重试</button></div>
      <div class="results-list" v-else-if="hasSearched">
        <div class="result-item" v-for="r in results" :key="r.id" @click="$router.push(`/works/${r.id}`)">
          <div class="result-cover" :style="{ background: getGradient(r.id) }"></div>
          <div class="book-result-info">
            <h3><HighlightedText :text="r.title" :keyword="submittedKeyword" /></h3>
            <p class="author"><HighlightedText :text="r.author" :keyword="submittedKeyword" /></p>
            <p class="desc">{{ r.description?.slice(0, 80) }}...</p>
            <div class="meta">
              <span>{{ r.category }}</span>
              <span>{{ (r.word_count || r.wordCount || 0).toLocaleString() }}字</span>
            </div>
          </div>
        </div>
        <div class="no-results" v-if="!results.length && keyword">
          <p>未找到"{{ keyword }}"相关的结果</p>
          <p class="hint">试试其他关键词</p>
        </div>
      </div>
      <div class="pagination" v-if="hasSearched && !loading && !errorMessage && total > pageSize">
        <button :disabled="page <= 1" @click="searchPage(page - 1)">上一页</button>
        <span>{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
        <button :disabled="page * pageSize >= total" @click="searchPage(page + 1)">下一页</button>
      </div>
      <div class="hot-searches" v-if="!hasSearched">
        <h3>🔥 热门搜索</h3>
        <div class="hot-tags">
          <span class="hot-tag" v-for="(tag, idx) in hotTags" :key="tag" @click="keyword = tag; doSearch()">
            {{ idx < 3 ? '🔥' : '' }} {{ tag }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../api'
import HighlightedText from '../components/HighlightedText.vue'
const keyword = ref('')
const submittedKeyword = ref('')
const results = ref([])
const suggestions = ref([])
const hasSearched = ref(false)
const sortBy = ref('relevance')
const searchInput = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const total = ref(0)
const page = ref(1)
const pageSize = 20
let requestId = 0
const hotTags = ['玄幻', '仙侠', '都市', '科幻', '言情', '穿越', '系统', '重生']
const getGradient = (id) => ['linear-gradient(135deg,#1a1e2e,#0f1118)','linear-gradient(135deg,#2d1f3d,#14101f)'][(id || 0) % 2]
const onInput = () => { suggestions.value = [] }
const searchPage = async (targetPage = 1) => {
  if (!submittedKeyword.value) return
  const id = ++requestId
  hasSearched.value = true
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await api.get('/works/search', { params: {
      q: submittedKeyword.value, sort: sortBy.value, page: targetPage, page_size: pageSize
    } })
    if (id !== requestId) return
    results.value = response.data.works
    total.value = response.data.total
    page.value = targetPage
  } catch (error) {
    if (id === requestId) errorMessage.value = '搜索失败，请检查连接后重试。'
  } finally {
    if (id === requestId) loading.value = false
  }
}
const doSearch = () => {
  submittedKeyword.value = keyword.value.trim()
  suggestions.value = []
  return searchPage(1)
}
onMounted(() => nextTick(() => searchInput.value?.focus()))
</script>
<style scoped>
.search-page { min-height: 100vh; background: #0a0c10; padding-bottom: 60px; }
.page-header { padding: 24px 0; border-bottom: 1px solid rgba(201,169,110,0.08); }
.container { max-width: 800px; margin: 0 auto; padding: 0 24px; }
.search-box { display: flex; gap: 8px; }
.search-box input { flex: 1; padding: 14px 20px; background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 12px; color: #e8e4dc; font-size: 16px; outline: none; }
.search-box input:focus { border-color: rgba(201,169,110,0.25); }
.search-box button { padding: 14px 24px; background: #c9a96e; border: none; border-radius: 12px; color: #0a0c10; font-size: 16px; cursor: pointer; }
.suggestions { margin-top: 8px; background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 12px; overflow: hidden; }
.suggestion-item { padding: 12px 20px; color: #8a8678; font-size: 14px; cursor: pointer; }
.suggestion-item:hover { background: rgba(201,169,110,0.05); }
.result-info { display: flex; align-items: center; justify-content: space-between; font-size: 14px; color: #555248; margin: 20px 0; }
.sort-options { display: flex; gap: 8px; }
.sort-options button { padding: 4px 12px; background: transparent; border: 1px solid rgba(201,169,110,0.08); border-radius: 16px; color: #555248; font-size: 12px; cursor: pointer; }
.sort-options button.active { border-color: #c9a96e; color: #c9a96e; }
.results-list { display: flex; flex-direction: column; gap: 12px; }
.result-item { display: flex; gap: 16px; padding: 16px; background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 12px; cursor: pointer; transition: border-color 0.2s; }
.result-item:hover { border-color: rgba(201,169,110,0.25); }
.result-cover { width: 80px; height: 110px; border-radius: 8px; flex-shrink: 0; }
.book-result-info { flex: 1; min-width: 0; }
.book-result-info h3 { font-size: 16px; color: #e8e4dc; margin-bottom: 4px; }
.author { font-size: 13px; color: #8a8678; margin-bottom: 8px; }
.desc { font-size: 13px; color: #555248; margin-bottom: 8px; line-height: 1.5; }
.meta { display: flex; gap: 8px; font-size: 11px; }
.meta span { padding: 2px 8px; background: rgba(201,169,110,0.1); border-radius: 4px; color: #8a7445; }
.no-results { text-align: center; padding: 60px 0; color: #555248; }
.no-results .hint { font-size: 13px; margin-top: 8px; opacity: 0.6; }
.hot-searches { padding: 24px 0; }
.hot-searches h3 { font-size: 16px; color: #e8e4dc; margin-bottom: 16px; }
.hot-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.hot-tag { padding: 8px 16px; background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 20px; font-size: 13px; color: #8a8678; cursor: pointer; }
.hot-tag:hover { border-color: rgba(201,169,110,0.25); color: #c9a96e; }
.pagination { display: flex; gap: 16px; align-items: center; justify-content: center; padding: 24px; }
.pagination button { padding: 8px 12px; border: 1px solid #c9a96e; border-radius: 6px; background: transparent; color: #c9a96e; }
.pagination button:disabled { opacity: .4; }
</style>
