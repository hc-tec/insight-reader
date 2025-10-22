<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  showProgress?: boolean
  showCancel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showProgress: true,
  showCancel: false
})

const emit = defineEmits<{
  cancel: []
}>()

// 进度条颜色
const progressColor = computed(() => {
  switch (props.status) {
    case 'processing':
      return 'bg-gradient-to-r from-blue-500 to-cyan-500'
    case 'completed':
      return 'bg-gradient-to-r from-green-500 to-emerald-500'
    case 'failed':
      return 'bg-gradient-to-r from-red-500 to-rose-500'
    default:
      return 'bg-gray-400'
  }
})

// 状态图标
const statusIcon = computed(() => {
  switch (props.status) {
    case 'processing':
      return 'i-heroicons-arrow-path' // 加载中
    case 'completed':
      return 'i-heroicons-check-circle' // 完成
    case 'failed':
      return 'i-heroicons-x-circle' // 失败
    default:
      return 'i-heroicons-clock' // 等待
  }
})

// 状态文本颜色
const statusTextColor = computed(() => {
  switch (props.status) {
    case 'processing':
      return 'text-blue-600 dark:text-blue-400'
    case 'completed':
      return 'text-green-600 dark:text-green-400'
    case 'failed':
      return 'text-red-600 dark:text-red-400'
    default:
      return 'text-gray-600 dark:text-gray-400'
  }
})

// 图标动画
const iconAnimation = computed(() => {
  return props.status === 'processing' ? 'animate-spin' : ''
})
</script>

<template>
  <div class="task-progress-container">
    <!-- 状态指示器 -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <div
          :class="[statusIcon, iconAnimation, statusTextColor]"
          class="w-5 h-5"
        />
        <span :class="statusTextColor" class="text-sm font-medium">
          {{ message || '处理中...' }}
        </span>
      </div>

      <!-- 取消按钮 -->
      <button
        v-if="showCancel && status === 'processing'"
        @click="emit('cancel')"
        class="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
      >
        取消
      </button>
    </div>

    <!-- 进度条 -->
    <div v-if="showProgress" class="progress-bar-container">
      <div class="progress-bar-track">
        <div
          :class="progressColor"
          :style="{ width: `${progress}%` }"
          class="progress-bar-fill"
        />
      </div>

      <!-- 进度百分比 -->
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">
        {{ progress }}%
      </div>
    </div>

    <!-- 错误信息提示 -->
    <div
      v-if="status === 'failed' && $slots.error"
      class="mt-2 text-xs text-red-600 dark:text-red-400"
    >
      <slot name="error" />
    </div>

    <!-- 完成提示 -->
    <div
      v-if="status === 'completed' && $slots.success"
      class="mt-2 text-xs text-green-600 dark:text-green-400"
    >
      <slot name="success" />
    </div>
  </div>
</template>

<style scoped>
.task-progress-container {
  @apply p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm;
}

.progress-bar-container {
  @apply w-full;
}

.progress-bar-track {
  @apply w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden;
}

.progress-bar-fill {
  @apply h-full transition-all duration-500 ease-out;
}

/* 脉冲动画（可选） */
@keyframes pulse-subtle {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.progress-bar-fill.processing {
  animation: pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
