<template>
  <!-- 遮罩层：点击外部关闭 -->
  <Transition
    enter-active-class="transition-opacity duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-150"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="show"
      class="fixed inset-0 z-40"
      @click="handleClose"
    ></div>
  </Transition>

  <!-- 弹窗内容 -->
  <Transition
    enter-active-class="transition-all duration-200 ease-out"
    enter-from-class="opacity-0 scale-95 translate-y-2"
    enter-to-class="opacity-100 scale-100 translate-y-0"
    leave-active-class="transition-all duration-150 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >
    <div
      v-if="show"
      ref="popupRef"
      :style="popupStyle"
      class="fixed z-50"
    >
      <Card class="w-96 shadow-2xl border-0 overflow-hidden backdrop-blur-md bg-white/95">
        <CardContent class="p-0">
          <!-- 顶部栏：选中文本预览 + 关闭按钮 -->
          <div class="px-4 py-3 bg-gradient-to-r from-slate-50 to-zinc-50 border-b border-gray-200 flex items-start justify-between gap-2">
            <div class="flex items-start space-x-2 flex-1 min-w-0">
              <svg class="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              <p class="text-sm text-gray-700 line-clamp-2 leading-relaxed">
                "{{ selectedText }}"
              </p>
            </div>
            <!-- 关闭按钮 -->
            <button
              @click="handleClose"
              class="flex-shrink-0 w-6 h-6 rounded-full hover:bg-white/60 flex items-center justify-center transition-colors group"
              title="关闭 (Esc)"
            >
              <svg class="w-4 h-4 text-gray-500 group-hover:text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- 快捷提问按钮 -->
          <div class="p-4 space-y-2">
            <button
              v-for="intent in intents"
              :key="intent.type"
              @click="handleSelect(intent.type)"
              class="group w-full flex items-center space-x-3 px-4 py-3 text-left rounded-xl hover:bg-gradient-to-r hover:from-slate-50 hover:to-zinc-50 transition-all duration-200 border border-transparent hover:border-gray-200 hover:shadow-sm"
            >
              <div :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-all',
                intent.color
              ]">
                <component :is="intent.icon" class="w-5 h-5" />
              </div>
              <div class="flex-1">
                <div class="font-medium text-gray-900 group-hover:text-emerald-700 transition-colors">
                  {{ intent.label }}
                </div>
                <div class="text-xs text-gray-500 mt-0.5">
                  {{ intent.description }}
                </div>
              </div>
              <svg class="w-4 h-4 text-gray-400 group-hover:text-emerald-600 opacity-0 group-hover:opacity-100 transition-all transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- 附带全文开关 -->
          <div class="px-4 pb-3 border-b border-gray-100">
            <label class="flex items-center justify-between cursor-pointer group">
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div>
                  <span class="text-sm font-medium text-gray-700">附带全文</span>
                  <p class="text-xs text-gray-500">AI将参考整篇文章内容</p>
                </div>
              </div>
              <div class="relative">
                <input
                  v-model="includeFullText"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </div>
            </label>
          </div>

          <!-- 自定义问题输入 -->
          <div class="px-4 pb-4">
            <div class="pt-3 border-t border-gray-100">
              <form @submit.prevent="handleCustomQuestion" class="space-y-2">
                <div class="relative">
                  <input
                    ref="customInput"
                    v-model="customQuestion"
                    type="text"
                    placeholder="或者输入你的自定义问题..."
                    class="w-full pl-10 pr-4 py-2.5 text-sm border-2 border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 transition-all"
                    @keydown.esc="handleClose"
                  />
                  <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </div>

                <Button
                  type="submit"
                  :disabled="!customQuestion.trim()"
                  class="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md hover:shadow-lg transition-all"
                  size="sm"
                >
                  <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  立即提问
                </Button>
              </form>
            </div>
          </div>

          <!-- 快捷键提示 -->
          <div class="px-4 pb-3 flex items-center justify-between text-xs text-gray-400">
            <span>快捷键: <kbd class="px-1.5 py-0.5 bg-gray-100 rounded">Esc</kbd> 关闭</span>
            <span class="flex items-center space-x-1">
              <span class="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
              <span>AI 已就绪</span>
            </span>
          </div>
        </CardContent>
      </Card>

      <!-- 指向选中文字的小箭头 (根据位置动态显示) -->
      <div
        v-if="isAbove"
        class="absolute left-1/2 transform -translate-x-1/2 -bottom-2"
      >
        <div class="w-4 h-4 bg-white rotate-45 border-r border-b border-gray-200"></div>
      </div>
      <div
        v-else
        class="absolute left-1/2 transform -translate-x-1/2 -top-2"
      >
        <div class="w-4 h-4 bg-white rotate-45 border-l border-t border-gray-200"></div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import type { Intent } from '~/types/insight'

