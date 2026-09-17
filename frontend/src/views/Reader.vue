<template>
  <div class="reader-page" :style="readerContainerStyle">
    <!-- 顶部导航栏 -->
    <transition name="slide-down">
      <header class="reader-header" v-show="showHeader" @click.self="toggleHeader">
        <div class="header-inner">
          <button class="icon-btn back-btn" @click="goBack">←</button>
          <div class="header-info">
            <span class="work-title">{{ workTitle }}</span>
            <span class="chapter-title">{{ chapter?.title }}</span>
          </div>
          <div class="header-right">
            <span v-if="readingMode === 'pagination'" class="page-number">{{ currentPage + 1 }} / {{ totalPages }} 页</span>
            <span class="progress-text">{{ progressPercent }}%</span>
            <button class="icon-btn menu-btn" @click.stop="showMenu = !showMenu">☰</button>
          </div>
        </div>
      </header>
    </transition>

    <!-- 阅读主体 -->
    <main class="reader-main" ref="readerMain" @click="toggleHeader" @touchstart="onTouchStart" @touchend="onTouchEnd">
      <div v-if="loading" class="reader-status" role="status">正在加载章节...</div>
      <div v-else-if="loadError" class="reader-status" role="alert">
        <p>{{ loadError }}</p><button @click.stop="loadReader">重试</button>
        <button @click.stop="goBack">返回目录</button>
      </div>
      <!-- 翻页模式 -->
      <template v-else-if="chapter && readingMode === 'pagination'">
        <div class="page-container" ref="pageContainer">
          <div class="page-content" ref="pageText" :style="pageStyle">{{ currentPageContent }}</div>
        </div>
        <!-- 翻页热区 -->
        <div class="page-hotspots">
          <div class="hotspot prev" @click="goPrevPage">‹</div>
          <div class="hotspot center" @click="toggleHeader">·</div>
          <div class="hotspot next" @click="goNextPage">›</div>
        </div>
      </template>
      
      <!-- 滚动模式 -->
      <template v-else-if="chapter">
        <article class="scroll-content" ref="scrollContent" :style="scrollStyle" @scroll.passive="onScroll">
          <h2 class="chapter-name">{{ chapter?.title }}</h2>
          <div class="chapter-text" ref="chapterText" @mouseup="onTextSelect" @touchend="onTextSelectTouch">
            {{ chapter?.content }}
          </div>
        </article>
        <!-- 滚动进度条 -->
        <div class="scroll-progress" @click="onProgressClick">
          <div class="scroll-progress-bar" :style="{ height: scrollPercent + '%' }"></div>
        </div>
      </template>
    </main>

    <!-- 底部工具栏 -->
    <transition name="slide-up">
      <footer class="reader-footer" v-show="showHeader">
        <div class="footer-inner">
          <div class="footer-chapter-nav">
            <button class="nav-btn" :disabled="!prevChapterId" @click.stop="goPrevChapter">上一章</button>
            <button class="nav-btn" :disabled="!nextChapterId" @click.stop="goNextChapter">下一章</button>
          </div>
          <div class="footer-tools">
            <button class="tool-btn" :class="{ active: readingMode === 'pagination' }" @click.stop="readingMode = 'pagination'">📖</button>
            <button class="tool-btn" :class="{ active: readingMode === 'scroll' }" @click.stop="readingMode = 'scroll'">📄</button>
            <button class="tool-btn" @click.stop="showSettings = !showSettings">⚙</button>
            <button class="tool-btn highlight-notebook-btn" @click.stop="showNotebook = true">📝</button>
          </div>
        </div>
      </footer>
    </transition>

    <!-- 阅读设置面板 -->
    <transition name="popup">
      <div class="settings-panel" v-if="showSettings">
        <div class="settings-header">
          <h3>阅读设置</h3>
          <button class="close-btn" @click="showSettings = false">✕</button>
        </div>
        <div class="settings-body">
          <!-- 字号 -->
          <div class="setting-row">
            <span class="setting-label">字号</span>
            <div class="setting-control">
              <button @click="adjustFontSize(-2)">A−</button>
              <span class="size-value">{{ fontSize }}</span>
              <button @click="adjustFontSize(2)">A+</button>
            </div>
          </div>
          <!-- 行间距 -->
          <div class="setting-row">
            <span class="setting-label">行距</span>
            <div class="setting-control">
              <button @click="adjustLineHeight(-0.2)">−</button>
              <span class="size-value">{{ lineHeight.toFixed(1) }}</span>
              <button @click="adjustLineHeight(0.2)">+</button>
            </div>
          </div>
          <!-- 字体 -->
          <div class="setting-row">
            <span class="setting-label">字体</span>
            <select v-model="fontFamily" class="setting-select">
              <option value="'PingFang SC','Microsoft YaHei',sans-serif">默认</option>
              <option value="'Noto Serif CJK SC','Source Han Serif SC',serif">宋体</option>
              <option value="'KaiTi','STKaiti',serif">楷体</option>
            </select>
          </div>
          <!-- 主题 -->
          <div class="setting-row">
            <span class="setting-label">主题</span>
            <div class="theme-selector">
              <button v-for="t in themes" :key="t.name" class="theme-btn" :class="{ active: theme === t.name }"
                :style="{ background: t.bg, border: theme === t.name ? '2px solid ' + t.accent : '2px solid transparent' }"
                @click="theme = t.name" :title="t.label">
              </button>
            </div>
          </div>
          <!-- 亮度 -->
          <div class="setting-row">
            <span class="setting-label">亮度</span>
            <input type="range" class="brightness-slider" v-model.number="brightness" min="30" max="100" />
          </div>
        </div>
      </div>
    </transition>

    <!-- 划线本弹窗 -->
    <transition name="popup">
      <div class="notebook-overlay" v-if="showNotebook" @click.self="showNotebook = false">
        <div class="notebook-panel">
          <div class="notebook-header">
            <h3>划线本</h3>
            <span class="notebook-count">{{ highlights.length }} 条划线</span>
            <button class="close-btn" @click="showNotebook = false">✕</button>
          </div>
          <div class="notebook-body" ref="notebookBody">
            <div class="notebook-item" v-for="h in highlights" :key="h.id">
              <div class="highlight-text" :style="{ borderLeft: '3px solid ' + highlightColor(h.color) }">
                "{{ h.content }}"
              </div>
              <div class="highlight-note" v-if="h.note">
                <span class="note-label">💭 想法: </span>{{ h.note }}
              </div>
              <div class="highlight-meta">
                <span class="highlight-chapter">{{ h.chapter_title || '章节' }}</span>
                <div class="highlight-actions">
                  <button class="small-btn" @click="editHighlightNote(h)">✏ 编辑</button>
                  <button class="small-btn danger" @click="deleteHighlight(h.id)">🗑 删除</button>
                </div>
              </div>
            </div>
            <div class="notebook-empty" v-if="!highlights.length">
              <p>暂无划线</p>
              <p class="hint">在阅读中选中文字即可添加划线</p>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 划线操作菜单 -->
    <transition name="popup">
      <div class="highlight-tooltip" v-if="showHighlightTooltip" :style="tooltipStyle">
        <button v-for="c in highlightColors" :key="c.name" :title="c.label" class="color-btn"
          :style="{ background: c.color }" @click="addHighlight(c.name)">
        </button>
        <button class="tooltip-action" title="添加想法" @click="startAddNote">💬</button>
      </div>
    </transition>

    <!-- 添加想法弹窗 -->
    <transition name="popup">
      <div class="note-modal-overlay" v-if="showNoteModal" @click.self="showNoteModal = false">
        <div class="note-modal">
          <h3>添加想法</h3>
          <div class="selected-text preview">{{ selectedText }}</div>
          <textarea v-model="noteContent" placeholder="写点想法..." rows="4"></textarea>
          <div class="note-actions">
            <button @click="showNoteModal = false">取消</button>
            <button class="primary" @click="saveNote">保存</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- VIP遮罩 -->
    <transition name="popup">
      <div class="premium-overlay" v-if="showPremiumModal">
        <div class="premium-card">
          <span class="premium-icon">👑</span>
          <h3>{{ premiumTitle }}</h3>
          <p>{{ premiumMessage }}</p>
          <div class="premium-actions">
            <button class="premium-btn secondary" @click="goToPayment">订阅VIP</button>
            <button class="premium-btn primary" v-if="showPurchaseBtn" @click="purchaseChapter" :disabled="purchasing">单章购买 ¥{{ chapterPrice }}</button>
          </div>
          <button class="premium-close" @click="goBack">返回目录</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import { paginateText, pageForPosition, createReadingClock } from '../utils/reading'
