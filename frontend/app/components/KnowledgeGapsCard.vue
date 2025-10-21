<template>
  <MetaInfoCard
    title="知识缺口提示"
    :icon="LightbulbIcon"
    icon-bg-class="bg-gradient-to-br from-indigo-500 to-blue-600"
    @feedback="$emit('feedback', $event)"
  >
    <!-- 前置知识 -->
    <div v-if="knowledgeGaps.prerequisites && knowledgeGaps.prerequisites.length > 0" class="mb-4">
      <div class="flex items-center gap-1 mb-2">
        <svg class="w-3 h-3 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
        </svg>
        <span class="text-sm font-medium text-gray-600">前置知识</span>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(prereq, index) in knowledgeGaps.prerequisites"
          :key="index"
          class="px-3 py-1.5 bg-indigo-50 border border-indigo-200 text-indigo-700 text-sm rounded-lg hover:bg-indigo-100 transition-colors cursor-pointer"
        >
          {{ prereq }}
        </span>
      </div>
      <p class="text-sm text-gray-600 mt-2">阅读本文建议先了解以上概念</p>
    </div>

    <!-- 隐含假设 -->
    <div v-if="knowledgeGaps.assumptions && knowledgeGaps.assumptions.length > 0" class="mb-4">
      <div class="flex items-center gap-1 mb-2">
        <svg class="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
        <span class="text-sm font-medium text-gray-600">隐含假设</span>
      </div>
      <ul class="space-y-1.5">
        <li
          v-for="(assumption, index) in knowledgeGaps.assumptions"
          :key="index"
          class="text-sm text-gray-700 flex items-start gap-2 p-2 bg-blue-50/50 rounded-lg border border-blue-200/50"
        >
          <svg class="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
          <span>{{ assumption }}</span>
        </li>
      </ul>
      <p class="text-sm text-gray-600 mt-2">作者未明说但默认读者知道的前提</p>
    </div>

    <!-- 缺失背景 -->
    <div v-if="knowledgeGaps.missing_context && knowledgeGaps.missing_context.length > 0" class="mb-4">
      <div class="flex items-center gap-1 mb-2">
        <svg class="w-3 h-3 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <span class="text-sm font-medium text-gray-600">缺失背景</span>
      </div>
      <ul class="space-y-1.5">
        <li
          v-for="(context, index) in knowledgeGaps.missing_context"
          :key="index"
          class="text-sm text-gray-700 flex items-start gap-2"
        >
          <svg class="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <span>{{ context }}</span>
        </li>
      </ul>
      <p class="text-sm text-gray-600 mt-2">文中未提及但可能重要的上下文信息</p>
    </div>

    <!-- 相关概念 -->
    <div v-if="knowledgeGaps.related_concepts && knowledgeGaps.related_concepts.length > 0" class="mb-4">
      <div class="flex items-center gap-1 mb-2">
        <svg class="w-3 h-3 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
          <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
        </svg>
        <span class="text-sm font-medium text-gray-600">拓展阅读</span>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(concept, index) in knowledgeGaps.related_concepts"
          :key="index"
          class="px-3 py-1.5 bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded-lg hover:bg-emerald-100 transition-colors cursor-pointer"
        >
          {{ concept }}
        </span>
      </div>
      <p class="text-sm text-gray-600 mt-2">推荐继续学习的相关主题</p>
    </div>

    <!-- 学习建议 -->
    <div class="mt-4 p-3 bg-gradient-to-r from-indigo-50/50 to-blue-50/50 rounded-lg border border-indigo-200/50">
      <div class="flex items-start gap-2">
        <svg class="w-4 h-4 text-indigo-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
        </svg>
        <p class="text-sm text-indigo-800">
          <strong>学习建议:</strong> {{ learningAdvice }}
        </p>
      </div>
    </div>

    <!-- 全部掌握状态 -->
    <div
      v-if="isAllMastered"
      class="mt-4 p-3 bg-gradient-to-r from-emerald-50/50 to-green-50/50 rounded-lg border border-emerald-200/50"
    >
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <p class="text-sm font-medium text-emerald-800">太棒了！本文似乎没有需要特别补充的知识</p>
      </div>
    </div>
  </MetaInfoCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { KnowledgeGaps } from '~/composables/useMetaView'

const LightbulbIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  `
}

const props = defineProps<{
  knowledgeGaps: KnowledgeGaps
}>()

const emit = defineEmits<{
  feedback: [type: 'helpful' | 'not-helpful']
}>()

// 是否全部掌握（没有知识缺口）
const isAllMastered = computed(() => {
  return (
    (!props.knowledgeGaps.prerequisites || props.knowledgeGaps.prerequisites.length === 0) &&
    (!props.knowledgeGaps.assumptions || props.knowledgeGaps.assumptions.length === 0) &&
    (!props.knowledgeGaps.missing_context || props.knowledgeGaps.missing_context.length === 0)
  )
})

// 学习建议
const learningAdvice = computed(() => {
  if (isAllMastered.value) {
    return '本文自成体系，您可以直接阅读。建议点击相关概念拓展知识面。'
  }

  const hasPrereq = props.knowledgeGaps.prerequisites && props.knowledgeGaps.prerequisites.length > 0
  const hasAssumptions = props.knowledgeGaps.assumptions && props.knowledgeGaps.assumptions.length > 0

  if (hasPrereq && hasAssumptions) {
    return '建议先了解前置知识，阅读时留意作者的隐含假设，必要时查阅背景资料。'
  } else if (hasPrereq) {
    return '建议先了解标注的前置知识，这将帮助您更好地理解文章内容。'
  } else if (hasAssumptions) {
    return '阅读时请留意作者的隐含假设，这些假设可能影响您对内容的理解。'
  } else {
    return '建议查阅缺失背景以获得更全面的理解。'
  }
})
</script>
