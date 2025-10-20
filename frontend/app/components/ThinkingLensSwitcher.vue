<template>
  <div class="mb-4 bg-white/80 backdrop-blur-md border border-gray-200/50 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all">
    <!-- 头部 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        </div>
        <h4 class="text-sm font-semibold text-gray-800">思维透镜</h4>
      </div>

      <!-- 帮助图标 -->
      <button
        @click="showHelp = !showHelp"
        class="p-1 rounded-lg hover:bg-gray-100 transition-colors"
        title="使用说明"
      >
        <svg class="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <!-- 使用说明 -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      leave-active-class="transition-all duration-200 ease-in"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="showHelp" class="mb-4 p-3 bg-gradient-to-r from-teal-50/50 to-cyan-50/50 rounded-lg border border-teal-200/50">
        <p class="text-xs text-teal-800 leading-relaxed">
          思维透镜可以帮助你以不同视角重新审视文章内容。选择透镜后，文章中的关键信息会被高亮标注，帮助你快速识别论证结构和作者立场。
        </p>
      </div>
    </Transition>

    <!-- 透镜选择器 -->
    <div class="space-y-3">
      <!-- 论证结构透镜 -->
      <div
        @click="toggleLens('argument_structure')"
        :class="[
          'relative p-4 rounded-xl border-2 cursor-pointer transition-all',
          isLensActive('argument_structure')
            ? 'border-teal-500 bg-gradient-to-r from-teal-50 to-cyan-50 shadow-md'
            : 'border-gray-200 bg-white/50 hover:border-teal-300 hover:shadow-sm'
        ]"
      >
        <!-- 加载状态 -->
        <div v-if="isLensLoading('argument_structure')" class="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-xl flex items-center justify-center z-10">
          <svg class="w-6 h-6 text-teal-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>

        <div class="flex items-start gap-3">
          <!-- 图标 -->
          <div :class="[
            'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors',
            isLensActive('argument_structure') ? 'bg-teal-500' : 'bg-gray-200'
          ]">
            <svg :class="[
              'w-5 h-5 transition-colors',
              isLensActive('argument_structure') ? 'text-white' : 'text-gray-500'
            ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>

          <!-- 内容 -->
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <h5 :class="[
                'text-sm font-semibold transition-colors',
                isLensActive('argument_structure') ? 'text-teal-700' : 'text-gray-700'
              ]">论证结构透镜</h5>
              <span v-if="isLensActive('argument_structure')" class="px-2 py-0.5 bg-teal-500 text-white text-[10px] font-medium rounded-full">
                已激活
              </span>
            </div>
            <p class="text-xs text-gray-600 mb-2">识别文章中的论点、证据和推理过程</p>

            <!-- 激活状态下的统计信息和关闭按钮 -->
            <div v-if="isLensActive('argument_structure') && getLensResult('argument_structure')" class="mt-3">
              <div class="flex items-center justify-between text-xs text-gray-600 pt-2 border-t border-teal-200/50">
                <span>共识别 {{ getTotalHighlights('argument_structure') }} 个关键片段</span>
                <button
                  @click.stop="removeLens('argument_structure')"
                  class="px-2 py-1 text-teal-600 hover:bg-teal-100 rounded transition-colors"
                >
                  关闭透镜
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 作者立场透镜 -->
      <div
        @click="toggleLens('author_stance')"
        :class="[
          'relative p-4 rounded-xl border-2 cursor-pointer transition-all',
          isLensActive('author_stance')
            ? 'border-purple-500 bg-gradient-to-r from-purple-50 to-pink-50 shadow-md'
            : 'border-gray-200 bg-white/50 hover:border-purple-300 hover:shadow-sm'
        ]"
      >
        <!-- 加载状态 -->
        <div v-if="isLensLoading('author_stance')" class="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-xl flex items-center justify-center z-10">
          <svg class="w-6 h-6 text-purple-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>

        <div class="flex items-start gap-3">
          <!-- 图标 -->
          <div :class="[
            'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors',
            isLensActive('author_stance') ? 'bg-purple-500' : 'bg-gray-200'
          ]">
            <svg :class="[
              'w-5 h-5 transition-colors',
              isLensActive('author_stance') ? 'text-white' : 'text-gray-500'
            ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
          </div>

          <!-- 内容 -->
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <h5 :class="[
                'text-sm font-semibold transition-colors',
                isLensActive('author_stance') ? 'text-purple-700' : 'text-gray-700'
              ]">作者立场透镜</h5>
              <span v-if="isLensActive('author_stance')" class="px-2 py-0.5 bg-purple-500 text-white text-[10px] font-medium rounded-full">
                已激活
              </span>
            </div>
            <p class="text-xs text-gray-600 mb-2">区分客观陈述与主观观点</p>

            <!-- 激活状态下的统计信息 -->
            <div v-if="isLensActive('author_stance') && getLensResult('author_stance')" class="mt-3 space-y-2">
              <!-- 色彩图例 -->
              <div class="flex flex-wrap gap-2">
                <div class="flex items-center gap-1.5">
                  <span class="w-3 h-3 rounded bg-indigo-200 border border-indigo-400"></span>
                  <span class="text-xs text-gray-600">客观陈述 ({{ getHighlightCount('author_stance', 'objective') }})</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="w-3 h-3 rounded bg-rose-200 border border-rose-400"></span>
                  <span class="text-xs text-gray-600">主观观点 ({{ getHighlightCount('author_stance', 'subjective') }})</span>
                </div>
              </div>

              <!-- 主观性比例 -->
              <div class="pt-2 border-t border-purple-200/50">
                <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
                  <span>主观性程度</span>
                  <span class="font-medium">{{ getSubjectivityRatio() }}%</span>
                </div>
                <div class="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-indigo-500 to-rose-500 rounded-full transition-all"
                    :style="{ width: `${getSubjectivityRatio()}%` }"
                  ></div>
                </div>
              </div>

              <!-- 统计信息 -->
              <div class="flex items-center justify-between text-xs text-gray-600 pt-2 border-t border-purple-200/50">
                <span>共识别 {{ getTotalHighlights('author_stance') }} 个片段</span>
                <button
                  @click.stop="removeLens('author_stance')"
                  class="px-2 py-1 text-purple-600 hover:bg-purple-100 rounded transition-colors"
                >
                  关闭透镜
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 论证结构可视化视图 -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-4"
      leave-active-class="transition-all duration-200 ease-in"
      leave-to-class="opacity-0 -translate-y-4"
    >
      <ArgumentStructureView
        v-if="isLensActive('argument_structure') && getLensResult('argument_structure')"
        :highlights="getLensResult('argument_structure')!.highlights"
        :annotations="getLensResult('argument_structure')!.annotations"
        class="mt-4"
      />
    </Transition>

    <!-- 错误提示 -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      leave-active-class="transition-all duration-200 ease-in"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="error" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-start gap-2">
          <svg class="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <div class="flex-1">
            <p class="text-xs text-red-800 font-medium">透镜应用失败</p>
            <p class="text-xs text-red-700 mt-1">{{ error }}</p>
            <button
              @click="retryApplyLens"
              class="mt-2 px-3 py-1 bg-red-600 text-white text-xs rounded-lg hover:bg-red-700 transition-colors"
            >
              重试
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 底部提示 -->
    <div v-if="!isLensActive('argument_structure') && !isLensActive('author_stance')" class="mt-4 pt-3 border-t border-gray-200">
      <p class="text-xs text-gray-500 text-center">
        点击上方透镜开始深度阅读（可同时开启多个）
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useThinkingLens } from '~/composables/useThinkingLens'
import type { LensType } from '~/composables/useThinkingLens'