import api from '../api'

// ==================== 状态 ====================
const route = useRoute()
const router = useRouter()
const workId = route.params.workId
const chapterId = route.params.chapterId

const chapter = ref(null)
const loading = ref(true)
const loadError = ref('')
const purchasing = ref(false)
const pageContainer = ref(null)
const pageText = ref(null)
const scrollContent = ref(null)
let disposed = false
let resizeObserver = null
let resizeFrame = null
let savedProgress = 0
const chapters = ref([])
const workTitle = ref('')
const showHeader = ref(true)
const showSettings = ref(false)
const showNotebook = ref(false)
const showPremiumModal = ref(false)
const premiumTitle = ref('')
const premiumMessage = ref('')
const showPurchaseBtn = ref(false)
const chapterPrice = ref(0)
const showMenu = ref(false)

// 阅读模式
const readingMode = ref(localStorage.getItem('novel_reading_mode') === 'scroll' ? 'scroll' : 'pagination')

// 阅读设置
const fontSize = ref(Math.max(12, Math.min(36, parseInt(localStorage.getItem('novel_font_size')) || 18)))
const lineHeight = ref(Math.max(1.2, Math.min(3.5, parseFloat(localStorage.getItem('novel_line_height')) || 2)))
const fontFamily = ref(localStorage.getItem('novel_font_family') || "'PingFang SC','Microsoft YaHei',sans-serif")
const theme = ref(localStorage.getItem('novel_theme') || 'dark')
const brightness = ref(parseInt(localStorage.getItem('novel_brightness') || '100'))

