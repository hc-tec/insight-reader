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

  <!-- 选中文字后显示的小logo按钮 -->
  <Transition
    enter-active-class="transition-all duration-200 ease-out"
    enter-from-class="opacity-0 scale-90"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition-all duration-150 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-90"
  >
    <button
      v-if="show"
      :style="buttonStyle"
      @click.stop="handleClick"
      class="fixed z-50 w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 rounded-full shadow-lg hover:shadow-xl flex items-center justify-center transition-all group"
      title="AI 洞察"
    >
      <svg class="w-6 h-6 text-white group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>

      <!-- 小脉冲动画 -->
      <span class="absolute inset-0 rounded-full bg-emerald-400 opacity-75 animate-ping"></span>
    </button>
  </Transition>
</template>

<script setup lang="ts">
// Props
interface Props {
  show: boolean
  position: { x: number; y: number }
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  click: []
  close: []
}>()

// 计算按钮位置
const buttonStyle = computed(() => {
  if (!props.show) return {}

  const buttonSize = 48 // 按钮大小
  const offset = 8 // 偏移量

  let x = props.position.x
  let y = props.position.y

  // 按钮显示在选中文字的右上角
  return {
    left: `${x + offset}px`,
    top: `${y - buttonSize - offset}px`,
  }
})

const handleClick = () => {
  emit('click')
}

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
@keyframes ping {
  75%, 100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.animate-ping {
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}
</style>
