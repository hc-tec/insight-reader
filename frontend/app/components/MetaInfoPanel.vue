<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="translate-x-full"
    enter-to-class="translate-x-0"
    leave-active-class="transition-all duration-300 ease-in"
    leave-from-class="translate-x-0"
    leave-to-class="translate-x-full"
  >
    <aside
      v-if="isMetaViewActive"
      class="fixed top-0 right-0 h-full w-full md:w-[420px] bg-white/70 backdrop-blur-xl border-l border-gray-200/50 shadow-2xl overflow-y-auto z-40"
    >
      <!-- 面板头部 -->
      <div class="sticky top-0 z-10 bg-white/90 backdrop-blur-xl border-b border-gray-200/50 p-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center shadow-md">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">
                元视角
              </h2>
              <p class="text-xs text-gray-500">Meta-View Mode</p>
            </div>
          </div>

          <!-- 关闭按钮 -->
          <button
            @click="closeMetaView"
            class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 面板内容 -->
      <div class="p-6 space-y-6">
        <!-- 加载状态 -->
        <div v-if="isAnalyzing" class="py-12 flex flex-col items-center justify-center">
          <div class="w-16 h-16 border-4 border-violet-600 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p class="text-sm text-gray-600">正在分析文章元信息...</p>
          <p class="text-xs text-gray-500 mt-1">这可能需要几分钟</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="analysisError" class="py-12 flex flex-col items-center justify-center">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-sm text-gray-700 mb-2">分析失败</p>
          <p class="text-xs text-gray-500 mb-4 text-center">{{ analysisError }}</p>
          <button
            @click="$emit('retry')"
            class="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-sm rounded-lg transition-colors"
          >
            重试
          </button>
        </div>

        <!-- 元信息卡片 -->
        <template v-else-if="metaAnalysisData">
          <!-- 作者意图卡片 -->
          <AuthorIntentCard
            :author-intent="metaAnalysisData.author_intent"
            @feedback="handleFeedback('author_intent', $event)"
          />

          <!-- 时效性卡片 -->
          <TimelinessCard
            :timeliness-analysis="metaAnalysisData.timeliness_analysis"
            :timeliness-score="metaAnalysisData.timeliness_score"
            @feedback="handleFeedback('timeliness', $event)"
          />

          <!-- 潜在偏见卡片 -->
          <BiasCard
            :bias-analysis="metaAnalysisData.bias_analysis"
            @feedback="handleFeedback('bias', $event)"
          />

          <!-- 知识缺口卡片 -->
          <KnowledgeGapsCard
            :knowledge-gaps="metaAnalysisData.knowledge_gaps"
            @feedback="handleFeedback('knowledge_gaps', $event)"
          />

          <!-- 思维透镜切换器 -->
          <ThinkingLensSwitcher
            :article-id="metaAnalysisData.article_id"
            container-element-id="article-content-container"
            @lens-applied="handleLensApplied"
            @lens-removed="handleLensRemoved"
          />

          <!-- 分析质量信息 -->
          <div class="mt-6 p-4 bg-gray-50/50 rounded-xl border border-gray-200/50">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-sm font-medium text-gray-600">分析信息</span>
            </div>
            <div class="space-y-1 text-sm text-gray-500">
              <p>模型: {{ metaAnalysisData.analysis_quality.llm_model }}</p>
              <p>耗时: {{ metaAnalysisData.analysis_quality.processing_time_ms }}ms</p>
              <p>置信度: {{ Math.round(metaAnalysisData.analysis_quality.confidence_score * 100) }}%</p>
              <p>版本: {{ metaAnalysisData.analysis_quality.prompt_version }}</p>
            </div>
          </div>
        </template>

        <!-- 空状态 -->
        <div v-else class="py-12 flex flex-col items-center justify-center">
          <div class="w-20 h-20 bg-gradient-to-br from-violet-100 to-purple-100 rounded-2xl flex items-center justify-center mb-4">
            <svg class="w-10 h-10 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <p class="text-sm text-gray-700 mb-1">暂无元信息分析</p>
          <p class="text-xs text-gray-500 text-center">点击眼镜图标开始分析</p>
        </div>
      </div>
    </aside>
  </Transition>

  <!-- 遮罩层 (移动端) -->
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="isMetaViewActive"
      class="fixed inset-0 bg-black/20 backdrop-blur-sm z-30 md:hidden"
      @click="closeMetaView"
    />
  </Transition>
</template>

<script setup lang="ts">
const props = defineProps<{
  articleContent: string
}>()

const { isMetaViewActive, metaAnalysisData, isAnalyzing, analysisError, closeMetaView, submitFeedback } = useMetaView()
const { user } = useAuth()

const emit = defineEmits<{
  retry: []
}>()

const handleFeedback = async (cardType: string, feedbackType: 'helpful' | 'not-helpful') => {
  if (!user.value?.id || !metaAnalysisData.value?.id) return

  try {
    await submitFeedback(
      user.value.id,
      'meta_info_card',
      metaAnalysisData.value.id,
      undefined,
      feedbackType === 'helpful' ? 5 : 1,
      undefined,
      {
        card_type: cardType,
        helpful: feedbackType === 'helpful'
      }
    )

    console.log('✅ 反馈已提交:', cardType, feedbackType)
  } catch (error) {
    console.error('❌ 反馈提交失败:', error)
  }
}

const handleLensApplied = (lensType: string) => {
  console.log('✅ 思维透镜已应用:', lensType)
}

const handleLensRemoved = () => {
  console.log('✅ 思维透镜已移除')
}
</script>
