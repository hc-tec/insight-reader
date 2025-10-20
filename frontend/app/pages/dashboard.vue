<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-zinc-50 relative overflow-hidden">
    <!-- 全屏背景装饰 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-emerald-400/10 rounded-full blur-3xl"></div>
      <div class="absolute top-1/3 -left-40 w-80 h-80 bg-teal-400/10 rounded-full blur-3xl"></div>
      <div class="absolute bottom-20 right-1/3 w-64 h-64 bg-slate-400/10 rounded-full blur-3xl"></div>
    </div>

    <!-- 内容区域 -->
    <div class="relative z-10">
      <AppHeader />

      <!-- 页面头部 -->
      <div class="max-w-7xl mx-auto px-6 pt-8 pb-6">
        <div class="mb-6">
          <h1 class="text-4xl font-bold bg-gradient-to-r from-slate-800 via-slate-700 to-zinc-700 bg-clip-text text-transparent mb-2">
            个人认知仪表盘
          </h1>
          <p class="text-gray-600 text-lg">
            可视化你的知识资产，发现思维模式，探索认知盲区
          </p>
        </div>

        <!-- 总览统计卡片 -->
        <div v-if="overview" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <!-- 知识节点 -->
          <div class="group bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all hover:-translate-y-1">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg transition-all group-hover:scale-110">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <div class="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  {{ overview.knowledgeGraph.totalNodes }}
                </div>
                <div class="text-sm text-gray-600 mt-0.5">知识节点</div>
              </div>
            </div>
          </div>

          <!-- 关系连接 -->
          <div class="group bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all hover:-translate-y-1">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-gradient-to-br from-slate-500 to-zinc-600 rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg transition-all group-hover:scale-110">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
              <div>
                <div class="text-3xl font-bold bg-gradient-to-r from-slate-600 to-zinc-600 bg-clip-text text-transparent">
                  {{ overview.knowledgeGraph.totalEdges }}
                </div>
                <div class="text-sm text-gray-600 mt-0.5">关系连接</div>
              </div>
            </div>
          </div>

          <!-- 火花点击 -->
          <div class="group bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all hover:-translate-y-1">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg transition-all group-hover:scale-110">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <div class="text-3xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                  {{ overview.stats.totalSparkClicks }}
                </div>
                <div class="text-sm text-gray-600 mt-0.5">火花点击</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="max-w-7xl mx-auto px-6 pb-12">
        <div v-if="userId" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 左侧：知识图谱 -->
          <div>
            <KnowledgeGraph :user-id="userId" />
          </div>

          <!-- 右侧：指标面板 -->
          <div class="space-y-6">
            <!-- 好奇心指纹 -->
            <CuriosityFingerprint :user-id="userId" />

            <!-- 思维盲区 -->
            <BlindSpotDetector :user-id="userId" />
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-else-if="isLoading" class="flex items-center justify-center py-20">
          <div class="animate-spin h-12 w-12 border-4 border-emerald-600 border-t-transparent rounded-full"></div>
          <span class="ml-4 text-gray-600">加载中...</span>
        </div>

        <!-- 底部提示 -->
        <div v-if="userId" class="mt-8 bg-gradient-to-r from-emerald-50/80 to-teal-50/80 backdrop-blur-xl border border-emerald-200/50 rounded-2xl p-6 text-center shadow-sm">
          <div class="flex items-center justify-center gap-2 text-emerald-800">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <p class="text-sm font-medium">
              持续点击文章中的火花，让你的知识图谱不断生长
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()
const { isAuthenticated, user } = useAuth()
const { fetchOverview, overview, isLoading } = useDashboard()

// 获取用户 ID
const userId = computed(() => user.value?.id || null)

// 检查登录状态
onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }

  // 加载仪表盘数据
  if (userId.value) {
    await fetchOverview(userId.value)
  }
})

// 监听用户变化
watch(userId, async (newUserId) => {
  if (newUserId) {
    await fetchOverview(newUserId)
  }
})

// 设置页面标题
useHead({
  title: '个人认知仪表盘 - InsightReader'
})
</script>
