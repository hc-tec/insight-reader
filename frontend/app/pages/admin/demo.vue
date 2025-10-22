<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-zinc-50 relative overflow-hidden">
    <!-- 背景装饰 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-emerald-400/10 rounded-full blur-3xl"></div>
      <div class="absolute top-1/3 -left-40 w-80 h-80 bg-teal-400/10 rounded-full blur-3xl"></div>
      <div class="absolute bottom-20 right-1/3 w-64 h-64 bg-slate-400/10 rounded-full blur-3xl"></div>
    </div>

    <!-- 内容区域 -->
    <div class="relative z-10">
      <AppHeader />

      <!-- 权限检查 -->
      <div v-if="!user" class="max-w-7xl mx-auto px-6 py-20">
        <div class="max-w-md mx-auto bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-8 shadow-sm text-center">
          <div class="w-20 h-20 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg class="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">需要登录</h2>
          <p class="text-gray-600 mb-6">请先登录才能访问管理员页面</p>
          <NuxtLink
            to="/login"
            class="inline-block px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl hover:from-emerald-700 hover:to-teal-700 transition-all shadow-md font-semibold"
          >
            前往登录
          </NuxtLink>
        </div>
      </div>

      <!-- 管理员内容 -->
      <div v-else>
        <!-- 页面头部 -->
        <div class="max-w-7xl mx-auto px-6 pt-8 pb-6">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h1 class="text-4xl font-bold bg-gradient-to-r from-slate-800 via-slate-700 to-zinc-700 bg-clip-text text-transparent mb-2">
                示例文章管理
              </h1>
              <p class="text-gray-600 text-lg">
                管理员专用页面
              </p>
            </div>
            <NuxtLink
              to="/"
              target="_blank"
              class="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl hover:from-emerald-700 hover:to-teal-700 transition-all shadow-md font-semibold whitespace-nowrap"
            >
              查看首页示例文章 →
            </NuxtLink>
          </div>

          <!-- 标签切换 -->
          <div class="bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-2 flex gap-2 shadow-sm">
            <button
              @click="activeTab = 'demo'"
              :class="[
                'flex-1 px-6 py-3 rounded-xl font-semibold transition-all',
                activeTab === 'demo'
                  ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-50'
              ]"
            >
              已标记的示例 ({{ demoArticles.length }})
            </button>
            <button
              @click="activeTab = 'all'"
              :class="[
                'flex-1 px-6 py-3 rounded-xl font-semibold transition-all',
                activeTab === 'all'
                  ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-50'
              ]"
            >
              所有文章
            </button>
          </div>
        </div>

        <!-- 文章列表区域 -->
        <div class="max-w-7xl mx-auto px-6 pb-12">
          <!-- 加载状态 -->
          <div v-if="loading" class="flex items-center justify-center py-20">
            <div class="animate-spin h-12 w-12 border-4 border-purple-600 border-t-transparent rounded-full"></div>
            <span class="ml-4 text-gray-600">加载中...</span>
          </div>

          <!-- 错误状态 -->
          <div v-else-if="error" class="py-20 flex flex-col items-center justify-center">
            <div class="w-24 h-24 bg-gradient-to-br from-red-100 to-pink-100 rounded-2xl flex items-center justify-center mb-6">
              <svg class="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">加载失败</h3>
            <p class="text-gray-600 mb-6">{{ error }}</p>
            <button
              @click="loadData"
              class="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl hover:from-emerald-700 hover:to-teal-700 transition-all shadow-md"
            >
              重试
            </button>
          </div>

          <!-- 示例文章列表 -->
          <div v-else-if="activeTab === 'demo'">
            <!-- 空状态 -->
            <div v-if="demoArticles.length === 0" class="py-20 flex flex-col items-center justify-center">
              <div class="w-24 h-24 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-2xl flex items-center justify-center mb-6">
                <svg class="w-12 h-12 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">暂无示例文章</h3>
              <p class="text-gray-600 mb-6">切换到"所有文章"标签，选择文章标记为示例</p>
            </div>

            <!-- 示例文章网格 -->
            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="article in sortedDemoArticles"
                :key="article.id"
                class="group bg-white/70 backdrop-blur-xl border-2 border-amber-200/50 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all"
              >
                <div class="flex items-start justify-between mb-3">
                  <div class="flex items-center gap-2">
                    <span class="px-3 py-1 bg-gradient-to-r from-amber-500 to-orange-600 text-white text-sm font-bold rounded-full">
                      #{{ article.demo_order || '?' }}
                    </span>
                    <span v-if="article.has_analysis" class="px-3 py-1 bg-teal-100 text-teal-700 text-xs rounded-full font-medium">
                      完整分析
                    </span>
                    <span v-if="article.has_meta_analysis" class="px-3 py-1 bg-slate-100 text-slate-700 text-xs rounded-full font-medium">
                      元视角
                    </span>
                  </div>
                  <button
                    @click="handleUnmark(article.id)"
                    class="p-2 rounded-lg hover:bg-red-50 transition-colors"
                    title="取消示例标记"
                  >
                    <svg class="w-5 h-5 text-gray-400 hover:text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <h3 class="text-xl font-semibold text-gray-900 mb-2">
                  {{ article.title }}
                </h3>
                <p v-if="article.author" class="text-sm text-gray-600 mb-3">
                  作者: {{ article.author }}
                </p>

                <div class="flex items-center gap-4 text-sm text-gray-600 mb-4">
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {{ formatNumber(article.word_count || 0) }} 字
                  </span>
                </div>

                <div class="flex items-center gap-2">
                  <input
                    v-model.number="article.demo_order"
                    type="number"
                    min="1"
                    placeholder="展示顺序"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    @change="handleUpdateOrder(article.id, article.demo_order)"
                  />
                  <NuxtLink
                    :to="`/?articleId=${article.id}`"
                    target="_blank"
                    class="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg text-sm font-medium hover:from-emerald-700 hover:to-teal-700 transition-all"
                  >
                    预览
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>

          <!-- 所有文章列表 -->
          <div v-else-if="activeTab === 'all'">
            <!-- 搜索框 -->
            <div class="mb-6">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索文章标题..."
                class="w-full px-6 py-4 bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-500 text-lg shadow-sm"
              />
            </div>

            <!-- 空状态 -->
            <div v-if="filteredAllArticles.length === 0" class="py-20 flex flex-col items-center justify-center">
              <div class="w-24 h-24 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-2xl flex items-center justify-center mb-6">
                <svg class="w-12 h-12 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">没有找到文章</h3>
              <p class="text-gray-600">尝试调整搜索关键词</p>
            </div>

            <!-- 文章网格 -->
            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="article in filteredAllArticles"
                :key="article.id"
                class="group bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all"
              >
                <h3 class="text-xl font-semibold text-gray-900 mb-2">
                  {{ article.title }}
                </h3>
                <div class="flex items-center gap-4 text-sm text-gray-600 mb-4">
                  <span v-if="article.author" class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    {{ article.author }}
                  </span>
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {{ formatNumber(article.word_count || 0) }} 字
                  </span>
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ formatDate(article.created_at) }}
                  </span>
                </div>

                <div class="flex items-center gap-2">
                  <input
                    v-model.number="markOrders[article.id]"
                    type="number"
                    min="1"
                    placeholder="展示顺序（可选）"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                  <button
                    @click="handleMark(article.id, markOrders[article.id])"
                    class="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg text-sm font-medium hover:from-emerald-700 hover:to-teal-700 transition-all whitespace-nowrap"
                  >
                    标记为示例
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast 提示 -->
    <div
      v-if="toast.show"
      class="fixed bottom-8 right-8 px-6 py-4 bg-white rounded-xl shadow-lg border-l-4 font-semibold z-50 animate-slide-in"
      :class="toast.type === 'success' ? 'border-green-500 text-green-700' : 'border-red-500 text-red-700'"
    >
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AdminArticle } from '~/composables/useAdminDemo'

