<template>
  <div class="mb-4 bg-white/80 backdrop-blur-md border border-gray-200/50 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all">
    <!-- 卡片头部 -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <div :class="['w-8 h-8 rounded-lg flex items-center justify-center', iconBgClass]">
          <component :is="icon" class="w-5 h-5 text-white" />
        </div>
        <h4 class="text-sm font-semibold text-gray-800">{{ title }}</h4>
      </div>

      <!-- 置信度指示器 -->
      <div v-if="confidence !== undefined && confidence !== null" class="flex items-center gap-1">
        <div class="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            :class="['h-full rounded-full transition-all', confidenceColorClass]"
            :style="{ width: `${confidence * 100}%` }"
          ></div>
        </div>
        <span class="text-xs text-gray-500">{{ Math.round(confidence * 100) }}%</span>
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="space-y-2">
      <slot />
    </div>

    <!-- 反馈按钮 -->
    <div class="mt-3 flex items-center justify-end gap-2">
      <button
        @click="$emit('feedback', 'helpful')"
        :class="[
          'p-1.5 rounded-lg transition-colors',
          feedbackGiven === 'helpful' ? 'bg-emerald-100' : 'hover:bg-gray-100'
        ]"
        title="有帮助"
      >
        <svg
          :class="[
            'w-4 h-4 transition-colors',
            feedbackGiven === 'helpful' ? 'text-emerald-600' : 'text-gray-400 hover:text-emerald-600'
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
        </svg>
      </button>
      <button
        @click="$emit('feedback', 'not-helpful')"
        :class="[
          'p-1.5 rounded-lg transition-colors',
          feedbackGiven === 'not-helpful' ? 'bg-red-100' : 'hover:bg-gray-100'
        ]"
        title="不准确"
      >
        <svg
          :class="[
            'w-4 h-4 transition-colors',
            feedbackGiven === 'not-helpful' ? 'text-red-600' : 'text-gray-400 hover:text-red-600'
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
  title: string
  icon: any  // Component
  iconBgClass: string
  confidence?: number
}>()

const emit = defineEmits<{
  feedback: [type: 'helpful' | 'not-helpful']
}>()

const feedbackGiven = ref<'helpful' | 'not-helpful' | null>(null)

const confidenceColorClass = computed(() => {
  if (props.confidence === undefined || props.confidence === null) return ''

  if (props.confidence >= 0.8) return 'bg-emerald-500'
  if (props.confidence >= 0.6) return 'bg-yellow-500'
  return 'bg-orange-500'
})

// 监听反馈事件并记录
const handleFeedback = (type: 'helpful' | 'not-helpful') => {
  feedbackGiven.value = type
  emit('feedback', type)
}
</script>
