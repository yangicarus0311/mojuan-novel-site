<template>
  <div class="home">
    <!-- 顶部导航 -->
    <header class="home-nav">
      <div class="nav-inner container">
        <div class="nav-left">
          <h1 class="logo">墨卷</h1>
        </div>
        <div class="nav-right">
          <router-link to="/search" class="nav-link">🔍</router-link>
          <router-link to="/bookshelf" class="nav-link">📚</router-link>
          <router-link v-if="!isLoggedIn" to="/login" class="nav-btn">登录</router-link>
          <router-link v-else :to="'/profile/' + currentUserId" class="nav-avatar">{{ userInitial }}</router-link>
        </div>
      </div>
    </header>

    <!-- Hero Banner -->
    <section class="hero-section">
      <div class="container">
        <div class="hero-card" @click="goWork(featured[0]?.id)">
          <div class="hero-bg" :style="featured[0]?.cover_url ? { backgroundImage: `url(${featured[0].cover_url})`, backgroundSize: 'cover', backgroundPosition: 'center' } : { background: 'linear-gradient(135deg, #1a1e2e 0%, #0f1118 100%)' }"></div>
          <div class="hero-content">
            <span class="hero-badge">{{ featured[0]?.category || '推荐' }}</span>
            <h2 class="hero-title">{{ featured[0]?.title || '欢迎来到墨卷' }}</h2>
            <p class="hero-author">{{ featured[0]?.author || '' }}</p>
            <p class="hero-desc">{{ featured[0]?.description?.slice(0, 80) || '沉浸式阅读体验，开启你的阅读之旅' }}...</p>
            <div class="hero-stats">
              <span>{{ featured[0]?.wordCount?.toLocaleString() || 0 }}字</span>
              <span>{{ featured[0]?.clicks?.toLocaleString() || 0 }}阅读</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 快速分类 -->
    <section class="categories-section container">
      <div class="categories-scroll">
        <button v-for="cat in categories" :key="cat" class="category-chip"
          :class="{ active: selectedCategory === cat }" @click="selectCategory(cat)">
          {{ cat }}
        </button>
      </div>
    </section>

    <!-- 热门推荐 -->
    <section class="section container" v-if="hotWorks.length">
      <div class="section-header">
        <h2 class="section-title">🔥 热门推荐</h2>
        <router-link to="/search" class="section-more">更多 →</router-link>
      </div>
      <div class="horizontal-scroll">
        <div class="work-card-h" v-for="w in hotWorks" :key="w.id" @click="goWork(w.id)">
          <div class="card-cover" :style="w.cover_url ? {} : { background: getGradient(w.id) }">
            <img v-if="w.cover_url" :src="w.cover_url" alt="" class="cover-img" @error="onCoverError(w)" />
          </div>
          <div class="card-info">
            <h3>{{ w.title }}</h3>
            <p class="card-author">{{ w.author }}</p>
            <div class="card-tags">
              <span class="tag">{{ w.category }}</span>
              <span class="tag" v-if="w.status === 'completed'">完本</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 精选作品网格 -->
    <section class="section container">
      <div class="section-header">
        <h2 class="section-title">{{ selectedCategory === '全部' ? '📖 作品列表' : selectedCategory }}</h2>
      </div>
      <div class="works-grid">
        <div class="work-card" v-for="work in displayWorks" :key="work.id" @click="goWork(work.id)">
          <div class="work-cover" :style="work.cover_url ? {} : { background: getGradient(work.id) }">
            <img v-if="work.cover_url" :src="work.cover_url" alt="" class="cover-img" @error="onCoverError(work)" />
            <span class="work-rank" v-if="work.rank && work.rank <= 3">{{ work.rank }}</span>
          </div>
          <div class="work-info">
            <h3 class="work-title">{{ work.title }}</h3>
            <p class="work-author">{{ work.author }}</p>
            <div class="work-meta">
              <span>{{ work.category }}</span>
              <span>{{ (work.word_count || work.wordCount || 0).toLocaleString() }}字</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 加载更多 -->
    <div class="load-more container" v-if="hasMore">
      <button @click="loadMore" :disabled="loadingMore" class="load-btn">
        {{ loadingMore ? '加载中...' : '加载更多' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const works = ref([])
const hotWorks = ref([])
const featured = ref([])
const isLoggedIn = ref(!!localStorage.getItem('token'))
const currentUserId = ref(null)
const userInitial = ref('')
const selectedCategory = ref('全部')
const currentPage = ref(1)
const loadingMore = ref(false)
const hasMore = ref(true)

const categories = ['全部', '玄幻', '仙侠', '都市', '历史', '科幻', '游戏', '轻小说', '言情', '悬疑']

const displayWorks = computed(() => {
  if (selectedCategory.value === '全部') return works.value
  return works.value.filter(w => (w.category || w.category_name) === selectedCategory.value)
})

const getGradient = (id) => {
  const gradients = [
    'linear-gradient(135deg, #1a1e2e, #0f1118)',
    'linear-gradient(135deg, #2d1f3d, #14101f)',
    'linear-gradient(135deg, #1f2d30, #0f1414)',
    'linear-gradient(135deg, #2d2d1f, #14140f)',
    'linear-gradient(135deg, #2d1f1f, #14100f)',
    'linear-gradient(135deg, #1f2d2d, #0f1414)',
    'linear-gradient(135deg, #3d2d1f, #1f1410)',
    'linear-gradient(135deg, #2d1f2d, #141014)',
  ]
  return gradients[(id || 0) % gradients.length]
}

const onCoverError = (work) => {
  work.cover_url = null
}

const goWork = (id) => {
  if (id) router.push(`/works/${id}`)
}

const selectCategory = (cat) => {
  selectedCategory.value = cat
}

const loadMore = async () => {
  loadingMore.value = true
  currentPage.value++
  try {
    const res = await api.get('/works', { params: { page: currentPage.value, page_size: 12 } })
    const newWorks = res.data?.works || []
    if (newWorks.length < 12) hasMore.value = false
    works.value = [...works.value, ...newWorks]
  } catch (e) {
    currentPage.value--
  } finally {
    loadingMore.value = false
  }
}

onMounted(async () => {
  const user = localStorage.getItem('user')
  if (user) {
    try { const u = JSON.parse(user); userInitial.value = u.username?.[0]?.toUpperCase() || 'U'; currentUserId.value = u.id } catch(e) {}
  }

  try {
    const [worksRes, hotRes] = await Promise.all([
      api.get('/works', { params: { page: 1, page_size: 20 } }),
      api.get('/recommend/hot', { params: { limit: 10 } }),
    ])
    works.value = worksRes.data?.works || []
    hotWorks.value = hotRes.data || []
    featured.value = hotRes.data?.slice(0, 3) || works.value.slice(0, 3)
  } catch (e) {
    works.value = []
    hotWorks.value = []
    featured.value = []
  }
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: #0a0c10;
  padding-bottom: 40px;
}

.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

/* Nav */
.home-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(10,12,16,0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(201,169,110,0.08);
}
.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
}
.logo {
  font-size: 20px;
  font-weight: 700;
  color: #c9a96e;
  letter-spacing: 4px;
}
.nav-right { display: flex; align-items: center; gap: 12px; }
.nav-link {
  color: #8a8678;
  text-decoration: none;
  font-size: 18px;
  padding: 8px;
}
.nav-btn {
  padding: 8px 20px;
  background: #c9a96e;
  color: #0a0c10;
  border-radius: 20px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
}
.nav-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #c9a96e;
  color: #0a0c10;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  text-decoration: none;
}

/* Hero */
.hero-section { padding: 24px 0 16px; }
.hero-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  min-height: 240px;
  cursor: pointer;
  border: 1px solid rgba(201,169,110,0.1);
}
.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1a1e2e 0%, #0f1118 100%);
}
.hero-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 70% 30%, rgba(201,169,110,0.08) 0%, transparent 60%),
    linear-gradient(to top, rgba(10,12,16,0.95) 0%, transparent 50%);
}
.hero-content {
  position: relative;
  z-index: 2;
  padding: 32px;
  max-width: 70%;
}
.hero-badge {
  display: inline-block;
  padding: 4px 12px;
  background: #c9a96e;
  color: #0a0c10;
  font-size: 11px;
  font-weight: 700;
  border-radius: 4px;
  margin-bottom: 12px;
}
.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: #e8e4dc;
  margin-bottom: 8px;
}
.hero-author { font-size: 14px; color: #8a8678; margin-bottom: 12px; }
.hero-desc { font-size: 13px; color: #555248; line-height: 1.6; margin-bottom: 16px; }
.hero-stats { display: flex; gap: 20px; font-size: 12px; color: #555248; }

/* Categories */
.categories-section { padding: 8px 0 20px; }
.categories-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.category-chip {
  flex-shrink: 0;
  padding: 8px 20px;
  background: #12151c;
  border: 1px solid rgba(201,169,110,0.08);
  border-radius: 20px;
  font-size: 13px;
  color: #8a8678;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}
.category-chip:hover, .category-chip.active {
  background: rgba(201,169,110,0.1);
  border-color: rgba(201,169,110,0.25);
  color: #c9a96e;
}

/* Sections */
.section { margin-bottom: 32px; }
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #e8e4dc;
}
.section-more {
  font-size: 13px;
  color: #555248;
  text-decoration: none;
}
.section-more:hover { color: #c9a96e; }

/* Horizontal Scroll */
.horizontal-scroll {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 8px;
}
.work-card-h {
  flex-shrink: 0;
  width: 140px;
  cursor: pointer;
  transition: transform 0.2s;
}
.work-card-h:hover { transform: translateY(-4px); }
.card-cover {
  height: 200px;
  border-radius: 12px;
  margin-bottom: 10px;
  overflow: hidden;
}
.card-cover .cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-info h3 {
  font-size: 14px;
  color: #e8e4dc;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-author {
  font-size: 12px;
  color: #8a8678;
  margin-bottom: 6px;
}
.card-tags { display: flex; gap: 4px; }
.tag {
  padding: 2px 8px;
  background: rgba(201,169,110,0.1);
  border-radius: 4px;
  font-size: 10px;
  color: #8a7445;
}

/* Works Grid */
.works-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.work-card {
  background: #12151c;
  border: 1px solid rgba(201,169,110,0.08);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s;
}
.work-card:hover {
  border-color: rgba(201,169,110,0.25);
  transform: translateY(-3px);
}
.work-cover {
  height: 130px;
  position: relative;
  overflow: hidden;
}
.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.work-rank {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 24px;
  height: 24px;
  background: #c9a96e;
  color: #0a0c10;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}
.work-info { padding: 14px; }
.work-title {
  font-size: 14px;
  font-weight: 600;
  color: #e8e4dc;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.work-author {
  font-size: 12px;
  color: #8a8678;
  margin-bottom: 8px;
}
.work-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #555248;
}
.work-meta span {
  padding: 2px 8px;
  background: rgba(201,169,110,0.08);
  border-radius: 4px;
  color: #8a7445;
}

/* Load More */
.load-more { padding: 24px 0 40px; text-align: center; }
.load-btn {
  padding: 12px 48px;
  background: #12151c;
  border: 1px solid rgba(201,169,110,0.15);
  border-radius: 8px;
  color: #c9a96e;
  font-size: 14px;
  cursor: pointer;
}
.load-btn:disabled { opacity: 0.5; }
.load-btn:hover:not(:disabled) { background: rgba(201,169,110,0.1); }

@media (max-width: 768px) {
  .works-grid { grid-template-columns: repeat(2, 1fr); }
  .hero-content { max-width: 100%; padding: 24px; }
  .hero-title { font-size: 22px; }
}
</style>
