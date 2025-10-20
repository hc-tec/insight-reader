<template>
  <div class="p-6 h-full flex flex-col">
    <!-- 标题栏 -->
    <div class="mb-6">
      <div class="flex items-center gap-2 mb-2">
        <div class="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h2 class="text-lg font-semibold text-gray-900">AI 洞察</h2>
      </div>
      <p class="text-sm text-gray-500">深度解析你选中的内容</p>
    </div>

    <!-- 内容区域 -->
    <div class="flex-1 overflow-auto">
      <!-- 错误状态 -->
      <Transition
        enter-active-class="transition-all duration-300"
        enter-from-class="opacity-0 translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
      >
        <div v-if="error" class="bg-red-50 border-l-4 border-red-500 rounded-r-lg p-4 mb-4">
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p class="text-red-800 text-sm font-medium mb-1">出错了</p>
              <p class="text-red-700 text-sm">{{ error }}</p>
            </div>
          </div>
        </div>
      </Transition>

      <!-- 洞察内容 -->
      <Transition
        enter-active-class="transition-all duration-300"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        mode="out-in"
      >
        <div v-if="insight || reasoning || isLoading" key="content">
          <!-- 加载中的提示（仅在非推理模式或推理内容也为空时显示） -->
          <div v-if="isLoading && !insight && !reasoning" class="flex items-center gap-3 text-gray-700 mb-6 p-4 bg-emerald-50 rounded-xl border border-emerald-100">
            <div class="relative">
              <div class="animate-spin h-5 w-5 border-2 border-emerald-600 border-t-transparent rounded-full"></div>
              <div class="absolute inset-0 animate-ping h-5 w-5 border-2 border-emerald-400 border-t-transparent rounded-full opacity-20"></div>
            </div>
            <div>
              <p class="text-sm font-semibold">AI 正在思考...</p>
              <p class="text-xs text-gray-600 mt-0.5">正在为你生成深度洞察</p>
            </div>
          </div>

          <!-- 实时显示生成的内容（推理模式下即使 insight 为空也显示） -->
          <div v-if="insight || reasoning || (isLoading && useReasoning)" class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <!-- 操作按钮栏 -->
            <div v-if="!isLoading" class="px-6 py-4 bg-gradient-to-r from-gray-50 to-white border-b border-gray-100 flex justify-end gap-2">
              <!-- 暂存按钮 -->
              <button
                v-if="!isStashed"
                @click="handleStash"
                :disabled="isStashing"
                class="px-3 py-1.5 text-sm font-medium rounded-lg transition-all flex items-center gap-1.5"
                :class="[
                  isStashing
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-100 hover:border-amber-300'
                ]"
              >
                <svg v-if="!isStashing" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
                <div v-else class="animate-spin h-4 w-4 border-2 border-amber-600 border-t-transparent rounded-full"></div>
                <span>{{ isStashing ? '暂存中...' : '📌 暂存' }}</span>
              </button>
              <div v-else class="flex items-center gap-2 text-amber-700 text-sm px-3 py-1.5 bg-amber-50 rounded-lg border border-amber-200">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span class="font-medium">已暂存</span>
              </div>

              <!-- 收藏按钮（需要登录） -->
              <Button
                v-if="isAuthenticated && !saveSuccess"
                variant="outline"
                size="sm"
                @click="handleSaveToCollection"
                :disabled="isSaving"
                class="hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-all"
              >
                <svg v-if="!isSaving" class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
                <div v-else class="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full mr-2"></div>
                {{ isSaving ? '收藏中...' : '收藏此洞察' }}
              </Button>
              <div v-else-if="isAuthenticated && saveSuccess" class="flex items-center gap-2 text-green-700 text-sm px-3 py-1.5 bg-green-50 rounded-lg border border-green-200">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span class="font-medium">已收藏</span>
              </div>
            </div>

            <!-- 内容区 -->
            <div class="px-6 py-6">
              <!-- 推理内容（推理模式下始终显示，支持流式更新） -->
              <div v-if="useReasoning || reasoning" class="mb-6">
                <button
                  @click="showReasoning = !showReasoning"
                  class="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-emerald-700 transition-colors mb-3"
                >
                  <svg :class="['w-4 h-4 transition-transform', showReasoning && 'rotate-90']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  <span>思维链</span>
                  <span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-700">推理模式</span>
                </button>

                <!-- 推理内容区域（移除 Transition，直接显示以支持流式更新） -->
                <div v-if="showReasoning" class="p-4 bg-gray-50 rounded-xl border border-gray-200 mb-6 overflow-hidden">
                  <!-- 推理内容为空且正在加载时显示提示 -->
                  <div v-if="!reasoning && isLoading" class="flex items-center gap-2 text-gray-500 text-sm">
                    <div class="animate-spin h-4 w-4 border-2 border-emerald-600 border-t-transparent rounded-full"></div>
                    <span>AI 正在推理中...</span>
                  </div>
                  <!-- 推理内容 -->
                  <div v-else class="prose prose-sm max-w-none text-gray-700" v-html="renderedReasoning"></div>
                  <!-- 推理过程中显示光标 -->
                  <span v-if="isLoading && reasoning" class="inline-block w-0.5 h-5 bg-emerald-600 animate-blink ml-1 align-middle"></span>
                </div>
              </div>

              <!-- 正常内容 -->
              <div class="prose prose-sm max-w-none" v-html="renderedInsight"></div>

              <!-- 流式加载时显示光标 -->
              <span v-if="isLoading" class="inline-block w-0.5 h-5 bg-emerald-600 animate-blink ml-1 align-middle"></span>

              <!-- 追问功能区域（洞察生成完成后显示） -->
              <div v-if="!isLoading && insight" class="mt-6 pt-6 border-t border-gray-100">
                <!-- 对话历史（包括正在生成的内容） -->
                <ConversationThread
                  v-if="conversationHistory.length > 0 || (isGeneratingAnswer && currentAnswer)"
                  :messages="conversationHistory"
                  :is-generating="isGeneratingAnswer"
                  :current-answer="currentAnswer"
                  class="mb-6"
                />

                <!-- 追问按钮 -->
                <FollowUpButtons
                  :buttons="followUpButtons"
                  :loading="isGeneratingButtons || isGeneratingAnswer"
                  :disabled="isGeneratingAnswer"
                  @select="handleFollowUpSelect"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 空白状态 -->
        <div v-else key="empty" class="text-center py-20 animate-fade-in">
          <div class="mb-6 relative">
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="w-24 h-24 bg-emerald-100 rounded-full animate-pulse opacity-20"></div>
            </div>
            <svg class="w-20 h-20 mx-auto text-emerald-500 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-700 mb-3">等待你的提问</h3>
          <p class="text-gray-500 mb-2">在左侧文章中选中文字</p>
          <p class="text-sm text-gray-400">AI 会帮你深度理解选中的内容</p>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import type { InsightRequest } from '~/types/insight'

