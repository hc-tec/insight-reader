<template>
  <MetaInfoCard
    title="潜在偏见检测"
    :icon="AlertIcon"
    :confidence="biasAnalysis.detected ? 0.8 : 0.9"
    icon-bg-class="bg-gradient-to-br from-rose-500 to-pink-600"
    @feedback="$emit('feedback', $event)"
  >
    <!-- 检测结果状态 -->
    <div class="mb-3">
      <div v-if="!biasAnalysis.detected" class="flex items-center gap-2 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
        <svg class="w-5 h-5 text-emerald-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <div>
          <p class="text-sm font-medium text-emerald-800">未检测到明显偏见</p>
          <p class="text-xs text-emerald-700 mt-0.5">文章整体保持客观平衡</p>
        </div>
      </div>

      <div v-else class="flex items-center gap-2 p-3 bg-rose-50 rounded-lg border border-rose-200">
        <svg class="w-5 h-5 text-rose-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <div>
          <p class="text-sm font-medium text-rose-800">检测到潜在偏见</p>
          <p class="text-xs text-rose-700 mt-0.5">建议批判性阅读</p>
        </div>
      </div>
    </div>

    <!-- 偏见类型 -->
    <div v-if="biasAnalysis.detected && biasAnalysis.types.length > 0" class="mb-3">
      <div class="flex items-center gap-1 mb-2">
        <svg class="w-3 h-3 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
        <span class="text-xs font-medium text-gray-600">偏见类型</span>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(type, index) in biasAnalysis.types"
          :key="index"
          class="px-2 py-1 bg-rose-100 text-rose-700 text-xs rounded-lg"
        >
          {{ biasTypeLabels[type] || type }}
        </span>
      </div>
    </div>

    <!-- 严重程度 -->
    <div v-if="biasAnalysis.detected" class="mb-3">
      <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
        <span>严重程度</span>
        <span :class="['font-medium', severityColorClass]">{{ severityLabel }}</span>
      </div>
      <div class="relative h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          :class="['h-full rounded-full transition-all', severityBarClass]"
          :style="{ width: severityWidth }"
        ></div>
      </div>
    </div>

    <!-- 整体平衡性 -->
    <div class="flex items-center justify-between text-sm mb-3">
      <span class="text-gray-600">整体平衡:</span>
      <span :class="['font-medium', balanceColorClass]">{{ balanceLabel }}</span>
    </div>

    <!-- 具体案例 -->
    <div v-if="biasAnalysis.detected && biasAnalysis.examples && biasAnalysis.examples.length > 0" class="mt-4">
      <div class="flex items-center gap-1 mb-2">
        <svg class="w-3 h-3 text-rose-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
          <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
        </svg>
        <span class="text-xs font-medium text-gray-600">具体案例</span>
      </div>
      <div class="space-y-2">
        <div
          v-for="(example, index) in biasAnalysis.examples.slice(0, 3)"
          :key="index"
          class="p-3 bg-rose-50/50 rounded-lg border border-rose-200/50"
        >
          <div class="flex items-start gap-2 mb-1.5">
            <span class="px-2 py-0.5 bg-rose-200 text-rose-800 text-[10px] font-medium rounded">
              {{ biasTypeLabels[example.type] || example.type }}
            </span>
          </div>
          <p class="text-xs text-gray-700 italic mb-1.5">"{{ example.text }}"</p>
          <p class="text-xs text-rose-700">{{ example.explanation }}</p>
        </div>
      </div>
    </div>

    <!-- 阅读提示 -->
    <div class="mt-4 p-3 bg-gradient-to-r from-rose-50/50 to-pink-50/50 rounded-lg border border-rose-200/50">
      <div class="flex items-start gap-2">
        <svg class="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
        <p class="text-xs text-rose-800">
          <strong>阅读提示:</strong> {{ readingTip }}
        </p>
      </div>
    </div>
  </MetaInfoCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BiasAnalysis } from '~/composables/useMetaView'

const AlertIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  `
}

const props = defineProps<{
  biasAnalysis: BiasAnalysis
}>()

const emit = defineEmits<{
  feedback: [type: 'helpful' | 'not-helpful']
}>()

// 偏见类型标签
const biasTypeLabels: Record<string, string> = {
  confirmation_bias: '确认偏误',
  political_bias: '政治倾向',
  cultural_bias: '文化偏见',
  selection_bias: '选择性偏见',
  anchoring_bias: '锚定效应',
  availability_bias: '可得性偏见'
}

// 严重程度标签
const severityLabels: Record<string, string> = {
  low: '轻微',
  medium: '中等',
  high: '严重'
}

// 平衡性标签
const balanceLabels: Record<string, string> = {
  balanced: '平衡',
  slightly_biased: '略有偏向',
  heavily_biased: '明显偏向'
}

const severityLabel = computed(() => severityLabels[props.biasAnalysis.severity] || props.biasAnalysis.severity)
const balanceLabel = computed(() => balanceLabels[props.biasAnalysis.overall_balance] || props.biasAnalysis.overall_balance)

// 严重程度颜色
const severityColorClass = computed(() => {
  switch (props.biasAnalysis.severity) {
    case 'low': return 'text-yellow-600'
    case 'medium': return 'text-orange-600'
    case 'high': return 'text-red-600'
    default: return 'text-gray-600'
  }
})

// 严重程度进度条
const severityBarClass = computed(() => {
  switch (props.biasAnalysis.severity) {
    case 'low': return 'bg-yellow-500'
    case 'medium': return 'bg-orange-500'
    case 'high': return 'bg-red-500'
    default: return 'bg-gray-500'
  }
})

const severityWidth = computed(() => {
  switch (props.biasAnalysis.severity) {
    case 'low': return '33%'
    case 'medium': return '66%'
    case 'high': return '100%'
    default: return '0%'
  }
})

// 平衡性颜色
const balanceColorClass = computed(() => {
  switch (props.biasAnalysis.overall_balance) {
    case 'balanced': return 'text-emerald-600'
    case 'slightly_biased': return 'text-orange-600'
    case 'heavily_biased': return 'text-red-600'
    default: return 'text-gray-600'
  }
})

// 阅读提示
const readingTip = computed(() => {
  if (!props.biasAnalysis.detected) {
    return '文章未检测到明显偏见，但仍建议保持批判性思维'
  }

  if (props.biasAnalysis.severity === 'high') {
    return '检测到严重偏见，请格外警惕，建议对照其他来源验证信息'
  } else if (props.biasAnalysis.severity === 'medium') {
    return '检测到一定程度的偏见，建议注意作者的观点立场'
  } else {
    return '检测到轻微偏见，阅读时注意区分事实与观点'
  }
})
</script>