const props = defineProps<{
  articleId: number  // 改用 article_id
  containerElementId?: string  // 文章容器DOM元素ID，用于应用高亮
}>()

const emit = defineEmits<{
  lensApplied: [lensType: LensType]
  lensRemoved: []
}>()

// 使用思维透镜 composable
const {
  enabledLenses,
  lensResults,
  loadingLenses,
  error,
  toggleLens: toggleLensComposable
} = useThinkingLens()

const showHelp = ref(false)
const pendingLens = ref<LensType | null>(null)

// 检查特定透镜是否激活
const isLensActive = (lensType: LensType) => {
  return enabledLenses.value.has(lensType)
}

// 获取特定透镜的结果
const getLensResult = (lensType: LensType) => {
  return lensResults.value.get(lensType) || null
}

// 检查特定透镜是否正在加载
const isLensLoading = (lensType: LensType) => {
  return loadingLenses.value.has(lensType)
}

// 切换透镜
const toggleLens = async (lensType: LensType) => {
  // 应用新透镜
  pendingLens.value = lensType

  try {
    const containerEl = props.containerElementId ? document.getElementById(props.containerElementId) : null
    if (!containerEl) {
      console.error('⚠️ 未找到文章容器元素')
      return
    }

    await toggleLensComposable(props.articleId, lensType, containerEl)

    // 触发事件
    if (enabledLenses.value.has(lensType)) {
      emit('lensApplied', lensType)
    } else {
      emit('lensRemoved')
    }
  } catch (err) {
    console.error('Failed to toggle lens:', err)
  } finally {
    pendingLens.value = null
  }
}

// 移除特定透镜
const removeLens = (lensType: LensType) => {
  const containerEl = props.containerElementId ? document.getElementById(props.containerElementId) : null
  if (containerEl) {
    toggleLensComposable(props.articleId, lensType, containerEl)
  }
  emit('lensRemoved')
}

// 重试应用透镜
const retryApplyLens = () => {
  if (pendingLens.value) {
    toggleLens(pendingLens.value)
  }
}

// 获取特定透镜、特定类别的高亮数量
const getHighlightCount = (lensType: LensType, category: string): number => {
  const result = getLensResult(lensType)
  if (!result) return 0
  return result.highlights.filter(h => h.category === category).length
}

// 获取特定透镜的总高亮数量
const getTotalHighlights = (lensType: LensType): number => {
  const result = getLensResult(lensType)
  if (!result) return 0
  return result.highlights.length
}

// 计算主观性比例（仅用于作者立场透镜）
const getSubjectivityRatio = (): number => {
  const result = getLensResult('author_stance')
  if (!result) return 0

  const total = result.highlights.length
  if (total === 0) return 0

  const subjectiveCount = getHighlightCount('author_stance', 'subjective')
  return Math.round((subjectiveCount / total) * 100)
}

// 监听文章变化，自动清除透镜
watch(() => props.articleId, () => {
  // 文章变化时，清空所有透镜状态（新文章需要重新加载）
  enabledLenses.value.clear()
})
</script>
