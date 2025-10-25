<template>
  <Transition
    enter-active-class="transition-all duration-300"
    enter-from-class="opacity-0 translate-y-2"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition-all duration-200"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <button
      v-if="insightCount > 0"
      @click="handleToggle"
      :class="[
        'fixed z-50 px-4 py-2 rounded-full shadow-lg transition-all duration-300',
        'bottom-40 right-8',
        'flex items-center gap-2',
        isReplayMode
          ? 'bg-gradient-to-r from-orange-500 to-amber-600 text-white'
          : 'bg-white border-2 border-orange-500 text-orange-600 hover:bg-orange-50'
      ]"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
      </svg>
      <span class="font-medium">
        {{ isReplayMode ? '关闭回放' : `历史洞察 (${insightCount})` }}
      </span>
    </button>
  </Transition>
</template>

<script setup lang="ts">
const props = defineProps<{
  insightCount: number
}>()

const { isReplayMode, toggleReplayMode, renderHistoryHighlights, removeHistoryHighlights, insightConversations } = useInsightReplay()

const handleToggle = () => {
  toggleReplayMode()

  // 渲染或移除标注
  const containerEl = document.getElementById('article-content-container')
  if (!containerEl) return

  if (isReplayMode.value) {
    renderHistoryHighlights(containerEl, insightConversations.value)
  } else {
    removeHistoryHighlights(containerEl)
  }
}
</script>