const props = defineProps<{
  insight: string
  reasoning: string
  isLoading: boolean
  error: string
  currentRequest?: InsightRequest
  useReasoning?: boolean
}>()

const { isAuthenticated } = useAuth()
const { saveInsight } = useCollections()
const { addToStash, isStashed: checkIsStashed } = useStash()
const {
  conversationHistory,
  followUpButtons,
  isGeneratingButtons,
  isGeneratingAnswer,
  currentAnswer,
  generateButtons,
  askFollowUp,
  clearConversation
} = useFollowUp()

// 收藏相关
const isSaving = ref(false)
const saveSuccess = ref(false)

// 暂存相关
const isStashing = ref(false)
const isStashed = computed(() => {
  if (!props.insight || !props.currentRequest) return false
  return checkIsStashed(props.currentRequest.selected_text, props.insight)
})

// 推理内容显示
const showReasoning = ref(true)

// Markdown 渲染
const renderedInsight = computed(() => {
  if (!props.insight) return ''
  return marked(props.insight, { breaks: true })
})

const renderedReasoning = computed(() => {
  if (!props.reasoning) return ''
  return marked(props.reasoning, { breaks: true })
})

// 当有推理内容时，自动展开
watch(() => props.reasoning, (newValue) => {
  if (newValue && newValue.length > 0) {
    showReasoning.value = true
  }
})

