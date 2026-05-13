<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <h2 class="admin-logo">⚙ 管理后台</h2>
      <nav class="admin-nav">
        <router-link to="/admin" class="nav-link" exact-active-class="active">📊 概览</router-link>
        <router-link to="/admin/works" class="nav-link" active-class="active">📚 作品管理</router-link>
        <router-link to="/admin/users" class="nav-link" active-class="active">👥 用户管理</router-link>
        <router-link to="/" class="nav-link exit">← 返回前台</router-link>
      </nav>
    </aside>
    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>
<style scoped>
.admin-layout { display: flex; min-height: 100vh; background: #0a0c10; }
.admin-sidebar { width: 220px; background: #12151c; border-right: 1px solid rgba(201,169,110,0.08); padding: 24px 0; }
.admin-logo { font-size: 16px; color: #c9a96e; padding: 0 24px; margin-bottom: 32px; }
.admin-nav { display: flex; flex-direction: column; }
.nav-link { padding: 12px 24px; color: #8a8678; text-decoration: none; font-size: 14px; transition: all 0.2s; }
.nav-link:hover { background: rgba(201,169,110,0.05); color: #c9a96e; }
.nav-link.active { background: rgba(201,169,110,0.1); color: #c9a96e; border-right: 2px solid #c9a96e; }
.nav-link.exit { margin-top: 40px; color: #555248; font-size: 13px; }
.admin-content { flex: 1; padding: 32px; }
</style>