// Props
interface Props {
  show: boolean
  position: { x: number; y: number }
  selectedText: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  select: [intent: Intent, customQuestion?: string, includeFullText?: boolean]
  close: []
}>()

// Refs
const customQuestion = ref('')
const customInput = ref<HTMLInputElement | null>(null)
const popupRef = ref<HTMLElement | null>(null)
const includeFullText = ref(false)

// 是否显示在选中文字上方
const isAbove = ref(false)

// 计算弹窗位置
const popupStyle = computed(() => {
  if (!props.show) return {}

  const viewportHeight = window.innerHeight
  const viewportWidth = window.innerWidth
  const popupHeight = 450 // 预估弹窗高度
  const popupWidth = 384 // w-96 = 24rem = 384px
  const margin = 20 // 距离边缘的最小边距
  const arrowOffset = 16 // 箭头高度

  let x = props.position.x
  let y = props.position.y

  // 检查是否应该显示在上方
  const spaceBelow = viewportHeight - y
  const spaceAbove = y

  if (spaceBelow < popupHeight + margin && spaceAbove > spaceBelow) {
    // 显示在上方
    isAbove.value = true
    y = y - popupHeight - arrowOffset
  } else {
    // 显示在下方
    isAbove.value = false
    y = y + arrowOffset
  }

  // 检查左右边界
  let left = x
  const halfWidth = popupWidth / 2

  if (left - halfWidth < margin) {
    // 太靠左，右移
    left = halfWidth + margin
  } else if (left + halfWidth > viewportWidth - margin) {
    // 太靠右，左移
    left = viewportWidth - halfWidth - margin
  }

  // 确保不超出上下边界
  if (y < margin) {
    y = margin
  } else if (y + popupHeight > viewportHeight - margin) {
    y = viewportHeight - popupHeight - margin
  }

  return {
    left: `${left}px`,
    top: `${y}px`,
    transform: 'translateX(-50%)'
  }
})

// 意图配置
const intents = [
  {
    type: 'explain' as Intent,
    label: '这是什么意思？',
    description: '深度解析这段文字的含义',
    color: 'bg-emerald-100 text-emerald-600',
    icon: defineComponent({
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      `
    })
  },
  {
    type: 'analyze' as Intent,
    label: '作者为什么这么说？',
    description: '分析作者的观点和动机',
    color: 'bg-teal-100 text-teal-600',
    icon: defineComponent({
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      `
    })
  },
  {
    type: 'counter' as Intent,
    label: '有不同的看法吗？',
    description: '探索另一种视角和观点',
    color: 'bg-slate-100 text-slate-600',
    icon: defineComponent({
      template: `
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
        </svg>
      `
    })
  }
]

// 处理意图选择
const handleSelect = (intent: Intent) => {
  emit('select', intent, undefined, includeFullText.value)
  customQuestion.value = ''
}

// 处理自定义问题
const handleCustomQuestion = () => {
  if (customQuestion.value.trim()) {
    emit('select', 'custom', customQuestion.value, includeFullText.value)
    customQuestion.value = ''
  }
}

// 处理关闭
const handleClose = () => {
  emit('close')
  customQuestion.value = ''
}

// 监听显示状态
watch(() => props.show, (newValue) => {
  if (newValue) {
    nextTick(() => {
      // 暂不自动聚焦，让用户自己选择
    })
  }
})
</script>

<style scoped>
kbd {
  font-family: ui-monospace, monospace;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
