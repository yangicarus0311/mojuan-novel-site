<template>
  <div id="app-root">
    <router-view />
    <!-- 底部导航 (仅主页面显示) -->
    <nav class="bottom-nav" v-if="showBottomNav">
      <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
        <span class="nav-icon">🏠</span>
        <span class="nav-label">首页</span>
      </router-link>
      <router-link to="/feed" class="nav-item" :class="{ active: $route.path === '/feed' }">
        <span class="nav-icon">🌊</span>
        <span class="nav-label">动态</span>
      </router-link>
      <router-link to="/bookshelf" class="nav-item" :class="{ active: $route.path === '/bookshelf' }">
        <span class="nav-icon">📚</span>
        <span class="nav-label">书架</span>
      </router-link>
      <router-link to="/stats" class="nav-item" :class="{ active: $route.path === '/stats' }">
        <span class="nav-icon">📊</span>
        <span class="nav-label">统计</span>
      </router-link>
      <router-link to="/payment" class="nav-item" :class="{ active: $route.path === '/payment' }">
        <span class="nav-icon">👑</span>
        <span class="nav-label">会员</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const noNavPages = ['/login', '/register', '/admin']
const showBottomNav = computed(() => {
  return !noNavPages.some(p => route.path.startsWith(p)) && !route.path.includes('/chapters/')
})
</script>

<style>
/* Global Reset */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif; background: #0a0c10; color: #e8e4dc; overflow-x: hidden; }
a { color: inherit; text-decoration: none; }
button { font-family: inherit; }
input, textarea, select { font-family: inherit; }
::selection { background: rgba(201,169,110,0.3); color: #e8e4dc; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(201,169,110,0.15); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(201,169,110,0.3); }

/* Bottom Navigation */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: rgba(10,12,16,0.95);
  backdrop-filter: blur(12px);
  border-top: 1px solid rgba(201,169,110,0.08);
  z-index: 200;
  padding: 6px 0;
  padding-bottom: max(6px, env(safe-area-inset-bottom));
}
.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 4px 0;
  color: #555248;
  text-decoration: none;
  transition: color 0.2s;
}
.nav-item.active { color: #c9a96e; }
.nav-icon { font-size: 20px; }
.nav-label { font-size: 10px; }
</style>
