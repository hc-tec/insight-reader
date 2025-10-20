<template>
  <div v-if="messages.length > 0" class="conversation-thread">
    <!-- 折叠/展开按钮 -->
    <button
      @click="collapsed = !collapsed"
      class="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-emerald-700 transition-colors mb-3"
    >
      <svg
        :class="['w-4 h-4 transition-transform', !collapsed && 'rotate-90']"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
      <span>📝 对话历史</span>
      <span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-700">
        {{ Math.floor(messages.length / 2) }} 轮
      </span>
    </button>

    <!-- 对话内容 -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-screen"
      leave-active-class="transition-all duration-200"
      leave-from-class="opacity-100 max-h-screen"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="!collapsed" class="space-y-4 overflow-hidden">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="message-item"
          :class="msg.role"
        >
          <!-- 消息标签 -->
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-xs font-medium">
              {{ msg.role === 'user' ? '🙋 你的追问' : '🤖 AI 的回答' }}
            </span>
            <span v-if="msg.timestamp" class="text-xs text-gray-400">
              {{ formatTime(msg.timestamp) }}
            </span>
          </div>

          <!-- 消息内容 -->
          <div
            class="message-content pl-4 border-l-2 transition-colors"
            :class="[
              msg.role === 'user'
                ? 'border-blue-300 bg-blue-50/30'
                : 'border-emerald-300 bg-emerald-50/30'
            ]"
          >
            <div
              v-if="msg.role === 'assistant'"
              class="prose prose-sm max-w-none"
              v-html="renderMarkdown(msg.content)"
            ></div>
            <p v-else class="text-sm text-gray-700 py-2">
              {{ msg.content }}
            </p>
          </div>
        </div>

        <!-- 当前正在生成的回答 -->
        <div v-if="isGenerating && currentAnswer" class="message-item assistant">
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-xs font-medium">🤖 AI 的回答</span>
            <div class="flex items-center gap-1 text-xs text-emerald-600">
              <div class="animate-spin h-3 w-3 border-2 border-emerald-600 border-t-transparent rounded-full"></div>
              <span>生成中...</span>
            </div>
          </div>

          <div class="message-content pl-4 border-l-2 border-emerald-300 bg-emerald-50/30">
            <div class="prose prose-sm max-w-none" v-html="renderMarkdown(currentAnswer)"></div>
            <span class="inline-block w-0.5 h-4 bg-emerald-600 animate-blink ml-1 align-middle"></span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import type { Message } from '~/types/followup'

const props = defineProps<{
  messages: Message[]
  isGenerating?: boolean
  currentAnswer?: string
}>()

const collapsed = ref(false)

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 小于 1 分钟
  if (diff < 60000) {
    return '刚刚'
  }
  // 小于 1 小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)} 分钟前`
  }
  // 小于 24 小时
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)} 小时前`
  }
  // 否则显示完整时间
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 渲染 Markdown
const renderMarkdown = (content: string) => {
  if (!content) return ''
  return marked(content, { breaks: true })
}

// 监听消息变化，新消息到达时自动展开
watch(() => props.messages.length, (newLength, oldLength) => {
  if (newLength > oldLength) {
    collapsed.value = false
  }
})
</script>

<style scoped>
.message-item {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.message-content {
  padding: 0.75rem;
  border-radius: 0.5rem;
}

/* 继承 InsightPane 的 Markdown 样式 */
.prose :deep(p) {
  margin-bottom: 0.75em;
}

.prose :deep(code) {
  background: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-size: 0.9em;
  color: #e11d48;
}

.prose :deep(ul),
.prose :deep(ol) {
  margin: 0.75em 0;
  padding-left: 1.5em;
}

.prose :deep(li) {
  margin: 0.25em 0;
}

/* 光标闪烁 */
@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

.animate-blink {
  animation: blink 1s infinite;
}
</style>
