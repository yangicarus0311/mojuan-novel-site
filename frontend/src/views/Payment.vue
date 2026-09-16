<template>
  <div class="payment-page">
    <header class="page-header">
      <div class="container">
        <button class="back-btn" @click="$router.push('/')">← 返回</button>
        <h1>👑 会员中心</h1>
      </div>
    </header>
    <div class="container">
      <p v-if="loading" role="status" class="payment-message">正在加载会员信息...</p>
      <p v-if="serviceMessage" class="payment-message">{{ serviceMessage }}</p>
      <p v-if="statusMessage" role="status" class="payment-message">{{ statusMessage }}</p>
      <p v-if="errorMessage" role="alert" class="payment-message">{{ errorMessage }} <button @click="loadData">重试</button></p>
      <!-- 用户状态 -->
      <div class="status-card">
        <div class="status-left">
          <span class="status-avatar">{{ userName?.[0]?.toUpperCase() || 'U' }}</span>
          <div class="status-info">
            <h3>{{ userName || '用户' }}</h3>
            <span class="vip-badge" :class="{ active: subscriptionStatus.is_vip }">
              {{ subscriptionStatus.is_vip ? '👑 VIP会员' : '普通用户' }}
            </span>
            <p class="expire" v-if="subscriptionStatus.is_vip && subscriptionStatus.expire_date">
              到期: {{ formatDate(subscriptionStatus.expire_date) }}
            </p>
          </div>
        </div>
        <div class="balance-box">
          <span class="balance-label">余额</span>
          <span class="balance-amount">¥{{ balance.toFixed(2) }}</span>
          <button class="recharge-btn" @click="showRecharge = true" :disabled="!paymentsEnabled || loading">{{ paymentsEnabled ? '充值' : '充值暂未开放' }}</button>
        </div>
      </div>

      <!-- 套餐列表 -->
      <section class="section">
        <h2>会员套餐</h2>
        <div class="plans-grid">
          <div class="plan-card" v-for="plan in plans" :key="plan.id"
            :class="{ selected: selectedPlan === plan.id }" @click="selectedPlan = plan.id">
            <div class="plan-name">{{ plan.name }}</div>
            <div class="plan-price"><span class="currency">¥</span>{{ plan.price.toFixed(0) }}</div>
            <div class="plan-duration">/ {{ plan.duration_days }}天</div>
            <p class="plan-desc">{{ plan.description }}</p>
            <ul class="plan-benefits">
              <li>✓ VIP章节免费阅读</li>
              <li>✓ 阅读进度同步</li>
            </ul>
            <button class="subscribe-btn" :class="{ active: selectedPlan === plan.id }"
              @click.stop="subscribe(plan.id)" :disabled="!paymentsEnabled || busy || loading">
              {{ paymentsEnabled ? '立即开通' : '暂未开放' }}
            </button>
          </div>
        </div>
      </section>
    </div>

    <!-- 充值弹窗 -->
    <div class="modal-overlay" v-if="showRecharge" @click.self="showRecharge = false">
      <div class="modal-card">
        <h3>充值余额</h3>
        <div class="amount-grid">
          <button v-for="a in [10,30,50,100,200,500]" :key="a"
            :class="{ selected: rechargeAmount === a }" @click="rechargeAmount = a">¥{{ a }}</button>
        </div>
        <input type="number" v-model.number="rechargeAmount" class="amount-input" min="1" max="10000">
        <div class="modal-actions">
          <button class="cancel" @click="showRecharge = false">取消</button>
          <button class="confirm" @click="doRecharge">确认充值</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
