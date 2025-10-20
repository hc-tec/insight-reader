<template>
  <div class="bg-white/70 backdrop-blur-xl border border-gray-200/50 rounded-2xl shadow-sm overflow-hidden">
    <!-- 头部 -->
    <div class="p-6 border-b border-gray-200/50 bg-gradient-to-r from-slate-50/50 to-zinc-50/50">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-md">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold bg-gradient-to-r from-slate-800 to-zinc-700 bg-clip-text text-transparent">
            知识图谱
          </h3>
        </div>

        <button
          @click="handleRebuild"
          :disabled="isRebuilding"
          class="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white text-sm font-medium rounded-lg shadow-sm hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <svg v-if="!isRebuilding" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <svg v-else class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>{{ isRebuilding ? '构建中...' : '重建图谱' }}</span>
        </button>
      </div>
    </div>

    <!-- 图谱统计 -->
    <div v-if="graphData" class="p-6 border-b border-gray-200/50">
      <div class="grid grid-cols-3 gap-4">
        <div class="text-center">
          <div class="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
            {{ graphData.stats.totalNodes }}
          </div>
          <div class="text-xs text-gray-600 mt-1">概念节点</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold bg-gradient-to-r from-slate-600 to-zinc-600 bg-clip-text text-transparent">
            {{ graphData.stats.totalEdges }}
          </div>
          <div class="text-xs text-gray-600 mt-1">关系连接</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
            {{ Object.keys(graphData.stats.domains).length }}
          </div>
          <div class="text-xs text-gray-600 mt-1">知识领域</div>
        </div>
      </div>
    </div>

    <!-- 领域分布 -->
    <div v-if="graphData && graphData.stats.domains && Object.keys(graphData.stats.domains).length > 0" class="p-6 border-b border-gray-200/50 bg-gradient-to-br from-slate-50/30 to-zinc-50/30">
      <h4 class="text-sm font-semibold text-gray-700 mb-3">领域分布</h4>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="(count, domain) in graphData.stats.domains"
          :key="domain"
          class="px-3 py-1.5 bg-white/80 backdrop-blur border border-gray-200/50 rounded-lg text-xs font-medium text-gray-700 hover:shadow-sm transition-all cursor-pointer"
          @click="filterByDomain(domain as string)"
        >
          <span class="font-semibold">{{ domain }}</span>
          <span class="ml-1.5 text-gray-500">{{ count }}</span>
        </div>
      </div>
    </div>

    <!-- 图谱可视化区域 -->
    <div class="p-6">
      <!-- 空状态 -->
      <div v-if="!graphData || graphData.nodes.length === 0" class="flex flex-col items-center justify-center py-16">
        <div class="w-20 h-20 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-2xl flex items-center justify-center mb-4">
          <svg class="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <p class="text-lg font-semibold text-gray-700 mb-1">暂无知识图谱数据</p>
        <p class="text-sm text-gray-500">开始点击火花，构建你的知识网络</p>
      </div>

      <!-- D3.js 力导向图谱 -->
      <div v-else>
        <!-- 控制面板 -->
        <div class="mb-4 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <button
              @click="resetZoom"
              class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium rounded-lg transition-all"
            >
              重置视图
            </button>
            <button
              @click="toggleSimulation"
              class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium rounded-lg transition-all"
            >
              {{ simulationRunning ? '暂停' : '继续' }}
            </button>
          </div>
          <div class="text-xs text-gray-500">
            拖拽节点 | 滚轮缩放 | 点击查看详情
          </div>
        </div>

        <!-- SVG 画布 -->
        <div ref="graphContainer" class="w-full bg-gradient-to-br from-slate-50/30 to-zinc-50/30 rounded-xl border border-gray-200/50 overflow-hidden">
          <svg ref="svgRef" class="w-full" :height="height"></svg>
        </div>

        <!-- 选中节点详情 -->
        <Transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0 translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-150"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div v-if="selectedNode" class="mt-4 p-4 bg-gradient-to-r from-emerald-50/50 to-teal-50/50 border border-emerald-200/50 rounded-xl">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: selectedNode.color }"></div>
                  <h4 class="font-semibold text-gray-800">{{ selectedNode.label }}</h4>
                </div>
                <div class="text-xs text-gray-600 space-y-1">
                  <p>领域：{{ selectedNode.metadata.domain || '未分类' }}</p>
                  <p>点击次数：{{ selectedNode.size }} 次</p>
                  <p>创建时间：{{ formatDate(selectedNode.metadata.createdAt) }}</p>
                </div>
              </div>
              <button
                @click="selectedNode = null"
                class="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'
import type { KnowledgeGraphData, KnowledgeNode, KnowledgeEdge } from '~/composables/useDashboard'

const props = defineProps<{
  userId: number
}>()

