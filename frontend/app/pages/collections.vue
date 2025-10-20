<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader />

    <div class="max-w-6xl mx-auto px-6 py-8">
      <!-- 页头 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">我的收藏</h1>
        <p class="text-gray-600">管理你收藏的洞察卡片</p>
      </div>

      <!-- 搜索和筛选 -->
      <div class="mb-6 flex gap-4">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索收藏..."
          class="flex-1 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <select
          v-model="filterIntent"
          class="px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">全部类型</option>
          <option value="explain">解释</option>
          <option value="analyze">分析</option>
          <option value="counter">反方</option>
        </select>

        <Button @click="handleSearch">
          <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          搜索
        </Button>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="flex items-center justify-center py-20">
        <div class="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
        <span class="ml-3 text-gray-600">加载中...</span>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="collections.length === 0" class="text-center py-20">
        <svg class="w-20 h-20 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
        </svg>
        <p class="text-xl text-gray-600 mb-2">还没有收藏</p>
        <p class="text-gray-500 mb-6">开始阅读并收藏有价值的洞察吧</p>
        <NuxtLink to="/">
          <Button>开始阅读</Button>
        </NuxtLink>
      </div>

      <!-- 收藏列表 -->
      <div v-else class="space-y-4">
        <Card
          v-for="item in collections"
          :key="item.id"
          class="hover:shadow-lg transition-shadow cursor-pointer"
          @click="handleViewInsight(item)"
        >
          <CardContent class="p-6">
            <!-- 头部：时间和意图 -->
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <span class="px-3 py-1 text-xs font-medium rounded-full" :class="getIntentClass(item.intent)">
                  {{ getIntentLabel(item.intent) }}
                </span>
                <span class="text-sm text-gray-500">
                  {{ formatDate(item.created_at) }}
                </span>
              </div>

              <!-- 删除按钮 -->
              <Button
                variant="ghost"
                size="sm"
                @click.stop="handleDelete(item.id)"
                class="text-red-600 hover:text-red-700"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </Button>
            </div>

            <!-- 选中的文本 -->
            <p class="font-medium text-gray-900 mb-3 line-clamp-2">
              "{{ item.selected_text }}"
            </p>

            <!-- 洞察摘要 -->
            <p class="text-sm text-gray-600 mb-3 line-clamp-3">
              {{ item.insight.substring(0, 200) }}{{ item.insight.length > 200 ? '...' : '' }}
            </p>

            <!-- 文章标题 -->
            <div v-if="item.article_title" class="text-xs text-gray-500">
              来自: {{ item.article_title }}
            </div>
          </CardContent>
        </Card>

        <!-- 加载更多 -->
        <div v-if="total > collections.length" class="text-center py-6">
          <Button variant="outline" @click="loadMore" :disabled="isLoading">
            加载更多
          </Button>
        </div>

        <!-- 统计信息 -->
        <div class="text-center text-sm text-gray-500 py-4">
          已显示 {{ collections.length }} / {{ total }} 条收藏
        </div>
      </div>
    </div>

    <!-- 查看洞察详情弹窗 -->
    <Transition name="fade">
      <div v-if="selectedInsight" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-6">
        <Card class="w-full max-w-3xl max-h-[90vh] overflow-y-auto">
          <CardContent class="p-6">
            <!-- 关闭按钮 -->
            <div class="flex justify-end mb-4">
              <Button variant="ghost" size="sm" @click="selectedInsight = null">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </Button>
            </div>

            <!-- 元信息 -->
            <div class="mb-4 pb-4 border-b">
              <div class="flex items-center gap-3 mb-2">
                <span class="px-3 py-1 text-xs font-medium rounded-full" :class="getIntentClass(selectedInsight.intent)">
                  {{ getIntentLabel(selectedInsight.intent) }}
                </span>
                <span class="text-sm text-gray-500">
                  {{ formatDate(selectedInsight.created_at) }}
                </span>
              </div>
              <p class="font-medium text-gray-900">"{{ selectedInsight.selected_text }}"</p>
              <p v-if="selectedInsight.article_title" class="text-sm text-gray-500 mt-1">
                来自: {{ selectedInsight.article_title }}
              </p>
            </div>

            <!-- 洞察内容 -->
            <div class="prose prose-sm max-w-none" v-html="renderMarkdown(selectedInsight.insight)"></div>
          </CardContent>
        </Card>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import type { InsightCardResponse } from '~/types/collection'
import type { Intent } from '~/types/insight'

const router = useRouter()
const { isAuthenticated } = useAuth()
const { collections, total, isLoading, error, fetchCollections, deleteCollection } = useCollections()

const searchKeyword = ref('')
const filterIntent = ref<Intent | ''>('')
const selectedInsight = ref<InsightCardResponse | null>(null)
const currentPage = ref(0)
const pageSize = 20

// 检查登录状态
onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }

  // 加载收藏列表
  await handleSearch()
})

// 搜索
const handleSearch = async () => {
  currentPage.value = 0
  await fetchCollections({
    skip: 0,
    limit: pageSize,
    intent: filterIntent.value || undefined,
    search: searchKeyword.value || undefined
  })
}

// 加载更多
const loadMore = async () => {
  currentPage.value++
  await fetchCollections({
    skip: currentPage.value * pageSize,
    limit: pageSize,
    intent: filterIntent.value || undefined,
    search: searchKeyword.value || undefined
  })
}

// 查看洞察详情
const handleViewInsight = (item: InsightCardResponse) => {
  selectedInsight.value = item
}

// 删除收藏
const handleDelete = async (id: number) => {
  if (!confirm('确定要删除这条收藏吗？')) return

  const result = await deleteCollection(id)

  if (!result.success) {
    alert(result.error || '删除失败')
  }
}

// 渲染 Markdown
const renderMarkdown = (text: string) => {
  return marked(text)
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取意图标签
const getIntentLabel = (intent: Intent) => {
  const labels = {
    explain: '解释',
    analyze: '分析',
    counter: '反方'
  }
  return labels[intent]
}

// 获取意图样式类
const getIntentClass = (intent: Intent) => {
  const classes = {
    explain: 'bg-blue-50 text-blue-600',
    analyze: 'bg-green-50 text-green-600',
    counter: 'bg-purple-50 text-purple-600'
  }
  return classes[intent]
}

// 页面元信息
useHead({
  title: '我的收藏 - InsightReader',
  meta: [
    { name: 'description', content: '查看和管理你的洞察收藏' }
  ]
})
</script>

<style scoped>
.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.line-clamp-3 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
