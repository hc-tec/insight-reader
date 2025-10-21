<template>
  <div>
    <!-- 历史记录侧边栏 -->
    <Transition name="slide">
      <div
        v-if="isOpen"
        class="fixed inset-y-0 right-0 w-96 bg-white shadow-2xl z-50 flex flex-col"
      >
        <!-- 头部 -->
        <div class="p-4 border-b flex items-center justify-between">
          <h2 class="text-lg font-semibold">历史记录</h2>
          <div class="flex items-center gap-2">
            <Button
              v-if="history.length > 0"
              variant="ghost"
              size="sm"
              @click="handleClearAll"
            >
              清空
            </Button>
            <Button
              variant="ghost"
              size="sm"
              @click="emit('close')"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          </div>
        </div>

        <!-- 搜索框 -->
        <div class="p-4 border-b">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索历史记录..."
            class="w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- 历史记录列表 -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3">
          <div
            v-if="filteredHistory.length === 0"
            class="text-center text-gray-400 mt-10"
          >
            <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-sm">{{ searchKeyword ? '没有找到相关记录' : '暂无历史记录' }}</p>
          </div>

          <Card
            v-for="item in filteredHistory"
            :key="item.id"
            class="cursor-pointer hover:shadow-md transition-shadow"
            @click="handleSelectItem(item)"
          >
            <CardContent class="p-3">
              <!-- 时间和意图 -->
              <div class="flex items-center justify-between mb-2 text-xs text-gray-500">
                <span>{{ formatTime(item.timestamp) }}</span>
                <span class="px-2 py-0.5 bg-blue-50 text-blue-600 rounded">
                  {{ getIntentLabel(item.intent) }}
                </span>
              </div>

              <!-- 选中的文本 -->
              <p class="text-sm font-medium text-gray-900 mb-2 line-clamp-2">
                "{{ item.selectedText }}"
              </p>

              <!-- 洞察摘要 -->
              <p class="text-xs text-gray-600 line-clamp-2">
                {{ item.insight.substring(0, 100) }}{{ item.insight.length > 100 ? '...' : '' }}
              </p>

              <!-- 文章标题 -->
              <p v-if="item.articleTitle" class="text-xs text-gray-400 mt-2">
                来自: {{ item.articleTitle }}
              </p>

              <!-- 删除按钮 -->
              <Button
                variant="ghost"
                size="sm"
                class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                @click.stop="deleteHistoryItem(item.id)"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </Transition>

    <!-- 遮罩层 -->
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 bg-black bg-opacity-30 z-40"
        @click="emit('close')"
      />
    </Transition>
  </div>
</template>

<script setup lang="ts">
import type { HistoryItem } from '~/types/history'
import type { Intent } from '~/types/insight'

const props = defineProps<{
  isOpen: boolean
}>()

const { history, deleteHistoryItem, clearHistory, searchHistory } = useHistory()
const searchKeyword = ref('')

const emit = defineEmits<{
  select: [item: HistoryItem]
  close: []
}>()

// 过滤后的历史记录
const filteredHistory = computed(() => {
  if (!searchKeyword.value) {
    return history.value
  }
  return searchHistory(searchKeyword.value)
})

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }

  // 小于1小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }

  // 小于24小时
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }

  // 小于7天
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  }

  // 显示完整日期
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
  return labels[intent] || intent
}

// 选择历史记录项
const handleSelectItem = (item: HistoryItem) => {
  emit('select', item)
  emit('close')
}

// 清空所有记录
const handleClearAll = () => {
  if (confirm('确定要清空所有历史记录吗？此操作不可恢复。')) {
    clearHistory()
  }
}
</script>

<style scoped>
/* 滑入动画 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 文本截断 */
.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
</style>