// 当洞察生成完成时，自动生成追问按钮
watch(() => [props.insight, props.isLoading] as const, ([insight, loading], [prevInsight, prevLoading]) => {
  // 当洞察从加载状态变为完成状态时
  if (!loading && prevLoading && insight && props.currentRequest) {
    generateButtons(
      props.currentRequest.selected_text,
      insight,
      props.currentRequest.intent
    )
  }
})

// 监听 insight 变化，重置状态
watch(() => props.insight, (newInsight, oldInsight) => {
  if (newInsight !== oldInsight && newInsight) {
    // 新的洞察生成，重置状态
    saveSuccess.value = false
    clearConversation() // 清空对话历史
  }
})

// 保存到收藏
const handleSaveToCollection = async () => {
  if (!props.currentRequest) {
    alert('无法保存：缺少请求信息')
    return
  }

  isSaving.value = true

  const result = await saveInsight({
    selected_text: props.currentRequest.selected_text,
    context: props.currentRequest.context,
    intent: props.currentRequest.intent,
    custom_question: props.currentRequest.custom_question,
    insight: props.insight
  })

  isSaving.value = false

  if (result.success) {
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)
  } else {
    alert(result.error || '收藏失败')
  }
}

// 暂存到本地
const handleStash = async () => {
  if (!props.currentRequest || !props.insight) {
    alert('无法暂存：缺少内容')
    return
  }

  isStashing.value = true

  try {
    addToStash({
      selectedText: props.currentRequest.selected_text,
      context: props.currentRequest.context,
      intent: props.currentRequest.intent,
      customQuestion: props.currentRequest.custom_question,
      insight: props.insight,
      reasoning: props.reasoning || undefined,
      conversationHistory: conversationHistory.value.length > 0 ? [...conversationHistory.value] : undefined
    })

    console.log('✅ 暂存成功')

    // 延迟重置状态
    setTimeout(() => {
      isStashing.value = false
    }, 500)
  } catch (error) {
    console.error('暂存失败:', error)
    alert('暂存失败')
    isStashing.value = false
  }
}

// 处理追问选择
const handleFollowUpSelect = async (question: string) => {
  if (!props.currentRequest || !props.insight) return

  const useReasoning = useState('use-reasoning', () => false)

  await askFollowUp(
    props.currentRequest.selected_text,
    props.insight,
    question,
    useReasoning.value
  )

  // 追问完成后，重新生成追问按钮
  if (currentAnswer.value) {
    generateButtons(
      props.currentRequest.selected_text,
      props.insight,
      props.currentRequest.intent
    )
  }
}
</script>

<style scoped>
/* Markdown 样式 */
.prose {
  color: #374151;
  line-height: 1.8;
}

.prose :deep(p) {
  margin-bottom: 1em;
}

.prose :deep(h1),
.prose :deep(h2),
.prose :deep(h3) {
  font-weight: 600;
  margin-top: 1.5em;
  margin-bottom: 0.75em;
  color: #1f2937;
}

.prose :deep(h1) {
  font-size: 1.5em;
}

.prose :deep(h2) {
  font-size: 1.25em;
}

.prose :deep(h3) {
  font-size: 1.1em;
}

.prose :deep(ul),
.prose :deep(ol) {
  margin: 1em 0;
  padding-left: 1.5em;
}

.prose :deep(li) {
  margin: 0.5em 0;
}

.prose :deep(code) {
  background: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-size: 0.9em;
  color: #e11d48;
}

.prose :deep(pre) {
  background: #1f2937;
  color: #f3f4f6;
  padding: 1em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin: 1em 0;
}

.prose :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
}

.prose :deep(blockquote) {
  border-left: 4px solid #3b82f6;
  padding-left: 1em;
  margin: 1em 0;
  color: #6b7280;
  font-style: italic;
}

.prose :deep(strong) {
  font-weight: 600;
  color: #1f2937;
}

/* 光标闪烁动画 */
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

/* 淡入动画 */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}
</style>
