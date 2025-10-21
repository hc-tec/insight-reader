<template>
  <MetaInfoCard
    title="时效性评估"
    :icon="ClockIcon"
    :confidence="timelinessScore"
    icon-bg-class="bg-gradient-to-br from-amber-500 to-orange-600"
    @feedback="$emit('feedback', $event)"
  >
    <!-- 分类标签 -->
    <div class="flex items-center gap-2 mb-3">
      <span :class="['px-3 py-1.5 text-sm font-medium rounded-full', categoryBadgeClass]">
        {{ categoryLabel }}
      </span>
      <span :class="['text-sm font-medium', decayRateColorClass]">
        {{ decayRateLabel }}
      </span>
    </div>

    <!-- 时效性条形图 -->
    <div class="mb-3">
      <div class="flex items-center justify-between text-sm text-gray-600 mb-1">
        <span>时效敏感度</span>
        <span class="font-medium">{{ Math.round(timelinessScore * 100) }}%</span>
      </div>
      <div class="relative h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          :class="['h-full rounded-full transition-all', scoreColorClass]"
          :style="{ width: `${timelinessScore * 100}%` }"
        ></div>
      </div>
      <div class="flex items-center justify-between text-xs text-gray-500 mt-1">
        <span>永恒内容</span>
        <span>高度时效</span>
      </div>
    </div>

    <!-- 关键信息 -->
    <div class="space-y-2 text-base">
      <div class="flex items-center justify-between">
        <span class="text-gray-600">内容类型:</span>
        <span class="font-medium text-gray-800">{{ categoryLabel }}</span>
      </div>
      <div class="flex items-center justify-between">
        <span class="text-gray-600">信息衰减:</span>
        <span :class="['font-medium', decayRateColorClass]">{{ decayRateLabel }}</span>
      </div>
      <div v-if="timelinessAnalysis.best_before" class="flex items-center justify-between">
        <span class="text-gray-600">有效期至:</span>
        <span class="font-medium text-gray-800">{{ formatDate(timelinessAnalysis.best_before) }}</span>
      </div>
    </div>

    <!-- 时效性依赖 -->
    <div
      v-if="timelinessAnalysis.context_dependencies && timelinessAnalysis.context_dependencies.length > 0"
      class="mt-4 p-3 bg-amber-50/50 rounded-lg border border-amber-200/50"
    >
      <div class="flex items-center gap-1 mb-2">
        <svg class="w-4 h-4 text-amber-700" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
        <span class="text-sm font-medium text-amber-800">时效性依赖</span>
      </div>
      <ul class="space-y-1">
        <li
          v-for="(dep, index) in timelinessAnalysis.context_dependencies"
          :key="index"
          class="text-sm text-amber-700 flex items-start gap-1.5"
        >
          <svg class="w-2 h-2 text-amber-700 mt-1.5 flex-shrink-0" fill="currentColor" viewBox="0 0 8 8">
            <circle cx="4" cy="4" r="3" />
          </svg>
          <span>{{ dep }}</span>
        </li>
      </ul>
    </div>

    <!-- 阅读建议 -->
    <div class="mt-4 p-3 bg-gradient-to-r from-amber-50/50 to-orange-50/50 rounded-lg border border-amber-200/50">
      <div class="flex items-start gap-2">
        <svg class="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
        <p class="text-sm text-amber-800">
          <strong>阅读建议:</strong> {{ readingAdvice }}
        </p>
      </div>
    </div>
  </MetaInfoCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TimelinessAnalysis } from '~/composables/useMetaView'

const ClockIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  `
}

const props = defineProps<{
  timelinessAnalysis: TimelinessAnalysis
  timelinessScore: number
}>()

const emit = defineEmits<{
  feedback: [type: 'helpful' | 'not-helpful']
}>()

// 类别标签
const categoryLabels: Record<string, string> = {
  timeless: '永恒内容',
  evergreen: '常青内容',
  'time-sensitive': '时效敏感',
  breaking: '突发新闻'
}

// 衰减速度标签
const decayRateLabels: Record<string, string> = {
  low: '缓慢衰减',
  medium: '中等衰减',
  high: '快速衰减'
}

// 类别徽章样式
const categoryBadgeClasses: Record<string, string> = {
  timeless: 'bg-emerald-100 text-emerald-700',
  evergreen: 'bg-green-100 text-green-700',
  'time-sensitive': 'bg-orange-100 text-orange-700',
  breaking: 'bg-red-100 text-red-700'
}

// 衰减速度颜色
const decayRateColorClasses: Record<string, string> = {
  low: 'text-emerald-600',
  medium: 'text-orange-600',
  high: 'text-red-600'
}

const categoryLabel = computed(() => categoryLabels[props.timelinessAnalysis.category] || props.timelinessAnalysis.category)
const decayRateLabel = computed(() => decayRateLabels[props.timelinessAnalysis.decay_rate] || props.timelinessAnalysis.decay_rate)
const categoryBadgeClass = computed(() => categoryBadgeClasses[props.timelinessAnalysis.category] || 'bg-gray-100 text-gray-700')
const decayRateColorClass = computed(() => decayRateColorClasses[props.timelinessAnalysis.decay_rate] || 'text-gray-600')

// 分数颜色（渐变）
const scoreColorClass = computed(() => {
  if (props.timelinessScore >= 0.7) return 'bg-gradient-to-r from-orange-500 to-red-500'
  if (props.timelinessScore >= 0.4) return 'bg-gradient-to-r from-yellow-500 to-orange-500'
  return 'bg-gradient-to-r from-emerald-500 to-green-500'
})

// 格式化日期
const formatDate = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return dateStr
  }
}

// 阅读建议
const readingAdvice = computed(() => {
  const category = props.timelinessAnalysis.category

  if (category === 'timeless') {
    return '这是永恒内容，任何时候阅读都有价值'
  } else if (category === 'evergreen') {
    return '这是常青内容，长期保持相关性，值得收藏'
  } else if (category === 'time-sensitive') {
    return '这是时效性内容，建议尽快阅读以获取最新价值'
  } else if (category === 'breaking') {
    return '这是突发新闻，信息快速变化，需及时了解后续发展'
  }

  return '建议结合发布时间判断内容的当前价值'
})
</script>