// 翻页
const currentPage = ref(0)
const totalPages = ref(1)
const pageContents = ref([])

// 滚动进度
const scrollPercent = ref(0)

// 划线
const highlights = ref([])
const showHighlightTooltip = ref(false)
const showNoteModal = ref(false)
const selectedText = ref('')
const noteContent = ref('')
const tooltipStyle = ref({ top: '0px', left: '0px' })
const currentHighlightColor = ref('yellow')
const editingHighlightId = ref(null)
const highlightColors = [
  { name: 'yellow', color: '#FFD700', label: '黄色' },
  { name: 'green', color: '#4CAF50', label: '绿色' },
  { name: 'blue', color: '#2196F3', label: '蓝色' },
  { name: 'pink', color: '#E91E63', label: '粉色' },
  { name: 'orange', color: '#FF9800', label: '橙色' },
]

// 主题配置
const themes = [
  { name: 'dark', bg: '#0a0c10', text: '#e8e4dc', accent: '#c9a96e', label: '深色', section: '#12151c', border: 'rgba(201,169,110,0.08)' },
  { name: 'light', bg: '#f5f0e8', text: '#3a3a3a', accent: '#8b6914', label: '日间', section: '#ffffff', border: 'rgba(0,0,0,0.06)' },
  { name: 'sepia', bg: '#f4ecd8', text: '#5c4b37', accent: '#8b6914', label: '护眼', section: '#faf3e0', border: 'rgba(139,105,20,0.08)' },
  { name: 'green', bg: '#c7edcc', text: '#2d5016', accent: '#2e7d32', label: '绿护目', section: '#d8f0dc', border: 'rgba(46,125,50,0.08)' },
  { name: 'night', bg: '#1a1a2e', text: '#a0a0b8', accent: '#7c6ff7', label: '夜间', section: '#16213e', border: 'rgba(124,111,247,0.08)' },
]

// VIP状态
const userIsVip = ref(false)

// 阅读心跳
let heartbeatInterval = null
let readingClock = createReadingClock()
let acknowledgedChars = 0
let furthestChars = 0
let heartbeatPending = null

// 触摸手势
const touchStartX = ref(0)
const touchStartY = ref(0)

// ==================== 计算属性 ====================
const currentTheme = computed(() => themes.find(t => t.name === theme.value) || themes[0])

const readerContainerStyle = computed(() => {
  const t = currentTheme.value
  const alpha = brightness.value / 100
  return {
    background: t.bg,
    color: t.text,
    '--accent': t.accent,
    '--section-bg': t.section,
    '--border-color': t.border,
    '--brightness-alpha': alpha,
    filter: `brightness(${alpha})`,
    fontFamily: fontFamily.value
  }
})

const pageStyle = computed(() => ({
  fontSize: fontSize.value + 'px',
  lineHeight: lineHeight.value,
  fontFamily: fontFamily.value,
}))

const scrollStyle = computed(() => ({
  fontSize: fontSize.value + 'px',
  lineHeight: lineHeight.value,
  fontFamily: fontFamily.value,
}))

const progressPercent = computed(() => {
  if (readingMode.value === 'pagination') {
    return chapter.value?.content?.length ? Math.min(100, Math.floor((pageContents.value[currentPage.value]?.end || 0) / chapter.value.content.length * 100)) : 0
  }
  return Math.round(scrollPercent.value)
})

const prevChapterId = computed(() => {
  const idx = chapters.value.findIndex(c => c.id == chapterId)
  return idx > 0 ? chapters.value[idx - 1].id : null
})

const nextChapterId = computed(() => {
  const idx = chapters.value.findIndex(c => c.id == chapterId)
  return idx < chapters.value.length - 1 ? chapters.value[idx + 1].id : null
})

const currentPageContent = computed(() => {
  return pageContents.value[currentPage.value]?.text || ''
})

// ==================== 方法 ====================

// 阅读设置
function adjustFontSize(delta) {
  fontSize.value = Math.max(12, Math.min(36, fontSize.value + delta))
  localStorage.setItem('novel_font_size', fontSize.value)
}

