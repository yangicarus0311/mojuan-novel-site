import api from './index'

// Payment API
export const paymentAPI = {
  // 获取所有支付套餐
  getPlans() {
    return api.get('/payment/plans')
  },
  
  // 订阅VIP套餐
  subscribe(planId, paymentMethod) {
    return api.post('/payment/subscribe', null, { 
      params: { plan_id: planId, payment_method: paymentMethod } 
    })
  },
  
  // 获取用户订阅状态
  getSubscriptionStatus() {
    return api.get('/payment/subscription/status')
  },
  
  // 购买单章
  purchaseChapter(workId, chapterId) {
    return api.post('/payment/chapter/purchase', null, { 
      params: { work_id: workId, chapter_id: chapterId } 
    })
  },
  
  // 充值余额
  recharge(amount, paymentMethod) {
    return api.post('/payment/recharge', null, { 
      params: { amount, payment_method: paymentMethod } 
    })
  },
  
  // 获取用户余额
  getBalance() {
    return api.get('/payment/balance')
  },
  
  // 投月票
  voteTicket(workId, ticketCount = 1) {
    return api.post('/payment/ticket/vote', null, { 
      params: { work_id: workId, ticket_count: ticketCount } 
    })
  }
}

export default paymentAPI