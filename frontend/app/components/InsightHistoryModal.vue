<template>
  <Transition
    enter-active-class="transition-opacity duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-150"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="selectedItem"
      class="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click="close"
    >
      <div
        class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
        @click.stop
      >
        <!-- 头部 -->
        <div class="p-6 border-b border-gray-200 bg-gradient-to-r from-orange-50 to-amber-50">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-orange-500 to-amber-600 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">历史洞察</h3>
                <p class="text-xs text-gray-500">{{ formatDate(selectedItem.created_at) }}</p>
              </div>
            </div>

            <button
              @click="close"
              class="p-2 rounded-lg hover:bg-white/50 transition-colors"
            >
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 内容 -->
        <div class="p-6 overflow-y-auto max-h-[calc(80vh-100px)] space-y-4">
          <!-- 选中的文本 -->
          <div>
            <div class="text-xs font-medium text-gray-500 mb-2">📌 选中的文本</div>
            <div class="p-4 bg-orange-50 border-l-4 border-orange-500 rounded-lg">
              <p class="text-gray-800 leading-relaxed">{{ selectedItem.selected_text }}</p>
            </div>
          </div>

          <!-- 问题 -->
          <div v-if="selectedItem.question">
            <div class="text-xs font-medium text-gray-500 mb-2">❓ 你的问题</div>
            <div class="p-4 bg-blue-50 rounded-lg">
              <p class="text-gray-800">{{ selectedItem.question }}</p>
            </div>
          </div>

          <div v-else>
            <div class="text-xs font-medium text-gray-500 mb-2">🎯 意图</div>
            <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-full">
              <span class="text-sm text-gray-700">{{ getIntentLabel(selectedItem.intent) }}</span>
            </div>
          </div>

          <!-- AI 回答 -->
          <div>
            <div class="text-xs font-medium text-gray-500 mb-2">💡 AI 的回答</div>
            <div class="p-4 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-lg">
              <p class="text-gray-800 leading-relaxed whitespace-pre-wrap">{{ selectedItem.insight }}</p>
            </div>
          </div>

          <!-- 推理过程 -->
          <div v-if="selectedItem.reasoning">
            <div class="text-xs font-medium text-gray-500 mb-2">🧠 推理过程</div>
            <div class="p-4 bg-purple-50 rounded-lg">
              <p class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ selectedItem.reasoning }}</p>
            </div>
          </div>
        </div>

        <!-- 底部操作按钮 -->
        <div class="p-6 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
          <button
            @click="close"
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            关闭
          </button>

          <button
            @click="handleContinueChat"
            class="px-6 py-2 bg-gradient-to-r from-orange-500 to-amber-600 text-white text-sm rounded-lg hover:from-orange-600 hover:to-amber-700 transition-all shadow-md flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            继续聊天
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import type { InsightHistoryItem } from '~/composables/useInsightReplay'

const props = defineProps<{
  selectedItem: InsightHistoryItem | null
}>()

const emit = defineEmits<{
  close: []
  continueChat: [item: InsightHistoryItem]
}>()

const close = () => {
  emit('close')
}

const handleContinueChat = () => {
  if (props.selectedItem) {
    emit('continueChat', props.selectedItem)
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getIntentLabel = (intent: string) => {
  const labels: Record<string, string> = {
    'explain': '解释说明',
    'summarize': '总结概括',
    'question': '提问',
    'expand': '展开详述',
    'analyze': '深度分析'
  }
  return labels[intent] || intent
}
</script>