function adjustLineHeight(delta) {
  lineHeight.value = Math.max(1.2, Math.min(3.5, +(lineHeight.value + delta).toFixed(1)))
  localStorage.setItem('novel_line_height', lineHeight.value)
}

// 翻页
async function layoutPages(position = savedProgress) {
  await nextTick()
  if (disposed || !chapter.value) return
  if (readingMode.value === 'scroll') {
    const el = scrollContent.value
    if (el) {
      el.scrollTop = Math.max(0, el.scrollHeight - el.clientHeight) * position / 100
      onScroll()
    }
    return
  }
  const container = pageContainer.value
  const content = pageText.value
  if (!container || !content) return
  const box = getComputedStyle(container)
  const availableHeight = container.clientHeight - parseFloat(box.paddingTop) - parseFloat(box.paddingBottom)
  const width = container.clientWidth - parseFloat(box.paddingLeft) - parseFloat(box.paddingRight)
  const style = getComputedStyle(content)
  const measure = document.createElement('div')
  Object.assign(measure.style, {
    position: 'fixed', visibility: 'hidden', pointerEvents: 'none', top: '0', left: '-10000px',
    width: width + 'px', fontFamily: style.fontFamily, fontSize: style.fontSize,
    lineHeight: style.lineHeight, fontWeight: style.fontWeight, letterSpacing: style.letterSpacing,
    whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', textIndent: style.textIndent,
  })
  document.body.appendChild(measure)
  try {
    pageContents.value = paginateText(chapter.value.content || '', text => {
      measure.textContent = text
      return measure.getBoundingClientRect().height <= Math.max(1, availableHeight - 1)
    })
    totalPages.value = pageContents.value.length
    currentPage.value = pageForPosition(pageContents.value, (chapter.value.content || '').length * position / 100)
  } finally { measure.remove() }
}

function scheduleLayout() {
  if (resizeFrame) cancelAnimationFrame(resizeFrame)
  const position = layoutAnchor()
  resizeFrame = requestAnimationFrame(() => { void layoutPages(position) })
}

function layoutAnchor(mode = readingMode.value) {
  if (mode === 'scroll') return scrollPercent.value
  const length = chapter.value?.content?.length || 1
  return ((pageContents.value[currentPage.value]?.start || 0) + 0.01) / length * 100
}

function goPrevPage() {
  if (currentPage.value > 0) {
    currentPage.value--
  } else if (prevChapterId.value) {
    goPrevChapter()
  }
}

function goNextPage() {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++
  } else if (nextChapterId.value) {
    goNextChapter()
  }
}

// 划线功能
function onTextSelect(e) {
  const selection = window.getSelection()
  if (!selection?.rangeCount) return
  const text = selection.toString().trim()
  if (text.length > 2 && text.length < 200) {
    selectedText.value = text
    const range = selection.getRangeAt(0)
    const rect = range.getBoundingClientRect()
    tooltipStyle.value = {
      top: (rect.top - 50) + 'px',
      left: Math.max(10, Math.min(window.innerWidth - 200, (rect.left + rect.width / 2 - 100))) + 'px'
    }
    showHighlightTooltip.value = true
  }
}

function onTextSelectTouch(e) {
  setTimeout(() => {
    onTextSelect(e)
  }, 200)
}

async function addHighlight(color) {
  if (!selectedText.value) return
  currentHighlightColor.value = color
  showHighlightTooltip.value = false

  try {
    // 查找选中文本的大致位置
    const fullText = chapter.value?.content || ''
    const startPos = fullText.indexOf(selectedText.value.substring(0, 20))
    const endPos = startPos >= 0 ? startPos + selectedText.value.length : 0

    await api.post('/highlights', {
      chapter_id: parseInt(chapterId),
      content: selectedText.value,
      note: '',
      color: color,
      location_start: Math.max(0, startPos),
      location_end: Math.max(0, endPos)
    }, {
      params: { work_id: parseInt(workId) }
    })
    await loadHighlights()
    selectedText.value = ''
    window.getSelection().removeAllRanges()
  } catch (e) {
    console.error('划线失败:', e)
  }
}

function startAddNote() {
  editingHighlightId.value = null
  showHighlightTooltip.value = false
  noteContent.value = ''
  showNoteModal.value = true
}

async function saveNote() {
  if (!selectedText.value) return
  try {
    if (editingHighlightId.value) {
      await api.put(`/highlights/${editingHighlightId.value}`, { note: noteContent.value })
      editingHighlightId.value = null
    } else {
      const start = Math.max(0, (chapter.value?.content || '').indexOf(selectedText.value))
      await api.post('/highlights', {
        chapter_id: parseInt(chapterId), content: selectedText.value,
        color: currentHighlightColor.value, note: noteContent.value,
        location_start: start, location_end: start + selectedText.value.length
      }, { params: { work_id: parseInt(workId) } })
    }
    await loadHighlights()
    showNoteModal.value = false
    selectedText.value = ''
    noteContent.value = ''
    window.getSelection().removeAllRanges()
  } catch (e) {
    console.error('保存想法失败:', e)
  }
}

