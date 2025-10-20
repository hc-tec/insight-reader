<template>
  <div class="bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl shadow-sm overflow-hidden">
    <!-- 头部 -->
    <div class="p-6 border-b border-gray-200/50 bg-gradient-to-r from-slate-50/50 to-zinc-50/50">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-md">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
        </div>
        <h3 class="text-xl font-bold bg-gradient-to-r from-slate-800 to-zinc-700 bg-clip-text text-transparent">
          好奇心指纹
        </h3>
      </div>
    </div>

    <!-- 内容 -->
    <div v-if="fingerprint" class="p-6 space-y-6">
      <!-- 主导类型洞察卡片 -->
      <div class="p-5 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl shadow-md text-white">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <p class="text-sm font-medium">{{ dominantTypeText }}</p>
        </div>
      </div>

      <!-- 火花类型分布 -->
      <div>
        <h4 class="text-sm font-semibold text-gray-700 mb-3">火花类型分布</h4>
        <div class="space-y-3">
          <div v-for="(count, type) in fingerprint.spark_distribution" :key="type">
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-xs font-medium text-gray-700">{{ getTypeLabel(type) }}</span>
              <span class="text-xs font-bold text-gray-900">{{ count }}</span>
            </div>
            <div class="h-2.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :style="{
                  width: getPercentage(count) + '%',
                  background: getTypeGradient(type)
                }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 热门话题云 -->
      <div v-if="fingerprint.topic_cloud && fingerprint.topic_cloud.length > 0">
        <h4 class="text-sm font-semibold text-gray-700 mb-3">热门话题</h4>
        <div class="p-4 bg-gradient-to-br from-slate-50/50 to-zinc-50/50 rounded-xl flex flex-wrap justify-center items-center gap-3 min-h-[120px]">
          <span
            v-for="topic in fingerprint.topic_cloud.slice(0, 15)"
            :key="topic.topic"
            class="inline-block text-emerald-700 font-semibold transition-all hover:scale-110 cursor-default"
            :style="{
              fontSize: (0.75 + topic.weight * 0.5) + 'rem',
              opacity: 0.6 + topic.weight * 0.4
            }"
          >
            {{ topic.topic }}
          </span>
        </div>
      </div>

      <!-- 阅读活跃度时序图 -->
      <div v-if="fingerprint.time_series && fingerprint.time_series.length > 0">
        <h4 class="text-sm font-semibold text-gray-700 mb-3">阅读活跃度（最近 7 天）</h4>
        <div class="p-4 bg-gradient-to-br from-slate-50/50 to-zinc-50/50 rounded-xl">
          <div class="flex items-end justify-around gap-2 h-32 mb-3">
            <div
              v-for="(day, index) in getRecentDays(7)"
              :key="day.date"
              class="flex flex-col items-center gap-1 flex-1"
            >
              <div class="w-full flex items-end justify-center gap-0.5 flex-1">
                <div
                  class="w-3 bg-gradient-to-t from-emerald-500 to-teal-600 rounded-t transition-all hover:opacity-80"
                  :style="{ height: getTimelineHeight(day.counts.concept || 0) + 'px' }"
                  :title="`概念: ${day.counts.concept || 0}`"
                ></div>
                <div
                  class="w-3 bg-gradient-to-t from-slate-500 to-zinc-600 rounded-t transition-all hover:opacity-80"
                  :style="{ height: getTimelineHeight(day.counts.argument || 0) + 'px' }"
                  :title="`论证: ${day.counts.argument || 0}`"
                ></div>
              </div>
              <div class="text-[10px] text-gray-500 font-medium">{{ formatDate(day.date) }}</div>
            </div>
          </div>
          <div class="flex items-center justify-center gap-4 pt-3 border-t border-gray-200/50">
            <div class="flex items-center gap-1.5">
              <div class="w-3 h-3 bg-gradient-to-br from-emerald-500 to-teal-600 rounded"></div>
              <span class="text-xs text-gray-600">概念</span>
            </div>
            <div class="flex items-center gap-1.5">
              <div class="w-3 h-3 bg-gradient-to-br from-slate-500 to-zinc-600 rounded"></div>
              <span class="text-xs text-gray-600">论证</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="p-12 flex flex-col items-center justify-center">
      <div class="w-20 h-20 bg-gradient-to-br from-amber-100 to-orange-100 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-10 h-10 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
        </svg>
      </div>
      <p class="text-lg font-semibold text-gray-700 mb-1">暂无数据</p>
      <p class="text-sm text-gray-500">开始点击火花，构建你的好奇心指纹</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  userId: number
}>()

const { fetchCuriosityFingerprint, curiosityFingerprint, getDominantTypeText } = useDashboard()

const fingerprint = computed(() => curiosityFingerprint.value)
const dominantTypeText = computed(() => getDominantTypeText.value)

// 加载数据
onMounted(async () => {
  await fetchCuriosityFingerprint(props.userId)
})

// 获取类型标签
const getTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    concept: '📚 概念',
    argument: '💡 论证',
    entity: '👤 实体'
  }
  return labels[type] || type
}

// 获取类型渐变色
const getTypeGradient = (type: string): string => {
  const gradients: Record<string, string> = {
    concept: 'linear-gradient(to right, #10b981, #14b8a6)',
    argument: 'linear-gradient(to right, #64748b, #71717a)',
    entity: 'linear-gradient(to right, #f59e0b, #f97316)'
  }
  return gradients[type] || 'linear-gradient(to right, #6b7280, #9ca3af)'
}

// 计算百分比
const getPercentage = (count: number): number => {
  if (!fingerprint.value) return 0

  const total = Object.values(fingerprint.value.spark_distribution).reduce((sum, c) => sum + c, 0)
  return total > 0 ? Math.round((count / total) * 100) : 0
}

// 获取最近 N 天的数据
const getRecentDays = (days: number) => {
  if (!fingerprint.value) return []
  return fingerprint.value.time_series.slice(-days)
}

// 计算时序图高度
const getTimelineHeight = (count: number): number => {
  const maxHeight = 100
  const maxCount = Math.max(
    ...getRecentDays(7).flatMap(day => Object.values(day.counts))
  )
  return maxCount > 0 ? Math.round((count / maxCount) * maxHeight) : 2
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>
