<template>
  <div class="bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl shadow-sm overflow-hidden">
    <!-- 头部 -->
    <div class="p-6 border-b border-gray-200/50 bg-gradient-to-r from-slate-50/50 to-zinc-50/50">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-slate-500 to-zinc-600 rounded-xl flex items-center justify-center shadow-md">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h3 class="text-xl font-bold bg-gradient-to-r from-slate-800 to-zinc-700 bg-clip-text text-transparent">
          思维盲区探测
        </h3>
      </div>
    </div>

    <!-- 内容 -->
    <div v-if="blindSpots" class="p-6 space-y-6">
      <!-- 缺失领域 -->
      <div v-if="blindSpots.missingDomains && blindSpots.missingDomains.length > 0">
        <div class="mb-3">
          <h4 class="text-sm font-semibold text-gray-700 mb-1">未探索的领域</h4>
          <p class="text-xs text-gray-500">以下领域你还未涉足，不妨尝试拓展阅读</p>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div
            v-for="domain in blindSpots.missingDomains"
            :key="domain"
            class="group p-4 bg-gradient-to-br from-slate-50/50 to-zinc-50/50 border border-gray-200/50 rounded-xl hover:shadow-md hover:border-emerald-300/50 transition-all text-center"
          >
            <div class="text-3xl mb-2">{{ getDomainIcon(domain) }}</div>
            <div class="text-sm font-semibold text-gray-800 mb-2">{{ domain }}</div>
            <button
              @click="handleExploreDomain(domain)"
              class="text-xs px-3 py-1.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-lg transition-all opacity-0 group-hover:opacity-100"
            >
              去探索
            </button>
          </div>
        </div>
      </div>

      <!-- 知识孤岛 -->
      <div v-if="blindSpots.knowledgeIslands && blindSpots.knowledgeIslands.length > 0">
        <div class="mb-3">
          <h4 class="text-sm font-semibold text-gray-700 mb-1">知识孤岛</h4>
          <p class="text-xs text-gray-500">这些概念彼此孤立，建议阅读相关内容建立联系</p>
        </div>

        <div class="space-y-3">
          <div
            v-for="island in blindSpots.knowledgeIslands"
            :key="island.id"
            class="p-4 bg-gradient-to-r from-amber-50/50 to-orange-50/50 border-l-4 border-amber-500 rounded-lg"
          >
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span
                v-for="(concept, index) in island.concepts"
                :key="concept"
                class="inline-flex items-center gap-1.5"
              >
                <span class="text-sm font-semibold text-amber-900">{{ concept }}</span>
                <span v-if="index < island.concepts.length - 1" class="text-amber-600">·</span>
              </span>
            </div>
            <div class="flex items-start gap-2 text-xs text-amber-800">
              <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ island.recommendation }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 全部探索完成 -->
      <div
        v-if="(!blindSpots.missingDomains || blindSpots.missingDomains.length === 0) && (!blindSpots.knowledgeIslands || blindSpots.knowledgeIslands.length === 0)"
        class="py-12 text-center"
      >
        <div class="w-20 h-20 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-2xl flex items-center justify-center mb-4 mx-auto">
          <svg class="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-lg font-semibold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent mb-1">
          太棒了！
        </p>
        <p class="text-sm text-gray-600">你已经探索了多个知识领域，知识网络连接紧密</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-else class="p-12 flex flex-col items-center justify-center">
      <div class="w-20 h-20 bg-gradient-to-br from-slate-100 to-zinc-100 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-10 h-10 text-slate-600 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      </div>
      <p class="text-sm text-gray-500">正在扫描思维盲区...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  userId: number
}>()

const { fetchBlindSpots, blindSpots } = useDashboard()

// 加载数据
onMounted(async () => {
  await fetchBlindSpots(props.userId)
})

// 领域图标映射
const getDomainIcon = (domain: string): string => {
  const icons: Record<string, string> = {
    '人工智能': '🤖',
    '经济学': '💰',
    '哲学': '🧠',
    '计算机科学': '💻',
    '生物学': '🧬',
    '物理学': '⚛️',
    '历史': '📚',
    '心理学': '🧘'
  }
  return icons[domain] || '📖'
}

// 探索领域（TODO: 实现推荐逻辑）
const handleExploreDomain = (domain: string) => {
  console.log('🔍 探索领域:', domain)
  // TODO: 跳转到推荐文章或搜索
  alert(`探索 ${domain} 领域的功能正在开发中...`)
}
</script>