function editHighlightNote(h) {
  editingHighlightId.value = h.id
  selectedText.value = h.content
  noteContent.value = h.note
  showNoteModal.value = true
}

async function deleteHighlight(id) {
  try {
    await api.delete(`/highlights/${id}`)
    highlights.value = highlights.value.filter(h => h.id !== id)
  } catch (e) {
    console.error('删除划线失败:', e)
  }
}

async function loadHighlights() {
  try {
    const res = await api.get('/highlights', {
      params: { work_id: workId, chapter_id: chapterId }
    })
    highlights.value = res.data || []
    // 获取章节标题
    for (const h of highlights.value) {
      const ch = chapters.value.find(c => c.id === h.chapter_id)
      h.chapter_title = ch ? ch.title : ''
    }
  } catch (e) {
    console.error('加载划线失败:', e)
    highlights.value = []
  }
}

function highlightColor(color) {
  const c = highlightColors.find(h => h.name === color)
  return c ? c.color : '#FFD700'
}

// 导航
function goBack() {
  router.push(`/works/${workId}`)
}

function goPrevChapter() {
  if (prevChapterId.value) {
    router.push(`/works/${workId}/chapters/${prevChapterId.value}`)
  }
}

function goNextChapter() {
  if (nextChapterId.value) {
    router.push(`/works/${workId}/chapters/${nextChapterId.value}`)
  }
}

function toggleHeader() {
  showHeader.value = !showHeader.value
}

function goToPayment() {
  router.push('/payment')
}

async function purchaseChapter() {
  if (purchasing.value) return
  purchasing.value = true
  try {
    await api.post('/payment/chapter/purchase', null, { params: { work_id: workId, chapter_id: chapterId } })
    showPremiumModal.value = false
    await loadReader()
  } catch (error) {
    premiumMessage.value = error.response?.data?.detail || '购买失败，请稍后重试。'
  } finally { purchasing.value = false }
}

// 滚动进度
function onProgressClick(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  const percent = ((e.clientY - rect.top) / rect.height) * 100
  const mainEl = scrollContent.value
  if (mainEl) {
    mainEl.scrollTop = (mainEl.scrollHeight - mainEl.clientHeight) * (percent / 100)
  }
}

// 触摸手势
function onTouchStart(e) {
  touchStartX.value = e.touches[0].clientX
  touchStartY.value = e.touches[0].clientY
}

function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - touchStartX.value
  const dy = e.changedTouches[0].clientY - touchStartY.value
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {
    if (readingMode.value === 'pagination') {
      if (dx > 0) goPrevPage()
      else goNextPage()
    }
  }
}

// 键盘快捷键
function onKeyDown(e) {
  if (loading.value || !chapter.value || showNoteModal.value || e.target?.closest('input, textarea, select, [contenteditable="true"]')) return
  if (e.key === 'ArrowLeft') {
    readingMode.value === 'pagination' ? goPrevPage() : goPrevChapter()
  } else if (e.key === 'ArrowRight') {
    readingMode.value === 'pagination' ? goNextPage() : goNextChapter()
  } else if (e.key === ' ') {
    e.preventDefault()
    readingMode.value === 'pagination' ? goNextPage() : null
  }
}

// 数据加载
async function loadChapter() {
  const res = await api.get(`/chapters/${chapterId}`)
  if (disposed) return
  if (res.data.work_id !== Number(workId)) throw new Error('章节不属于当前作品')
  chapter.value = res.data
}

async function loadChapters() {
  const res = await api.get('/chapters', { params: { work_id: workId } })
  chapters.value = res.data.chapters
  chapterPrice.value = chapters.value.find(ch => ch.id === Number(chapterId))?.chapter_price || 0
}

async function loadReader() {
  loading.value = true
  loadError.value = ''
  chapter.value = null
  showPremiumModal.value = false
  stopHeartbeat()
  try {
    // Load the directory first so the paywall always has the actual price.
    await loadChapters()
    await loadChapter()
    if (disposed) return
    try {
      const { data } = await api.get(`/bookshelf/progress/${workId}`)
      savedProgress = data.chapter_id === Number(chapterId) ? data.progress : 0
    } catch { savedProgress = 0 }
    acknowledgedChars = Math.floor((chapter.value.content || '').length * savedProgress / 100)
    furthestChars = acknowledgedChars
    readingClock = createReadingClock()
  } catch (error) {
    chapter.value = null
    const status = error.response?.status
    if (status === 402 || status === 403) {
      showPremiumModal.value = true
      premiumTitle.value = status === 403 ? 'VIP专属章节' : '付费章节'
      premiumMessage.value = error.response.data?.detail || '请先购买或查看会员状态'
      showPurchaseBtn.value = status === 402
    } else {
      loadError.value = status === 404 ? '章节不存在，请返回目录选择其他章节。' : '章节加载失败，请检查连接后重试。'
    }
  } finally { loading.value = false }
  if (chapter.value && !disposed) {
    await layoutPages(savedProgress)
    observeLayout()
    startHeartbeat()
    void loadHighlights()
  }
}

