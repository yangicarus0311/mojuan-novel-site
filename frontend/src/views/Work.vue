<template>
  <div class="work-page" v-if="work">
    <!-- 作品头部 -->
    <header class="work-header">
      <div class="container">
        <div class="header-top">
          <button class="back-btn" @click="$router.push('/')">← 返回</button>
        </div>
        <div class="work-hero">
          <div class="work-cover" :style="{ background: coverGradient }">
            <span class="status-badge" v-if="work.status === 'completed'">完本</span>
          </div>
          <div class="work-info">
            <h1>{{ work.title }}</h1>
            <p class="work-author">{{ work.author }}</p>
            <div class="work-tags">
              <span class="tag">{{ work.category }}</span>
              <span class="tag status" :class="work.status">{{ statusText }}</span>
            </div>
            <p class="work-desc">{{ work.description }}</p>
            <div class="work-stats">
              <div class="stat"><span class="num">{{ (work.word_count || 0).toLocaleString() }}</span><span class="label">字数</span></div>
              <div class="stat"><span class="num">{{ chapterList.length }}</span><span class="label">章节</span></div>
              <div class="stat"><span class="num">{{ (work.clicks || 0).toLocaleString() }}</span><span class="label">阅读</span></div>
            </div>
            <div class="work-actions">
              <button class="btn-primary" @click="startRead">📖 开始阅读</button>
              <button class="btn-secondary" :class="{ active: isInShelf }" @click="toggleShelf">
                {{ isInShelf ? '✅ 已收藏' : '📥 加入书架' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="container work-body">
      <!-- 章节目录 -->
      <section class="section">
        <div class="section-header">
          <h2 class="section-title">📑 章节目录</h2>
        </div>
        <div class="chapter-list">
          <div v-for="(ch, idx) in chapterList" :key="ch.id" class="chapter-item" @click="readChapter(ch.id)">
            <span class="chapter-num">{{ idx + 1 }}</span>
            <span class="chapter-title-text">{{ ch.title }}</span>
            <span class="chapter-date">{{ formatDate(ch.created_at) }}</span>
          </div>
          <div class="chapter-empty" v-if="!chapterList.length">
            <p>暂无章节</p>
          </div>
        </div>
      </section>

      <!-- 书评区 -->
      <section class="section" v-if="isLoggedIn">
        <div class="section-header">
          <h2 class="section-title">💬 写书评</h2>
        </div>
        <div class="review-form" v-if="!showReviewForm" @click="showReviewForm = true">
          <span class="placeholder">写下你对这本书的看法...</span>
        </div>
        <div class="review-form active" v-else>
          <div class="star-rating">
            <span v-for="s in 5" :key="s" class="star" :class="{ active: s <= newRating }" @click="newRating = s">★</span>
            <span class="rating-text">{{ ratingText }}</span>
          </div>
          <textarea v-model="newReview" placeholder="写下你的书评..." rows="4"></textarea>
          <div class="review-actions">
            <button class="btn-cancel" @click="cancelReview">取消</button>
            <button class="btn-submit" @click="submitReview" :disabled="!newReview.trim()">发布</button>
          </div>
        </div>
      </section>

      <!-- 书评列表 -->
      <section class="section">
        <div class="section-header">
          <h2 class="section-title">📝 书评 ({{ reviews.length }})</h2>
        </div>
        <div class="reviews-list">
          <div class="review-card" v-for="r in reviews" :key="r.id">
            <div class="review-user">
              <span class="review-avatar">{{ r.username?.[0]?.toUpperCase() || '?' }}</span>
              <div class="review-user-info">
                <span class="review-username">{{ r.username || '匿名' }}</span>
                <span class="review-stars">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
              </div>
              <span class="review-date">{{ formatDate(r.created_at) }}</span>
            </div>
            <div class="review-content">
              <h4 v-if="r.title" class="review-title">{{ r.title }}</h4>
              <p>{{ r.content }}</p>
            </div>
            <div class="review-footer">
              <button class="like-btn" :class="{ liked: r.is_liked }" @click="toggleLike(r)">
                {{ r.is_liked ? '❤️' : '🤍' }} {{ r.likes }}
              </button>
            </div>
          </div>
          <div class="reviews-empty" v-if="!reviews.length">
            <p>暂无书评，来写第一条吧</p>
          </div>
        </div>
      </section>

      <!-- 类似推荐 -->
      <section class="section" v-if="similarWorks.length">
        <div class="section-header">
          <h2 class="section-title">📎 猜你喜欢</h2>
        </div>
        <div class="horizontal-scroll">
          <div class="mini-card" v-for="w in similarWorks" :key="w.id" @click="goWork(w.id)">
            <div class="mini-cover" :style="{ background: getGradient(w.id) }"></div>
            <div class="mini-info">
              <h4>{{ w.title }}</h4>
              <p>{{ w.author }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>

  <!-- 加载中 -->
  <div class="loading-page" v-else>
    <p v-if="!loadError">加载中...</p><div v-else role="alert">{{ loadError }} <button @click="loadWork">重试</button></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const work = ref(null)
const loadError = ref('')
const chapterList = ref([])
const reviews = ref([])
const similarWorks = ref([])
const isInShelf = ref(false)
const isLoggedIn = ref(!!localStorage.getItem('token'))

const showReviewForm = ref(false)
const newReview = ref('')
const newRating = ref(5)

const coverGradient = computed(() => {
  const g = ['linear-gradient(135deg, #1a1e2e, #0f1118)', 'linear-gradient(135deg, #2d1f3d, #14101f)', 'linear-gradient(135deg, #1f2d30, #0f1414)']
  return g[(work.value?.id || 0) % g.length]
})

const statusText = computed(() => {
  const s = work.value?.status
  if (s === 'ongoing') return '连载中'
  if (s === 'completed') return '已完结'
  if (s === 'paused') return '暂停'
  return s
})

const ratingText = computed(() => {
  const t = ['', '很差', '较差', '还行', '推荐', '力荐']
  return t[newRating.value] || ''
})

const getGradient = (id) => {
  const g = ['linear-gradient(135deg, #1a1e2e, #0f1118)', 'linear-gradient(135deg, #2d1f3d, #14101f)', 'linear-gradient(135deg, #1f2d30, #0f1414)']
  return g[(id || 0) % g.length]
}

const formatDate = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

const startRead = async () => {
  if (!chapterList.value.length) return
  let chapterId = chapterList.value[0].id
  if (isLoggedIn.value) {
    try {
      const { data } = await api.get(`/bookshelf/progress/${work.value.id}`)
      if (chapterList.value.some(chapter => chapter.id === data.chapter_id)) chapterId = data.chapter_id
    } catch {}
  }
  router.push(`/works/${work.value.id}/chapters/${chapterId}`)
}

const readChapter = (chapterId) => {
  router.push(`/works/${work.value.id}/chapters/${chapterId}`)
}

const goWork = (id) => router.push(`/works/${id}`)

const toggleShelf = async () => {
  if (!isLoggedIn.value) { router.push('/login'); return }
  try {
    if (isInShelf.value) {
      await api.delete(`/bookshelf/${work.value.id}`)
      isInShelf.value = false
    } else {
      await api.post('/bookshelf', null, { params: { work_id: work.value.id } })
      isInShelf.value = true
    }
  } catch (e) { console.error(e) }
}

const submitReview = async () => {
  try {
    await api.post('/social/reviews', {
      work_id: work.value.id,
      rating: newRating.value,
      content: newReview.value,
      is_long: newReview.value.length > 200 ? 1 : 0
    })
    newReview.value = ''
    newRating.value = 5
    showReviewForm.value = false
    await loadReviews()
  } catch (e) { console.error('发布书评失败:', e) }
}

const cancelReview = () => {
  showReviewForm.value = false
  newReview.value = ''
  newRating.value = 5
}

const toggleLike = async (r) => {
  try {
    const res = await api.post(`/social/reviews/${r.id}/like`)
    r.is_liked = res.data.liked
    r.likes = res.data.likes
  } catch (e) { console.error(e) }
}

async function loadReviews() {
  if (!isLoggedIn.value) return
  try {
    const res = await api.get('/social/reviews', { params: { work_id: work.value.id, sort: 'created_at' } })
    reviews.value = res.data || []
  } catch (e) { reviews.value = [] }
}

async function loadSimilar() {
  try {
    const res = await api.get(`/recommend/similar/${route.params.id}`, { params: { limit: 8 } })
    similarWorks.value = res.data || []
  } catch (e) { similarWorks.value = [] }
}

async function checkShelf() {
  if (!isLoggedIn.value) return
  try {
    const res = await api.get('/bookshelf')
    const ids = (res.data || []).map(b => b.work?.id || b.work_id)
    isInShelf.value = ids.includes(parseInt(route.params.id))
  } catch (e) { }
}

async function loadWork() {
  loadError.value = ''
  try {
    const [workRes, chaptersRes] = await Promise.all([
      api.get(`/works/${route.params.id}`),
      api.get('/chapters', { params: { work_id: route.params.id } })
    ])
    work.value = workRes.data
    chapterList.value = chaptersRes.data?.chapters || []
    
    await Promise.all([
      loadReviews(),
      loadSimilar(),
      checkShelf()
    ])
  } catch (e) {
    loadError.value = '作品加载失败，请重试。'
  }
}
onMounted(loadWork)
</script>

<style scoped>
.work-page { min-height: 100vh; background: #0a0c10; padding-bottom: 60px; }
.container { max-width: 1000px; margin: 0 auto; padding: 0 24px; }

/* Header */
.work-header {
  background: linear-gradient(to bottom, #0a0c10, #12151c);
  padding: 20px 0 40px;
}
.header-top { margin-bottom: 24px; }
.back-btn { background: none; border: none; color: #8a8678; font-size: 14px; cursor: pointer; }
.back-btn:hover { color: #c9a96e; }

.work-hero { display: flex; gap: 40px; }
.work-cover {
  width: 220px; height: 300px; border-radius: 12px; flex-shrink: 0;
  position: relative; border: 1px solid rgba(201,169,110,0.08);
}
.status-badge {
  position: absolute; top: 12px; right: 12px;
  padding: 4px 10px; background: #4CAF50; color: white;
  border-radius: 12px; font-size: 11px; font-weight: 600;
}

.work-info { flex: 1; }
.work-info h1 { font-size: 28px; color: #e8e4dc; margin-bottom: 8px; }
.work-author { font-size: 15px; color: #8a8678; margin-bottom: 12px; }
.work-tags { display: flex; gap: 8px; margin-bottom: 16px; }
.tag {
  padding: 4px 12px; background: rgba(201,169,110,0.1);
  border-radius: 4px; font-size: 12px; color: #c9a96e;
}
.tag.status.completed { background: rgba(76,175,80,0.15); color: #4CAF50; }
.tag.status.ongoing { background: rgba(33,150,243,0.15); color: #42a5f5; }

.work-desc {
  font-size: 14px; color: #555248; line-height: 1.8;
  margin-bottom: 20px; max-width: 600px;
}
.work-stats { display: flex; gap: 32px; margin-bottom: 24px; }
.stat { display: flex; flex-direction: column; }
.stat .num { font-size: 22px; font-weight: 700; color: #c9a96e; }
.stat .label { font-size: 12px; color: #555248; }

.work-actions { display: flex; gap: 12px; }
.btn-primary {
  padding: 12px 36px; background: #c9a96e; border: none;
  border-radius: 8px; color: #0a0c10; font-size: 15px; font-weight: 600; cursor: pointer;
}
.btn-secondary {
  padding: 12px 24px; background: transparent; border: 1px solid rgba(201,169,110,0.25);
  border-radius: 8px; color: #c9a96e; font-size: 14px; cursor: pointer;
}
.btn-secondary.active { background: rgba(201,169,110,0.1); }

/* Body */
.work-body { padding: 32px 24px; }
.section { margin-bottom: 40px; }
.section-header { margin-bottom: 16px; }
.section-title { font-size: 18px; font-weight: 600; color: #e8e4dc; }

/* Chapter List */
.chapter-list {
  background: #12151c; border: 1px solid rgba(201,169,110,0.08);
  border-radius: 12px; overflow: hidden;
}
.chapter-item {
  display: flex; align-items: center; padding: 14px 20px;
  border-bottom: 1px solid rgba(201,169,110,0.05); cursor: pointer;
  transition: background 0.2s;
}
.chapter-item:last-child { border-bottom: none; }
.chapter-item:hover { background: rgba(201,169,110,0.05); }
.chapter-num { width: 40px; font-size: 13px; color: #555248; }
.chapter-title-text { flex: 1; font-size: 14px; color: #e8e4dc; }
.chapter-date { font-size: 12px; color: #555248; }
.chapter-empty { padding: 40px; text-align: center; color: #555248; }

/* Review Form */
.review-form {
  background: #12151c; border: 1px solid rgba(201,169,110,0.08);
  border-radius: 12px; padding: 16px 20px; cursor: pointer;
}
.review-form.active { cursor: default; }
.review-form .placeholder { color: #555248; font-size: 14px; }
.star-rating { margin-bottom: 12px; }
.star {
  font-size: 24px; color: #555248; cursor: pointer; margin-right: 4px;
}
.star.active { color: #ffb300; }
.rating-text { font-size: 13px; color: #8a8678; margin-left: 8px; }
.review-form textarea {
  width: 100%; padding: 12px; background: #0a0c10; border: 1px solid rgba(201,169,110,0.08);
  border-radius: 8px; color: #e8e4dc; font-size: 14px; resize: vertical; font-family: inherit;
}
.review-actions {
  display: flex; gap: 12px; margin-top: 12px; justify-content: flex-end;
}
.btn-cancel, .btn-submit {
  padding: 8px 20px; border-radius: 6px; font-size: 13px; cursor: pointer;
}
.btn-cancel { background: none; border: 1px solid rgba(201,169,110,0.15); color: #8a8678; }
.btn-submit { background: #c9a96e; border: none; color: #0a0c10; font-weight: 600; }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }

/* Reviews */
.reviews-list { display: flex; flex-direction: column; gap: 12px; }
.review-card {
  background: #12151c; border: 1px solid rgba(201,169,110,0.06);
  border-radius: 12px; padding: 16px 20px;
}
.review-user { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.review-avatar {
  width: 36px; height: 36px; border-radius: 50%; background: #1e2330;
  display: flex; align-items: center; justify-content: center;
  color: #c9a96e; font-weight: 700; font-size: 14px;
}
.review-user-info { flex: 1; }
.review-username { display: block; font-size: 14px; color: #e8e4dc; }
.review-stars { display: block; font-size: 12px; color: #ffb300; }
.review-date { font-size: 12px; color: #555248; }
.review-content { margin-bottom: 12px; }
.review-title { font-size: 15px; color: #e8e4dc; margin-bottom: 8px; }
.review-content p { font-size: 14px; color: #8a8678; line-height: 1.7; }
.review-footer { display: flex; justify-content: flex-end; }
.like-btn {
  background: none; border: 1px solid rgba(201,169,110,0.1);
  border-radius: 20px; padding: 6px 14px; color: #8a8678; font-size: 13px; cursor: pointer;
}
.like-btn.liked { background: rgba(255,107,107,0.1); border-color: rgba(255,107,107,0.3); color: #ff6b6b; }
.reviews-empty { text-align: center; padding: 40px; color: #555248; }

/* Similar */
.horizontal-scroll {
  display: flex; gap: 12px; overflow-x: auto;
  -webkit-overflow-scrolling: touch; scrollbar-width: none;
}
.mini-card {
  flex-shrink: 0; width: 120px; cursor: pointer;
  transition: transform 0.2s;
}
.mini-card:hover { transform: translateY(-3px); }
.mini-cover { height: 160px; border-radius: 8px; margin-bottom: 8px; }
.mini-info h4 { font-size: 13px; color: #e8e4dc; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mini-info p { font-size: 11px; color: #555248; margin-top: 2px; }

/* Loading */
.loading-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; color: #555248; }

@media (max-width: 768px) {
  .work-hero { flex-direction: column; align-items: center; text-align: center; }
  .work-cover { width: 160px; height: 220px; }
  .work-stats { justify-content: center; }
  .work-actions { justify-content: center; }
}
</style>
