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
        class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[85vh] overflow-hidden flex flex-col"
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
                <h3 class="text-lg font-bold text-gray-900">对话记录</h3>
                <p class="text-xs text-gray-500">{{ formatDate(selectedItem.created_at) }} · 共 {{ messageCount }} 条对话</p>
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

        <!-- 原始选中文本 -->
        <div class="px-6 pt-4 pb-2 bg-orange-50/50">
          <div class="text-xs font-medium text-gray-500 mb-2">📌 选中的文本</div>
          <div class="p-3 bg-white border-l-4 border-orange-500 rounded-lg">
            <p class="text-sm text-gray-800 leading-relaxed">{{ selectedItem.selected_text }}</p>
          </div>
        </div>

        <!-- 对话历史 -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4">
          <div
            v-for="(message, index) in selectedItem.messages"
            :key="index"
            :class="[
              'flex',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              :class="[
                'max-w-[85%] rounded-xl p-4 shadow-sm',
                message.role === 'user'
                  ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                  : 'bg-gradient-to-br from-emerald-50 to-teal-50 text-gray-800'
              ]"
            >
              <!-- 角色标签 -->
              <div class="flex items-center gap-2 mb-2">
                <span :class="[
                  'text-xs font-medium',
                  message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                ]">
                  {{ message.role === 'user' ? '👤 你' : '🤖 AI' }}
                </span>
                <span :class="[
                  'text-xs',
                  message.role === 'user' ? 'text-blue-200' : 'text-gray-400'
                ]">
                  {{ formatTimestamp(message.timestamp) }}
                </span>
              </div>

              <!-- 消息内容 -->
              <div class="prose prose-sm max-w-none">
                <p :class="[
                  'leading-relaxed whitespace-pre-wrap',
                  message.role === 'user' ? 'text-white' : 'text-gray-800'
                ]">
                  {{ message.content }}
                </p>
              </div>

              <!-- 推理过程（仅 AI 消息） -->
              <div v-if="message.reasoning && message.role === 'assistant'" class="mt-3 pt-3 border-t border-teal-200">
                <div class="flex items-center gap-1 text-xs font-medium text-purple-600 mb-2">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span>推理过程</span>
                </div>
                <p class="text-xs text-gray-600 leading-relaxed whitespace-pre-wrap">
                  {{ message.reasoning }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部操作按钮 -->
        <div class="p-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
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
import type { InsightConversation } from '~/composables/useInsightReplay'
import { computed } from 'vue'

const props = defineProps<{
  selectedItem: InsightConversation | null
}>()

const emit = defineEmits<{
  close: []
  continueChat: [item: InsightConversation]
}>()

const messageCount = computed(() => props.selectedItem?.messages.length || 0)

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

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