async function loadWorkInfo() {
  try { workTitle.value = (await api.get(`/works/${workId}`)).data.title } catch { workTitle.value = '作品' }
}

// Only visible, successfully loaded content contributes active reading time.
function tickReading() {
  readingClock.tick(document.visibilityState === 'visible' && !!chapter.value && !loading.value && !showPremiumModal.value)
  if (chapter.value) furthestChars = Math.max(furthestChars, Math.floor((chapter.value.content || '').length * progressPercent.value / 100))
}

function startHeartbeat() {
  stopHeartbeat()
  heartbeatInterval = setInterval(() => {
    tickReading()
    if (readingClock.pending() >= 30) void flushHeartbeat()
  }, 1000)
}

function flushHeartbeat(keepalive = false) {
  if (!chapter.value || loading.value) return Promise.resolve()
  if (heartbeatPending) return heartbeatPending
  tickReading()
  const seconds = readingClock.pending()
  const submittedChars = furthestChars
  const payload = {
    work_id: Number(workId), chapter_id: Number(chapterId), duration_seconds: seconds,
    chars_read: Math.max(0, Math.min(100000, submittedChars - acknowledgedChars)), progress: progressPercent.value
  }
  const request = keepalive
    ? fetch('/api/reading/heartbeat', {
        method: 'POST', keepalive: true,
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify(payload)
      }).then(response => { if (!response.ok) throw new Error('进度保存失败') })
    : api.post('/reading/heartbeat', payload, { timeout: 2000 })
  heartbeatPending = request.then(() => {
    readingClock.acknowledge(seconds)
    acknowledgedChars = submittedChars
  }).catch(() => {}).finally(() => { heartbeatPending = null })
  return heartbeatPending
}

function stopHeartbeat() {
  if (heartbeatInterval) clearInterval(heartbeatInterval)
  heartbeatInterval = null
}

function onVisibilityChange() {
  // Reset the clock edge before a hidden interval can be counted on return.
  readingClock.tick(false)
  if (document.visibilityState === 'hidden') void flushHeartbeat(true)
}
function onPageHide() { void flushHeartbeat(true) }
function observeLayout() {
  resizeObserver?.disconnect()
  if (pageContainer.value) resizeObserver?.observe(pageContainer.value)
}

// 监听滚动
function onScroll() {
  const mainEl = scrollContent.value
  if (mainEl) {
    const scrollTop = mainEl.scrollTop
    const scrollHeight = mainEl.scrollHeight - mainEl.clientHeight
    scrollPercent.value = scrollHeight > 0 ? Math.round((scrollTop / scrollHeight) * 100) : 100
  }
}

watch(readingMode, async (val, old) => {
  const position = layoutAnchor(old)
  localStorage.setItem('novel_reading_mode', val)
  await layoutPages(position)
  observeLayout()
})
watch(progressPercent, val => { savedProgress = val })
watch([fontSize, lineHeight, fontFamily], () => { void layoutPages(layoutAnchor()) })
watch(theme, val => localStorage.setItem('novel_theme', val))
watch(fontFamily, val => localStorage.setItem('novel_font_family', val))
watch(brightness, val => localStorage.setItem('novel_brightness', val))

onBeforeRouteLeave(() => flushHeartbeat())
onBeforeRouteUpdate(() => flushHeartbeat())
onMounted(() => {
  resizeObserver = new ResizeObserver(scheduleLayout)
  document.addEventListener('keydown', onKeyDown)
  document.addEventListener('visibilitychange', onVisibilityChange)
  window.addEventListener('pagehide', onPageHide)
  window.addEventListener('resize', scheduleLayout)
  void loadWorkInfo()
  void loadReader()
})
onUnmounted(() => {
  disposed = true
  stopHeartbeat()
  resizeObserver?.disconnect()
  if (resizeFrame) cancelAnimationFrame(resizeFrame)
  document.removeEventListener('keydown', onKeyDown)
  document.removeEventListener('visibilitychange', onVisibilityChange)
  window.removeEventListener('pagehide', onPageHide)
  window.removeEventListener('resize', scheduleLayout)
})
</script>

<style scoped>
.reader-page {
  height: 100dvh;
  position: relative;
  overflow: hidden;
  user-select: none;
}

