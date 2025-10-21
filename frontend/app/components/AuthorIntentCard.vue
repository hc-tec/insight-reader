<template>
  <MetaInfoCard
    title="作者意图"
    :icon="TargetIcon"
    :confidence="authorIntent.confidence"
    icon-bg-class="bg-gradient-to-br from-violet-500 to-purple-600"
    @feedback="$emit('feedback', $event)"
  >
    <!-- 意图标签 -->
    <div class="flex items-center gap-2 mb-3">
      <span :class="['px-3 py-1.5 text-sm font-medium rounded-full', intentBadgeClass]">
        {{ intentLabel }}
      </span>
      <div class="flex items-center gap-1 text-sm text-gray-500">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
        </svg>
        <span>{{ Math.round(authorIntent.confidence * 100) }}% 置信度</span>
      </div>
    </div>

    <!-- 描述 -->
    <p class="text-base text-gray-700 leading-relaxed mb-3">
      {{ authorIntent.description }}
    </p>

    <!-- 识别依据 -->
    <div v-if="authorIntent.indicators && authorIntent.indicators.length > 0" class="mt-3">
      <div class="flex items-center gap-1 mb-2">
        <svg class="w-4 h-4 text-violet-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
        <span class="text-sm font-medium text-gray-600">识别依据</span>
      </div>
      <ul class="space-y-1.5">
        <li
          v-for="(indicator, index) in authorIntent.indicators"
          :key="index"
          class="text-sm text-gray-600 flex items-start gap-2"
        >
          <svg class="w-2 h-2 text-violet-500 mt-1.5 flex-shrink-0" fill="currentColor" viewBox="0 0 8 8">
            <circle cx="4" cy="4" r="3" />
          </svg>
          <span>{{ indicator }}</span>
        </li>
      </ul>
    </div>

    <!-- 意图说明 -->
    <div class="mt-4 p-3 bg-violet-50/50 rounded-lg border border-violet-200/50">
      <p class="text-sm text-violet-800">
        <strong>{{ intentLabel }}</strong>: {{ intentExplanation }}
      </p>
    </div>
  </MetaInfoCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AuthorIntent } from '~/composables/useMetaView'

// 图标组件（简化版，实际应使用 lucide-vue-next）
const TargetIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  `
}

const props = defineProps<{
  authorIntent: AuthorIntent
}>()

const emit = defineEmits<{
  feedback: [type: 'helpful' | 'not-helpful']
}>()

const intentLabels: Record<string, string> = {
  inform: '告知',
  persuade: '说服',
  entertain: '娱乐',
  provoke: '激发思考'
}

const intentExplanations: Record<string, string> = {
  inform: '作者主要目的是传达信息、解释概念或分享知识',
  persuade: '作者试图说服读者接受某种观点或采取某种行动',
  entertain: '作者以娱乐、引起兴趣或愉悦读者为主要目的',
  provoke: '作者旨在激发读者的批判性思维或引发深度思考'
}

const intentBadgeClasses: Record<string, string> = {
  inform: 'bg-blue-100 text-blue-700',
  persuade: 'bg-orange-100 text-orange-700',
  entertain: 'bg-pink-100 text-pink-700',
  provoke: 'bg-purple-100 text-purple-700'
}

const intentLabel = computed(() => intentLabels[props.authorIntent.primary] || props.authorIntent.primary)
const intentExplanation = computed(() => intentExplanations[props.authorIntent.primary] || '')
const intentBadgeClass = computed(() => intentBadgeClasses[props.authorIntent.primary] || 'bg-gray-100 text-gray-700')
</script>