const plans = ref([])
const selectedPlan = ref(null)
const subscriptionStatus = ref({ is_vip: false })
const balance = ref(0)
const userName = ref('')
const showRecharge = ref(false)
const rechargeAmount = ref(50)
const paymentsEnabled = ref(false)
const loading = ref(false)
const busy = ref(false)
const serviceMessage = ref('')
const errorMessage = ref('')
const statusMessage = ref('')
const formatDate = (d) => d ? new Date(d).toLocaleDateString('zh-CN') : ''
async function loadData() {
  loading.value = true
  errorMessage.value = ''
  const results = await Promise.allSettled([
    api.get('/payment/plans'), api.get('/payment/subscription/status'),
    api.get('/payment/balance'), api.get('/payment/capabilities')
  ])
  if (results[0].status === 'fulfilled') plans.value = results[0].value.data
  if (results[1].status === 'fulfilled') subscriptionStatus.value = results[1].value.data
  if (results[2].status === 'fulfilled') balance.value = results[2].value.data.balance
  if (results[3].status === 'fulfilled') {
    paymentsEnabled.value = results[3].value.data.external_payments_enabled
    serviceMessage.value = results[3].value.data.message
  }
  if (results.some(result => result.status === 'rejected')) errorMessage.value = '部分会员信息加载失败，请重试。'
  loading.value = false
}
async function checkout(path, params) {
  if (!paymentsEnabled.value || busy.value) return
  busy.value = true
  errorMessage.value = ''
  try {
    const { data } = await api.post(path, null, { params })
    statusMessage.value = data.status === 'paid' ? '支付已确认。' : '订单已创建，等待支付确认。'
    showRecharge.value = false
    await loadData()
  } catch (error) { errorMessage.value = error.response?.data?.detail || '提交失败，请稍后重试。' }
  finally { busy.value = false }
}
const subscribe = planId => checkout('/payment/subscribe', { plan_id: planId, payment_method: 'alipay' })
const doRecharge = () => checkout('/payment/recharge', { amount: rechargeAmount.value, payment_method: 'alipay' })
onMounted(() => {
  try { userName.value = JSON.parse(localStorage.getItem('user') || '{}').username || '' } catch {}
  void loadData()
})
</script>
<style scoped>
.payment-page { min-height: 100vh; background: #0a0c10; padding-bottom: 80px; }
.page-header { padding: 24px 0; border-bottom: 1px solid rgba(201,169,110,0.08); }
.container { max-width: 800px; margin: 0 auto; padding: 0 24px; }
.back-btn { background: none; border: none; color: #8a8678; font-size: 14px; cursor: pointer; margin-bottom: 8px; }
h1 { font-size: 22px; color: #e8e4dc; }
h2 { font-size: 18px; color: #e8e4dc; margin-bottom: 16px; }
.status-card { display: flex; align-items: center; justify-content: space-between; background: #12151c; border: 1px solid rgba(201,169,110,0.08); border-radius: 12px; padding: 20px; margin: 20px 0; }
.status-left { display: flex; align-items: center; gap: 16px; }
.status-avatar { width: 48px; height: 48px; border-radius: 50%; background: #c9a96e; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; color: #0a0c10; }
.status-info h3 { font-size: 16px; color: #e8e4dc; }
.vip-badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; background: #333; color: #666; margin-top: 4px; }
.vip-badge.active { background: linear-gradient(135deg, #ffd700, #ff9500); color: #333; }
.expire { font-size: 12px; color: #555248; margin-top: 4px; }
.balance-box { text-align: right; }
.balance-label { display: block; font-size: 12px; color: #555248; }
.balance-amount { display: block; font-size: 28px; font-weight: 700; color: #c9a96e; }
.recharge-btn { margin-top: 8px; padding: 6px 16px; background: #c9a96e; border: none; border-radius: 6px; color: #0a0c10; font-size: 13px; cursor: pointer; }
.plans-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 16px; }
.plan-card { background: #12151c; border: 2px solid rgba(201,169,110,0.08); border-radius: 16px; padding: 24px; cursor: pointer; transition: all 0.25s; }
.plan-card:hover { transform: translateY(-3px); }
.plan-card.selected { border-color: #c9a96e; }
.plan-name { font-size: 18px; font-weight: 600; color: #e8e4dc; margin-bottom: 8px; }
.plan-price { font-size: 36px; font-weight: 700; color: #c9a96e; }
.currency { font-size: 18px; }
.plan-duration { font-size: 13px; color: #555248; margin-bottom: 12px; }
.plan-desc { font-size: 13px; color: #8a8678; margin-bottom: 16px; }
.plan-benefits { list-style: none; padding: 0; margin-bottom: 20px; }
.plan-benefits li { padding: 4px 0; font-size: 13px; color: #555248; }
.subscribe-btn { width: 100%; padding: 12px; border: 1px solid #c9a96e; border-radius: 8px; background: transparent; color: #c9a96e; font-size: 15px; cursor: pointer; }
.subscribe-btn.active { background: #c9a96e; color: #0a0c10; font-weight: 600; }
.subscribe-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal-card { background: #1a1d24; border: 1px solid rgba(201,169,110,0.15); border-radius: 16px; padding: 32px; width: 90%; max-width: 400px; }
.modal-card h3 { font-size: 20px; color: #e8e4dc; margin-bottom: 20px; }
.amount-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.amount-grid button { padding: 10px 20px; background: #12151c; border: 1px solid rgba(201,169,110,0.1); border-radius: 8px; color: #8a8678; cursor: pointer; }
.amount-grid button.selected { border-color: #c9a96e; color: #c9a96e; }
.amount-input { width: 100%; padding: 12px; background: #12151c; border: 1px solid rgba(201,169,110,0.1); border-radius: 8px; color: #e8e4dc; font-size: 16px; }
.modal-actions { display: flex; gap: 12px; margin-top: 20px; }
.modal-actions button { flex: 1; padding: 12px; border-radius: 8px; font-size: 14px; cursor: pointer; }
.cancel { background: transparent; border: 1px solid rgba(201,169,110,0.15); color: #8a8678; }
.confirm { background: #c9a96e; border: none; color: #0a0c10; font-weight: 600; }
.payment-message { padding: 14px 0; color: #c9bfae; line-height: 1.6; }
.recharge-btn:disabled { opacity: .55; cursor: not-allowed; }
</style>