/* Header */
.reader-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--section-bg);
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(12px);
}

.header-inner {
  max-width: 800px;
  margin: 0 auto;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  background: none;
  border: none;
  color: var(--text);
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
}

.icon-btn:hover {
  background: rgba(128,128,128,0.1);
}

.header-info {
  flex: 1;
  min-width: 0;
}

.work-title {
  display: block;
  font-size: 12px;
  opacity: 0.6;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chapter-title {
  display: block;
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  opacity: 0.5;
  min-width: 40px;
  text-align: right;
}

/* Main Content */
.reader-main {
  height: 100dvh;
  padding-top: 56px;
  padding-bottom: 110px;
  position: relative;
}

/* Pagination Mode */
.page-container {
  max-width: 560px;
  margin: 0 auto;
  padding: 24px 20px;
  height: min(100%, 784px);
  position: relative;
  top: 50%;
  transform: translateY(-50%);
  overflow: hidden;
}

.page-content {
  width: 100%;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  user-select: text;
  max-width: 100%;
  line-height: var(--line-height, 2);
  text-indent: 2em;
}

.page-content p {
  margin-bottom: 1em;
}

.page-hotspots {
  position: fixed;
  bottom: 60px;
  left: 0;
  right: 0;
  top: 56px;
  display: flex;
  pointer-events: none;
}

.hotspot {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  cursor: pointer;
  font-size: 36px;
  opacity: 0;
  transition: opacity 0.2s;
  color: var(--accent);
}

.hotspot:hover {
  opacity: 0.6;
}

.hotspot.center {
  opacity: 0;
  cursor: default;
}

/* Scroll Mode */
.scroll-content {
  height: 100%;
  overflow-y: auto;
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px 120px;
  line-height: var(--line-height, 2);
  user-select: text;
  -webkit-user-select: text;
}

.chapter-name {
  font-size: 1.5em;
  text-align: center;
  margin-bottom: 32px;
  font-weight: 600;
  opacity: 0.8;
}

.chapter-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  text-indent: 2em;
}

.scroll-progress {
  position: fixed;
  top: 56px;
  right: 0;
  width: 4px;
  height: calc(100vh - 116px);
  background: var(--border-color);
  cursor: pointer;
  z-index: 50;
}

.scroll-progress-bar {
  width: 100%;
  height: 0%;
  background: var(--accent);
  transition: height 0.3s;
  opacity: 0.5;
}

.scroll-progress:hover .scroll-progress-bar {
  width: 100%;
  opacity: 1;
}

/* Footer */
.reader-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--section-bg);
  border-top: 1px solid var(--border-color);
  backdrop-filter: blur(12px);
}

.footer-inner {
  max-width: 800px;
  margin: 0 auto;
  padding: 8px 16px;
}

.footer-chapter-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.nav-btn {
  flex: 1;
  padding: 10px;
  background: rgba(128,128,128,0.1);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover:not(:disabled) {
  background: rgba(128,128,128,0.2);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.footer-tools {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.tool-btn {
  padding: 6px 12px;
  background: none;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text);
  font-size: 16px;
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.2s;
}

.tool-btn:hover,
.tool-btn.active {
  opacity: 1;
  background: rgba(128,128,128,0.1);
}

.tool-btn.active {
  border-color: var(--accent);
}

/* Settings Panel */
.settings-panel {
  position: fixed;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 400px;
  background: var(--section-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  z-index: 200;
  overflow: hidden;
}

.settings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.settings-header h3 {
  font-size: 16px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text);
  font-size: 16px;
  cursor: pointer;
  opacity: 0.5;
}

.settings-body {
  padding: 16px 20px;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.setting-row:last-child {
  margin-bottom: 0;
}

.setting-label {
  font-size: 14px;
  opacity: 0.7;
  min-width: 60px;
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-control button {
  width: 32px;
  height: 32px;
  background: rgba(128,128,128,0.1);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text);
  cursor: pointer;
  font-size: 14px;
}

.size-value {
  min-width: 40px;
  text-align: center;
  font-size: 14px;
}

.setting-select {
  padding: 6px 12px;
  background: rgba(128,128,128,0.1);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text);
  font-size: 13px;
}

.theme-selector {
  display: flex;
  gap: 8px;
}

.theme-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
}

.brightness-slider {
  width: 120px;
  accent-color: var(--accent);
}

/* Highlight Colors - for global use */
:deep(.hl-yellow) { background: rgba(255,215,0,0.3); }
:deep(.hl-green) { background: rgba(76,175,80,0.3); }
:deep(.hl-blue) { background: rgba(33,150,243,0.3); }
:deep(.hl-pink) { background: rgba(233,30,99,0.3); }
:deep(.hl-orange) { background: rgba(255,152,0,0.3); }

/* Highlight Tooltip */
.highlight-tooltip {
  position: fixed;
  z-index: 300;
  background: var(--section-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 8px 12px;
  display: flex;
  gap: 6px;
  align-items: center;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

.color-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
}

.color-btn:hover {
  transform: scale(1.15);
}

.tooltip-action {
  background: none;
  border: none;
  color: var(--text);
  font-size: 16px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}

.tooltip-action:hover {
  background: rgba(128,128,128,0.1);
}

/* Notebook */
.notebook-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 300;
  display: flex;
  align-items: flex-end;
}

.notebook-panel {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  max-height: 70vh;
  background: var(--section-bg);
  border-radius: 16px 16px 0 0;
  display: flex;
  flex-direction: column;
}

.notebook-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  gap: 12px;
}