const { fetchKnowledgeGraph, rebuildKnowledgeGraph, knowledgeGraph } = useDashboard()

const graphData = computed(() => knowledgeGraph.value)
const graphContainer = ref<HTMLElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)
const isRebuilding = ref(false)
const height = 500
const selectedNode = ref<KnowledgeNode | null>(null)
const simulationRunning = ref(true)

let simulation: d3.Simulation<any, any> | null = null
let svg: any = null
let g: any = null
let zoom: any = null

// 加载图谱数据
onMounted(async () => {
  await fetchKnowledgeGraph(props.userId)
})

// 监听数据变化，重新渲染图谱
watch(graphData, (newData) => {
  if (newData && newData.nodes.length > 0) {
    nextTick(() => {
      initGraph()
    })
  }
}, { immediate: true })

// 初始化图谱
const initGraph = () => {
  if (!svgRef.value || !graphData.value) return

  // 清空旧的 SVG 内容
  d3.select(svgRef.value).selectAll('*').remove()

  const width = graphContainer.value?.clientWidth || 800

  // 创建 SVG
  svg = d3.select(svgRef.value)
    .attr('width', width)
    .attr('height', height)

  // 创建缩放行为
  zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      g.attr('transform', event.transform)
    })

  svg.call(zoom)

  // 创建主画布组
  g = svg.append('g')

  // 创建力导向模拟
  simulation = d3.forceSimulation(graphData.value.nodes)
    .force('link', d3.forceLink(graphData.value.edges)
      .id((d: any) => d.id)
      .distance(100)
      .strength(0.5)
    )
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius((d: any) => d.size * 3 + 10))

  // 绘制边
  const links = g.append('g')
    .attr('class', 'links')
    .selectAll('line')
    .data(graphData.value.edges)
    .enter().append('line')
    .attr('stroke', '#cbd5e1')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', (d: any) => Math.sqrt(d.weight) * 2)

  // 绘制节点组
  const nodeGroups = g.append('g')
    .attr('class', 'nodes')
    .selectAll('g')
    .data(graphData.value.nodes)
    .enter().append('g')
    .call(drag(simulation) as any)
    .on('click', (_event: any, d: any) => {
      selectedNode.value = d
    })

  // 节点圆圈
  nodeGroups.append('circle')
    .attr('r', (d: any) => Math.max(d.size * 2 + 5, 8))
    .attr('fill', (d: any) => d.color)
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .attr('class', 'node-circle')
    .style('cursor', 'pointer')
    .on('mouseenter', function() {
      d3.select(this).transition().duration(200)
        .attr('r', function(d: any) { return Math.max(d.size * 2 + 8, 11) })
        .attr('stroke-width', 3)
    })
    .on('mouseleave', function() {
      d3.select(this).transition().duration(200)
        .attr('r', function(d: any) { return Math.max(d.size * 2 + 5, 8) })
        .attr('stroke-width', 2)
    })

  // 节点标签
  nodeGroups.append('text')
    .text((d: any) => d.label)
    .attr('x', 0)
    .attr('y', (d: any) => Math.max(d.size * 2 + 5, 8) + 15)
    .attr('text-anchor', 'middle')
    .attr('fill', '#475569')
    .attr('font-size', '11px')
    .attr('font-weight', '600')
    .attr('pointer-events', 'none')

  // 更新位置
  simulation.on('tick', () => {
    links
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y)

    nodeGroups
      .attr('transform', (d: any) => `translate(${d.x},${d.y})`)
  })
}

// 拖拽行为
const drag = (simulation: any) => {
  function dragstarted(event: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    event.subject.fx = event.subject.x
    event.subject.fy = event.subject.y
  }

  function dragged(event: any) {
    event.subject.fx = event.x
    event.subject.fy = event.y
  }

  function dragended(event: any) {
    if (!event.active) simulation.alphaTarget(0)
    event.subject.fx = null
    event.subject.fy = null
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended)
}

// 重置视图
const resetZoom = () => {
  if (svg && zoom) {
    svg.transition().duration(750).call(
      zoom.transform,
      d3.zoomIdentity
    )
  }
}

// 切换模拟
const toggleSimulation = () => {
  if (!simulation) return

  if (simulationRunning.value) {
    simulation.stop()
  } else {
    simulation.alpha(0.3).restart()
  }
  simulationRunning.value = !simulationRunning.value
}

// 按领域筛选（TODO: 实现筛选逻辑）
const filterByDomain = (domain: string) => {
  console.log('筛选领域:', domain)
  // TODO: 实现领域筛选可视化
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 重建图谱
const handleRebuild = async () => {
  isRebuilding.value = true
  await rebuildKnowledgeGraph(props.userId)
  isRebuilding.value = false
}

// 组件卸载时清理
onUnmounted(() => {
  if (simulation) {
    simulation.stop()
  }
})
</script>
