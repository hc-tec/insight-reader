<template>
  <div class="stash-panel h-full flex flex-col">
    <!-- 头部 -->
    <div class="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">
            暂存
            <span v-if="stats.count > 0" class="text-emerald-600">({{ stats.count }})</span>
          </h3>
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="stats.count > 0"
            @click="showExportDialog = true"
            class="px-3 py-1.5 text-sm font-medium text-emerald-700 bg-emerald-100 hover:bg-emerald-200 rounded-lg transition-colors flex items-center gap-1"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>导出</span>
          </button>
          <button
            v-if="stats.count > 0"
            @click="handleClearAll"
            class="px-3 py-1.5 text-sm font-medium text-red-700 bg-red-50 hover:bg-red-100 rounded-lg transition-colors flex items-center gap-1"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span>清空</span>
          </button>
        </div>
      </div>

      <!-- 统计信息 -->
      <div v-if="stats.count > 0" class="flex items-center gap-4 text-xs text-gray-600">
        <span>📝 {{ stats.totalWords }} 字</span>
        <span v-if="stats.hasConversations">💬 {{ stats.totalConversations }} 条对话</span>
        <span v-if="stats.hasReasoning">🧠 含推理内容</span>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="flex-1 overflow-auto">
      <!-- 空状态 -->
      <div v-if="stashItems.length === 0" class="flex flex-col items-center justify-center h-full text-center py-20 px-6">
        <div class="mb-6 relative">
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="w-24 h-24 bg-gray-100 rounded-full animate-pulse opacity-20"></div>
          </div>
          <svg class="w-20 h-20 mx-auto text-gray-300 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">暂存区为空</h3>
        <p class="text-sm text-gray-500 mb-1">在洞察卡片上点击"暂存"按钮</p>
        <p class="text-xs text-gray-400">可以保存多个洞察，阅读结束后一键导出</p>
      </div>

      <!-- 暂存列表 -->
      <div v-else class="p-4 space-y-3">
        <div
          v-for="(item, index) in stashItems"
          :key="item.id"
          class="stash-item bg-white rounded-xl border border-gray-200 hover:border-emerald-300 hover:shadow-md transition-all overflow-hidden"
        >
          <!-- 卡片头部 -->
          <div class="px-4 py-3 bg-gradient-to-r from-gray-50 to-white border-b border-gray-100">
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1 min-w-0">
                <h4 class="text-sm font-medium text-gray-900 truncate mb-1">
                  {{ index + 1 }}. "{{ truncate(item.selectedText, 40) }}"
                </h4>
                <div class="flex items-center gap-3 text-xs text-gray-500">
                  <span class="flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ formatTime(item.timestamp) }}
                  </span>
                  <span>{{ getIntentLabel(item.intent) }}</span>
                  <span>{{ item.insight.length }} 字</span>
                </div>
              </div>
              <div class="flex items-center gap-1">
                <button
                  @click="viewItem(item)"
                  class="p-1.5 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded transition-colors"
                  title="查看详情"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button
                  @click="removeItem(item.id)"
                  class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="移除"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 卡片预览内容 -->
          <div class="px-4 py-3">
            <p class="text-sm text-gray-600 line-clamp-2">
              {{ truncate(item.insight, 100) }}
            </p>
            <div v-if="item.conversationHistory && item.conversationHistory.length > 0" class="mt-2 flex items-center gap-1 text-xs text-emerald-600">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <span>含 {{ item.conversationHistory.length / 2 }} 轮对话</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出对话框 -->
    <ExportDialog
      :show="showExportDialog"
      :items="stashItems"
      @close="showExportDialog = false"
      @exported="handleExported"
    />
  </div>
</template>

<script setup lang="ts">
import type { StashItem } from '~/types/stash'
import type { Intent } from '~/types/insight'

const emit = defineEmits<{
  viewItem: [item: StashItem]
}>()

const { stashItems, removeFromStash, clearStash, getStats } = useStash()
const { formatTime, getIntentLabel } = useExport()

const showExportDialog = ref(false)

// 统计信息
const stats = computed(() => getStats())

// 截断文本
const truncate = (text: string, maxLength: number) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 移除单个项目
const removeItem = (id: string) => {
  if (confirm('确定要移除这个暂存的洞察吗？')) {
    removeFromStash(id)
  }
}

// 清空所有
const handleClearAll = () => {
  if (confirm(`确定要清空所有 ${stats.value.count} 个暂存的洞察吗？此操作不可恢复。`)) {
    clearStash()
  }
}

// 查看详情
const viewItem = (item: StashItem) => {
  emit('viewItem', item)
}

// 导出成功后的处理
const handleExported = () => {
  console.log('✅ 导出成功')
  // 可以选择是否清空暂存
  // clearStash()
}
</script>

<style scoped>
.stash-item {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 文本截断 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