.notebook-header h3 {
  font-size: 16px;
  font-weight: 600;
}

.notebook-count {
  font-size: 12px;
  opacity: 0.5;
  flex: 1;
}

.notebook-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.notebook-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.notebook-item:last-child {
  border-bottom: none;
}

.highlight-text {
  font-size: 14px;
  line-height: 1.6;
  padding: 8px 12px;
  margin-bottom: 8px;
  opacity: 0.9;
  font-style: italic;
}

.highlight-note {
  font-size: 13px;
  padding: 8px 12px;
  background: rgba(128,128,128,0.05);
  border-radius: 8px;
  margin-bottom: 8px;
  line-height: 1.5;
}

.note-label {
  opacity: 0.6;
}

.highlight-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.highlight-chapter {
  opacity: 0.4;
}

.highlight-actions {
  display: flex;
  gap: 4px;
}

.small-btn {
  padding: 4px 8px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text);
  font-size: 11px;
  cursor: pointer;
}

.small-btn.danger {
  border-color: rgba(255,0,0,0.3);
  color: #ff6b6b;
}

.notebook-empty {
  text-align: center;
  padding: 40px 0;
  opacity: 0.5;
}

.notebook-empty .hint {
  font-size: 12px;
  margin-top: 8px;
}

/* Note Modal */
.note-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 400;
  display: flex;
  align-items: center;
  justify-content: center;
}

.note-modal {
  width: 90%;
  max-width: 400px;
  background: var(--section-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
}

.note-modal h3 {
  font-size: 18px;
  margin-bottom: 16px;
}

.selected-text.preview {
  font-size: 14px;
  opacity: 0.7;
  padding: 12px;
  background: rgba(128,128,128,0.05);
  border-radius: 8px;
  margin-bottom: 16px;
  line-height: 1.6;
  font-style: italic;
}

.note-modal textarea {
  width: 100%;
  padding: 12px;
  background: rgba(128,128,128,0.05);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text);
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

.note-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.note-actions button {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: none;
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
}

.note-actions button.primary {
  background: var(--accent);
  color: #0a0c10;
  border-color: transparent;
  font-weight: 600;
}

/* Premium Overlay */
.premium-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.premium-card {
  background: var(--section-bg);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 32px;
  text-align: center;
  max-width: 360px;
  width: 90%;
}

.premium-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.premium-card h3 {
  font-size: 22px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 12px;
}

.premium-card p {
  font-size: 14px;
  opacity: 0.7;
  line-height: 1.6;
  margin-bottom: 24px;
}

.premium-actions {
  display: flex;
  gap: 12px;
}

.premium-btn {
  flex: 1;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.premium-btn.primary {
  background: var(--accent);
  color: #0a0c10;
}

.premium-btn.secondary {
  background: rgba(128,128,128,0.1);
  color: var(--text);
  border: 1px solid var(--border-color);
}

.premium-close {
  margin-top: 16px;
  background: none;
  border: none;
  color: var(--text);
  opacity: 0.5;
  font-size: 13px;
  cursor: pointer;
}

/* Transitions */
.slide-down-enter-active, .slide-down-leave-active { transition: transform 0.25s ease, opacity 0.25s ease; }
.slide-down-enter-from, .slide-down-leave-to { transform: translateY(-100%); opacity: 0; }

.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.25s ease, opacity 0.25s ease; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%); opacity: 0; }

.popup-enter-active, .popup-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.popup-enter-from, .popup-leave-to { opacity: 0; transform: scale(0.95); }

/* Responsive */
@media (max-width: 768px) {
  .scroll-content {
    padding: 24px 16px 100px;
  }
  .page-container {
    padding: 24px 16px;
  }
}
.page-number { font-size: 12px; color: var(--text-muted, #aaa); white-space: nowrap; }
.reader-status { display: flex; gap: 16px; flex-wrap: wrap; align-items: center; justify-content: center; height: 100%; padding: 24px; }
.reader-status button { padding: 10px 16px; background: var(--section-bg); color: inherit; border: 1px solid var(--accent); border-radius: 8px; }
</style>
