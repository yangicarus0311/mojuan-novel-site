import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Auth
export const authAPI = {
  register(data) { return api.post('/auth/register', data) },
  login(data) { return api.post('/auth/login', data) },
  getMe() { return api.get('/auth/me') }
}

// Works
export const worksAPI = {
  getList(params) { return api.get('/works', { params }) },
  getCategories() { return api.get('/works/categories') },
  getRankings(params) { return api.get('/works/rankings', { params }) },
  getById(id) { return api.get(`/works/${id}`) },
  search(q, page = 1, pageSize = 20) { return api.get('/works/search', { params: { q, page, page_size: pageSize } }) }
}

// Chapters
export const chaptersAPI = {
  getList(workId) { return api.get('/chapters', { params: { work_id: workId } }) },
  getById(id) { return api.get(`/chapters/${id}`) }
}

// Bookshelf
export const bookshelfAPI = {
  getList() { return api.get('/bookshelf') },
  add(workId) { return api.post('/bookshelf', null, { params: { work_id: workId } }) },
  remove(workId) { return api.delete(`/bookshelf/${workId}`) }
}

// Highlights
export const highlightsAPI = {
  getList(params) { return api.get('/highlights', { params }) },
  create(workId, data) { return api.post('/highlights', data, { params: { work_id: workId } }) },
  update(id, data) { return api.put(`/highlights/${id}`, data) },
  remove(id) { return api.delete(`/highlights/${id}`) },
  getNotebook() { return api.get('/highlights/notebook') }
}

// Reading
export const readingAPI = {
  heartbeat(data) { return api.post('/reading/heartbeat', data) },
  getStats(params) { return api.get('/reading/stats', { params }) }
}

// Social
export const socialAPI = {
  follow(userId) { return api.post(`/social/follow/${userId}`) },
  unfollow(userId) { return api.delete(`/social/unfollow/${userId}`) },
  getFollowers(userId) { return api.get('/social/followers', { params: { user_id: userId } }) },
  getFollowing(userId) { return api.get('/social/following', { params: { user_id: userId } }) },
  getReviews(params) { return api.get('/social/reviews', { params }) },
  createReview(data) { return api.post('/social/reviews', data) },
  likeReview(reviewId) { return api.post(`/social/reviews/${reviewId}/like`) },
  deleteReview(reviewId) { return api.delete(`/social/reviews/${reviewId}`) },
  getFeed(params) { return api.get('/social/feed', { params }) },
  getProfile(userId) { return api.get(`/social/profile/${userId}`) }
}

// Recommendations
export const recommendAPI = {
  getPersonalized(params) { return api.get('/recommend/personalized', { params }) },
  getSimilar(workId, params) { return api.get(`/recommend/similar/${workId}`, { params }) },
  getHot(params) { return api.get('/recommend/hot', { params }) },
  getNew(params) { return api.get('/recommend/new', { params }) },
  getTrending(params) { return api.get('/recommend/trending', { params }) }
}

// Admin
export const adminAPI = {
  getStats() { return api.get('/admin/stats') },
  getUsers(page = 1, pageSize = 20) { return api.get('/admin/users', { params: { page, page_size: pageSize } }) },
  getWorks(page = 1, pageSize = 20) { return api.get('/admin/works', { params: { page, page_size: pageSize } }) },
  createWork(data) { return api.post('/admin/works', null, { params: data }) },
  deleteWork(id) { return api.delete(`/admin/works/${id}`) }
}

// Payment
export const paymentAPI = {
  getPlans() { return api.get('/payment/plans') },
  subscribe(planId, paymentMethod) { return api.post('/payment/subscribe', null, { params: { plan_id: planId, payment_method: paymentMethod } }) },
  getSubscriptionStatus() { return api.get('/payment/subscription/status') },
  purchaseChapter(workId, chapterId) { return api.post('/payment/chapter/purchase', null, { params: { work_id: workId, chapter_id: chapterId } }) },
  recharge(amount, paymentMethod) { return api.post('/payment/recharge', null, { params: { amount, payment_method: paymentMethod } }) },
  getBalance() { return api.get('/payment/balance') },
  voteTicket(workId, ticketCount = 1) { return api.post('/payment/ticket/vote', null, { params: { work_id: workId, ticket_count: ticketCount } }) }
}