// 页面元数据
definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

// Composables
const { user } = useAuth()
const {
  getDemoArticles,
  getAllArticles,
  markAsDemo,
  unmarkDemo,
  updateOrder,
  loading,
  error
} = useAdminDemo()

// 状态
const activeTab = ref<'demo' | 'all'>('demo')
const demoArticles = ref<AdminArticle[]>([])
const allArticles = ref<AdminArticle[]>([])
const searchQuery = ref('')
const markOrders = ref<Record<number, number>>({})

// Toast 提示
const toast = ref({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

// 排序后的示例文章
const sortedDemoArticles = computed(() => {
  return [...demoArticles.value].sort((a, b) => {
    const orderA = a.demo_order ?? 999
    const orderB = b.demo_order ?? 999
    return orderA - orderB
  })
})

// 过滤后的所有文章
const filteredAllArticles = computed(() => {
  if (!searchQuery.value) return allArticles.value

  const query = searchQuery.value.toLowerCase()
  return allArticles.value.filter(article =>
    article.title.toLowerCase().includes(query)
  )
})

// 显示提示
const showToast = (message: string, type: 'success' | 'error' = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}万`
  }
  return num.toString()
}

// 加载数据
const loadData = async () => {
  if (activeTab.value === 'demo') {
    const articles = await getDemoArticles()
    if (articles) {
      demoArticles.value = articles
    }
  } else {
    const articles = await getAllArticles()
    if (articles) {
      allArticles.value = articles
    }
  }
}

// 标记为示例
const handleMark = async (articleId: number, order?: number) => {
  const success = await markAsDemo(articleId, {
    demo_order: order
  })

  if (success) {
    showToast('已标记为示例文章', 'success')
    await loadData()
  } else {
    showToast(error.value || '标记失败', 'error')
  }
}

// 取消标记
const handleUnmark = async (articleId: number) => {
  if (!confirm('确定要取消示例标记吗？')) return

  const success = await unmarkDemo(articleId)

  if (success) {
    showToast('已取消示例标记', 'success')
    await loadData()
  } else {
    showToast(error.value || '操作失败', 'error')
  }
}

// 更新顺序
const handleUpdateOrder = async (articleId: number, order?: number) => {
  if (!order) return

  const success = await updateOrder(articleId, order)

  if (success) {
    showToast('顺序已更新', 'success')
  } else {
    showToast(error.value || '更新失败', 'error')
  }
}

// 监听标签切换
watch(activeTab, () => {
  loadData()
})

// 页面加载时获取数据
onMounted(() => {
  loadData()
})

// 设置页面标题
useHead({
  title: '示例文章管理 - InsightReader'
})
</script>

<style scoped>
@keyframes slide-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animate-slide-in {
  animation: slide-in 0.3s ease-out;
}
</style>
