<template>
  <div>
    <!-- 触发按钮 -->
    <button
      @click="handleToggle"
      @mouseenter="showTooltip = true"
      @mouseleave="showTooltip = false"
      :class="[
        'fixed z-50 w-12 h-12 rounded-full shadow-lg transition-all duration-300',
        'bg-gradient-to-br from-violet-500/80 to-purple-600/80 backdrop-blur-md',
        'hover:from-violet-600 hover:to-purple-700 hover:shadow-xl hover:scale-110',
        'bottom-24 right-8',
        isMetaViewActive ? 'opacity-100' : 'opacity-40 hover:opacity-100'
      ]"
    >
      <!-- 默认状态：眼镜图标 -->
      <svg
        v-if="!isAnalyzing && !isMetaViewActive"
        class="w-6 h-6 text-white mx-auto"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
        />
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
        />
      </svg>

      <!-- 加载状态：旋转图标 -->
      <svg
        v-else-if="isAnalyzing"
        class="w-6 h-6 text-white animate-spin mx-auto"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
        />
      </svg>

      <!-- 激活状态：关闭图标 -->
      <svg
        v-else
        class="w-6 h-6 text-white mx-auto"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </button>

    <!-- 悬停提示 -->
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="showTooltip && !isAnalyzing"
        class="fixed bottom-24 right-24 px-3 py-1.5 bg-gray-900 text-white text-xs rounded-lg pointer-events-none z-50"
      >
        {{ isMetaViewActive ? '关闭元视角' : '开启元视角' }}
      </div>
    </Transition>

    <!-- 加载提示 -->
    <Transition
      enter-active-class="transition-all duration-200"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isAnalyzing"
        class="fixed bottom-24 right-24 px-4 py-2 bg-violet-600 text-white text-sm rounded-lg shadow-lg z-50"
      >
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          <span>分析中...</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  articleTitle: string
  articleContent: string
  articleAuthor?: string
  publishDate?: string
}>()

const {
  isMetaViewActive,
  isAnalyzing,
  analyzeArticle,
  toggleMetaView
} = useMetaView()

const { user } = useAuth()  // 获取用户信息

const showTooltip = ref(false)

const handleToggle = async () => {
  if (!isMetaViewActive.value) {
    // 开启元视角：触发分析
    try {
      await analyzeArticle(
        props.articleTitle,
        props.articleAuthor || 'Unknown',
        props.publishDate || new Date().toISOString(),
        props.articleContent,
        user.value?.id,  // 传递用户ID
        undefined  // sourceUrl
      )

      // 分析成功后打开面板
      toggleMetaView()
    } catch (error) {
      console.error('元信息分析失败:', error)
      // 分析失败时也打开面板显示错误
      toggleMetaView()
    }
  } else {
    // 关闭元视角
    toggleMetaView()
  }
}
</script>
