<template>
  <div class="profile-page">
    <header class="page-header">
      <div class="container">
        <button class="back-btn" @click="$router.push('/')">← 返回</button>
      </div>
    </header>
    <div class="container" v-if="profile">
      <div class="profile-header">
        <div class="profile-avatar">{{ profile.username?.[0]?.toUpperCase() || '?' }}</div>
        <div class="profile-info">
          <h1>{{ profile.username }}</h1>
          <p class="profile-bio">{{ profile.bio || '这个人很懒，什么都没写...' }}</p>
          <div class="profile-stats">
            <span class="stat-item"><strong>{{ profile.follower_count }}</strong> 粉丝</span>
            <span class="stat-item"><strong>{{ profile.following_count }}</strong> 关注</span>
            <span class="stat-item"><strong>{{ profile.review_count }}</strong> 书评</span>
          </div>
        </div>
        <button v-if="isLoggedIn && profile.id !== currentUserId" class="follow-btn"
          :class="{ following: profile.is_following }" @click="toggleFollow">
          {{ profile.is_following ? '已关注' : '关注' }}
        </button>
      </div>
      <div class="section">
        <h2 class="section-title">书评</h2>
        <div class="review-list">
          <div class="review-card" v-for="r in reviews" :key="r.id">
            <h3>{{ r.work_title || '作品' }}</h3>
            <div class="stars">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5-r.rating) }}</div>
            <p>{{ r.content?.slice(0, 200) }}</p>
          </div>
          <div class="empty-state" v-if="!reviews.length"><p>暂无书评</p></div>
        </div>
      </div>
    </div>
    <div class="loading" v-else><p>加载中...</p></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
const route = useRoute()
const profile = ref(null)
const reviews = ref([])
const isLoggedIn = ref(!!localStorage.getItem('token'))
const currentUserId = ref(null)
const toggleFollow = async () => {
  try {
    if (profile.value.is_following) {
      await api.delete(`/social/unfollow/${route.params.id}`)
      profile.value.is_following = false
      profile.value.follower_count--
    } else {
      await api.post(`/social/follow/${route.params.id}`)
      profile.value.is_following = true
      profile.value.follower_count++
    }
  } catch(e) {}
}
onMounted(async () => {
  try {
    const user = localStorage.getItem('user')
    if (user) currentUserId.value = JSON.parse(user).id
    const r = await api.get(`/social/profile/${route.params.id}`)
    profile.value = r.data
    const rev = await api.get('/social/reviews', { params: { user_id: route.params.id } })
    reviews.value = rev.data || []
  } catch(e) {}
})
</script>
<style scoped>
.profile-page { min-height: 100vh; background: #0a0c10; }
.page-header { border-bottom: 1px solid rgba(201,169,110,0.08); }
.container { max-width: 800px; margin: 0 auto; padding: 0 24px; }
.back-btn { background: none; border: none; color: #8a8678; font-size: 14px; cursor: pointer; padding: 16px 0; }
.profile-header { display: flex; align-items: center; gap: 20px; padding: 32px 0; }
.profile-avatar { width: 72px; height: 72px; border-radius: 50%; background: #c9a96e; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 700; color: #0a0c10; }
.profile-info { flex: 1; }
.profile-info h1 { font-size: 22px; color: #e8e4dc; }
.profile-bio { font-size: 14px; color: #555248; margin-top: 4px; }
.profile-stats { display: flex; gap: 20px; margin-top: 12px; font-size: 14px; color: #8a8678; }
.profile-stats strong { color: #e8e4dc; }
.follow-btn { padding: 8px 24px; border-radius: 20px; font-size: 14px; cursor: pointer; border: 1px solid #c9a96e; background: transparent; color: #c9a96e; }
.follow-btn.following { border-color: #555248; color: #555248; }
.section-title { font-size: 18px; color: #e8e4dc; margin-bottom: 16px; }
.review-list { display: flex; flex-direction: column; gap: 12px; padding-bottom: 60px; }
.review-card { background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 12px; padding: 16px 20px; }
.review-card h3 { font-size: 15px; color: #e8e4dc; margin-bottom: 4px; }
.stars { font-size: 14px; color: #ffb300; margin-bottom: 8px; }
.review-card p { font-size: 14px; color: #8a8678; line-height: 1.6; }
.empty-state { text-align: center; padding: 40px; color: #555248; }
.loading { min-height: 100vh; display: flex; align-items: center; justify-content: center; color: #555248; }
</style>
