<template>
  <div class="follow-up-section">
    <!-- 标题 -->
    <p class="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
      <span>💬</span>
      <span>继续深入？</span>
    </p>

    <!-- 预设按钮 -->
    <div class="flex flex-wrap gap-2 mb-3">
      <button
        v-for="btn in buttons"
        :key="btn.id"
        @click="handleButtonClick(btn)"
        :disabled="disabled || loading"
        class="px-3 py-2 text-sm rounded-lg border transition-all"
        :class="[
          disabled || loading
            ? 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
            : 'border-emerald-300 bg-emerald-50 hover:bg-emerald-100 hover:border-emerald-400 text-emerald-700 hover:shadow-sm active:scale-95'
        ]"
      >
        <span class="mr-1">{{ btn.icon }}</span>
        <span>{{ btn.label }}</span>
      </button>

      <!-- 加载中显示骨架屏 -->
      <div
        v-if="loading && buttons.length === 0"
        class="flex gap-2"
      >
        <div
          v-for="i in 3"
          :key="i"
          class="px-3 py-2 rounded-lg bg-gray-100 animate-pulse"
          style="width: 120px; height: 36px"
        ></div>
      </div>
    </div>

    <!-- 自定义提问输入框 -->
    <div class="flex gap-2">
      <input
        v-model="customQuestion"
        @keydown.enter="handleCustomQuestion"
        :disabled="disabled || loading"
        placeholder="➕ 或者自定义提问..."
        class="flex-1 min-w-0 px-3 py-2 text-sm rounded-lg border border-gray-300 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none transition-all"
        :class="[
          disabled || loading
            ? 'bg-gray-50 text-gray-400 cursor-not-allowed'
            : 'bg-white'
        ]"
      />
      <button
        v-if="customQuestion.trim()"
        @click="handleCustomQuestion"
        :disabled="disabled || loading"
        class="px-4 py-2 text-sm font-medium rounded-lg transition-all"
        :class="[
          disabled || loading
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-emerald-600 text-white hover:bg-emerald-700 active:scale-95'
        ]"
      >
        发送
      </button>
    </div>

    <!-- 提示文字 -->
    <p v-if="!disabled" class="text-xs text-gray-400 mt-2">
      提示：点击按钮或输入问题后按 Enter 键发送
    </p>
  </div>
</template>

<script setup lang="ts">
import type { FollowUpButton } from '~/types/followup'

const props = defineProps<{
  buttons: FollowUpButton[]
  loading?: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  select: [question: string]
}>()

const customQuestion = ref('')

const handleButtonClick = (button: FollowUpButton) => {
  if (props.disabled || props.loading) return
  emit('select', button.label)
  customQuestion.value = '' // 清空自定义输入
}

const handleCustomQuestion = () => {
  const question = customQuestion.value.trim()
  if (!question || props.disabled || props.loading) return

  emit('select', question)
  customQuestion.value = '' // 清空输入框
}
</script>

<style scoped>
/* 自定义动画 */
.follow-up-section {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
