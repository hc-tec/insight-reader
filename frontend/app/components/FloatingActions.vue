<template>
  <TooltipProvider>
    <!-- 热区：用于触发按钮显示 -->
    <div
      @mouseenter="showButtons = true"
      @mouseleave="showButtons = false"
      class="fixed bottom-0 right-0 w-32 h-32 z-40 pointer-events-auto"
    >
      <!-- 悬浮按钮组 -->
      <div
        :class="[
          'absolute bottom-6 right-6 flex flex-col gap-3 transition-all duration-300',
          showButtons ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8 pointer-events-none'
        ]"
      >
        <!-- AI洞察折叠/展开按钮 -->
        <Tooltip>
          <TooltipTrigger as-child>
            <button
              @click="$emit('toggle-insight-panel')"
              class="p-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full shadow-lg hover:shadow-xl hover:scale-110 transition-all duration-200"
            >
              <svg
                class="w-5 h-5 transition-transform duration-200"
                :class="{ 'rotate-180': !isInsightPanelExpanded }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>
          </TooltipTrigger>
          <TooltipContent side="left" class="bg-gray-900 text-white border-gray-900">
            {{ isInsightPanelExpanded ? '收起AI洞察' : '展开AI洞察' }}
          </TooltipContent>
        </Tooltip>

      <!-- 元视角按钮 -->
      <Tooltip>
        <TooltipTrigger as-child>
          <button
            @click="$emit('toggle-meta-view')"
            :class="[
              'p-3 rounded-full shadow-lg transition-all duration-300',
              'bg-gradient-to-br from-violet-500/80 to-purple-600/80 backdrop-blur-md',
              'hover:from-violet-600 hover:to-purple-700 hover:shadow-xl hover:scale-110',
              isMetaViewActive ? 'opacity-100' : 'opacity-40 hover:opacity-100'
            ]"
          >
            <!-- 默认状态：眼镜图标 -->
            <svg
              v-if="!isMetaAnalyzing && !isMetaViewActive"
              class="w-5 h-5 text-white"
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
              v-else-if="isMetaAnalyzing"
              class="w-5 h-5 text-white animate-spin"
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
              class="w-5 h-5 text-white"
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
        </TooltipTrigger>
        <TooltipContent side="left" class="bg-gray-900 text-white border-gray-900">
          {{ isMetaViewActive ? '关闭元视角' : '开启元视角' }}
        </TooltipContent>
      </Tooltip>

      <!-- 历史洞察按钮 -->
      <Transition
        enter-active-class="transition-all duration-300"
        enter-from-class="opacity-0 scale-90"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-200"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-90"
      >
        <Tooltip v-if="insightCount > 0">
          <TooltipTrigger as-child>
            <button
              @click="$emit('toggle-replay')"
              :class="[
                'relative p-3 rounded-full shadow-lg transition-all duration-300 hover:scale-110',
                isReplayMode
                  ? 'bg-gradient-to-r from-orange-500 to-amber-600 text-white'
                  : 'bg-white text-orange-600 hover:bg-orange-50'
              ]"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              <!-- 数量徽章 -->
              <span class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-medium">
                {{ insightCount }}
              </span>
            </button>
          </TooltipTrigger>
          <TooltipContent side="left" class="bg-gray-900 text-white border-gray-900">
            {{ isReplayMode ? '关闭回放模式' : '历史洞察回放' }}
          </TooltipContent>
        </Tooltip>
      </Transition>

      <!-- 历史记录按钮 -->
      <Tooltip>
        <TooltipTrigger as-child>
          <button
            @click="$emit('open-history')"
            class="relative p-3 bg-white border border-gray-300 hover:border-gray-400 rounded-full shadow-lg hover:shadow-xl hover:scale-110 transition-all duration-200 text-gray-700"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <!-- 数量徽章 -->
            <span v-if="historyCount > 0" class="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 text-white text-xs rounded-full flex items-center justify-center font-medium">
              {{ historyCount }}
            </span>
          </button>
        </TooltipTrigger>
        <TooltipContent side="left" class="bg-gray-900 text-white border-gray-900">
          历史记录
        </TooltipContent>
      </Tooltip>

      <!-- 元视角加载提示 -->
      <Transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="isMetaAnalyzing"
          class="px-4 py-2 bg-violet-600 text-white text-sm rounded-lg shadow-lg"
        >
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>分析中...</span>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 提示指示器：仅在按钮隐藏且没有特殊状态时显示 -->
    <div
      v-if="!showButtons && !isMetaAnalyzing"
      class="absolute bottom-6 right-6 w-3 h-3 bg-emerald-500/50 rounded-full animate-pulse pointer-events-none"
    ></div>
  </div>
  </TooltipProvider>
</template>

<script setup lang="ts">
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

defineProps<{
  isInsightPanelExpanded: boolean
  insightCount: number
  isReplayMode: boolean
  historyCount: number
  isMetaViewActive: boolean
  isMetaAnalyzing: boolean
}>()

defineEmits<{
  'toggle-insight-panel': []
  'toggle-replay': []
  'open-history': []
  'toggle-meta-view': []
}>()

const showButtons = ref(false)
</script>
