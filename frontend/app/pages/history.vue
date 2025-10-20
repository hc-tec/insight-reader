<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-zinc-50 relative overflow-hidden">
    <!-- 背景装饰 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl"></div>
      <div class="absolute top-1/3 -left-40 w-80 h-80 bg-indigo-400/10 rounded-full blur-3xl"></div>
      <div class="absolute bottom-20 right-1/3 w-64 h-64 bg-violet-400/10 rounded-full blur-3xl"></div>
    </div>

    <!-- 内容区域 -->
    <div class="relative z-10">
      <AppHeader />

      <!-- 页面头部 -->
      <div class="max-w-7xl mx-auto px-6 pt-8 pb-6">
        <div class="mb-6">
          <h1 class="text-4xl font-bold bg-gradient-to-r from-purple-800 via-violet-700 to-indigo-700 bg-clip-text text-transparent mb-2">
            阅读历史
          </h1>
          <p class="text-gray-600 text-lg">
            查看你曾经阅读过的文章，随时重温精彩内容
          </p>
        </div>

        <!-- 统计卡片 -->
        <div v-if="stats" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div class="bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-6 shadow-sm">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <div class="text-3xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  {{ stats.total }}
                </div>
                <div class="text-sm text-gray-600 mt-0.5">总阅读篇数</div>
              </div>
            </div>
          </div>

          <div class="bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-6 shadow-sm">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <div>
                <div class="text-3xl font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">
                  {{ stats.withMetaAnalysis }}
                </div>
                <div class="text-sm text-gray-600 mt-0.5">元视角分析</div>
              </div>
            </div>
          </div>

          <div class="bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-6 shadow-sm">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-xl flex items-center justify-center">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <div class="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">
                  {{ formatNumber(stats.totalWords) }}
                </div>
                <div class="text-sm text-gray-600 mt-0.5">累计字数</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 文章列表 -->
      <div class="max-w-7xl mx-auto px-6 pb-12">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="flex items-center justify-center py-20">
          <div class="animate-spin h-12 w-12 border-4 border-purple-600 border-t-transparent rounded-full"></div>
          <span class="ml-4 text-gray-600">加载中...</span>
        </div>

        <!-- 文章列表 -->
        <div v-else-if="articles.length > 0" class="space-y-4">
          <div
            v-for="article in articles"
            :key="article.id"
            class="group bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all hover:-translate-y-1 cursor-pointer"
            @click="openArticle(article.id)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h3 class="text-xl font-semibold text-gray-900 mb-2 group-hover:text-purple-600 transition-colors">
                  {{ article.title }}
                </h3>
                <div class="flex items-center gap-4 text-sm text-gray-600 mb-3">
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    {{ article.author || '未知作者' }}
                  </span>
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {{ formatNumber(article.word_count) }} 字
                  </span>
                  <span class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    阅读 {{ article.read_count }} 次
                  </span>
                </div>
                <div class="flex items-center gap-4 text-xs text-gray-500">
                  <span>首次阅读: {{ formatDate(article.created_at) }}</span>
                  <span>最后阅读: {{ formatDate(article.last_read_at) }}</span>
                </div>
              </div>

              <!-- 标签 -->
              <div class="flex flex-col items-end gap-2">
                <span v-if="article.has_meta_analysis" class="px-3 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                  元视角
                </span>
                <button
                  @click.stop="deleteArticle(article.id)"
                  class="p-2 rounded-lg hover:bg-red-50 transition-colors"
                  title="删除"
                >
                  <svg class="w-5 h-5 text-gray-400 hover:text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="py-20 flex flex-col items-center justify-center">
          <div class="w-24 h-24 bg-gradient-to-br from-purple-100 to-indigo-100 rounded-2xl flex items-center justify-center mb-6">
            <svg class="w-12 h-12 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">还没有阅读记录</h3>
          <p class="text-gray-600 mb-6">开始阅读文章，这里将显示你的历史记录</p>
          <NuxtLink
            to="/"
            class="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all shadow-md"
          >
            开始阅读
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()
const { isAuthenticated, user } = useAuth()
const config = useRuntimeConfig()

interface Article {
  id: number
  title: string
  author: string
  word_count: number
  read_count: number
  created_at: string
  last_read_at: string
  has_meta_analysis: boolean
}

const articles = ref<Article[]>([])
const isLoading = ref(true)
const stats = ref({
  total: 0,
  withMetaAnalysis: 0,
  totalWords: 0
})

// 获取文章列表
const fetchArticles = async () => {
  isLoading.value = true
  try {
    const response = await $fetch<{ total: number; articles: Article[] }>(
      `${config.public.apiBase}/api/v1/articles`,
      {
        params: {
          user_id: user.value?.id,
          limit: 50
        }
      }
    )

    articles.value = response.articles
    stats.value = {
      total: response.total,
      withMetaAnalysis: response.articles.filter(a => a.has_meta_analysis).length,
      totalWords: response.articles.reduce((sum, a) => sum + (a.word_count || 0), 0)
    }
  } catch (error) {
    console.error('❌ 获取文章列表失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 打开文章
const openArticle = async (articleId: number) => {
  try {
    const article = await $fetch<any>(
      `${config.public.apiBase}/api/v1/articles/${articleId}`
    )

    // 跳转到首页并加载文章
    router.push({
      path: '/',
      query: { articleId }
    })
  } catch (error) {
    console.error('❌ 获取文章失败:', error)
  }
}

// 删除文章
const deleteArticle = async (articleId: number) => {
  if (!confirm('确定要删除这篇文章吗？这将同时删除相关的元视角分析。')) {
    return
  }

  try {
    await $fetch(`${config.public.apiBase}/api/v1/articles/${articleId}`, {
      method: 'DELETE'
    })

    // 重新加载列表
    await fetchArticles()
  } catch (error) {
    console.error('❌ 删除文章失败:', error)
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`

  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}万`
  }
  return num.toString()
}

// 页面加载时获取数据
onMounted(async () => {
  if (!isAuthenticated.value) {
    // 未登录用户也可以查看（显示所有文章）
  }

  await fetchArticles()
})

// 设置页面标题
useHead({
  title: '阅读历史 - InsightReader'
})
</script>
