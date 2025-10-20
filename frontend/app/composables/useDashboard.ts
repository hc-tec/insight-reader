/**
 * 仪表盘 Composable
 * 负责获取和管理仪表盘数据（知识图谱、好奇心指纹、盲区）
 */

export interface KnowledgeNode {
  id: string
  label: string
  type: 'concept' | 'entity'
  size: number
  color: string
  metadata: {
    domain: string
    insightId: number
    createdAt: string
    reviewCount: number
  }
}

export interface KnowledgeEdge {
  id: string
  source: string
  target: string
  type: 'related' | 'contrast' | 'depends_on'
  weight: number
  label?: string
}

export interface KnowledgeGraphData {
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
  stats: {
    totalNodes: number
    totalEdges: number
    domains: Record<string, number>
    latestUpdate: string | null
  }
}

export interface CuriosityFingerprintData {
  spark_distribution: Record<string, number>
  time_series: Array<{
    date: string
    counts: Record<string, number>
  }>
  topic_cloud: Array<{
    topic: string
    count: number
    weight: number
  }>
  last_updated: string
}

export interface BlindSpotData {
  missingDomains: string[]
  knowledgeIslands: Array<{
    id: string
    concepts: string[]
    recommendation: string
  }>
  crossDomainSuggestions: any[]
}

export interface DashboardOverview {
  knowledgeGraph: {
    totalNodes: number
    totalEdges: number
    domains: Record<string, number>
  }
  curiosityFingerprint: {
    sparkDistribution: Record<string, number>
    dominantType: string | null
  }
  blindSpots: {
    missingDomains: string[]
    knowledgeIslands: number
  }
  stats: {
    totalSparkClicks: number
    activeDays: number
  }
}

export const useDashboard = () => {
  const config = useRuntimeConfig()

  // 状态
  const overview = useState<DashboardOverview | null>('dashboard-overview', () => null)
  const knowledgeGraph = useState<KnowledgeGraphData | null>('knowledge-graph', () => null)
  const curiosityFingerprint = useState<CuriosityFingerprintData | null>('curiosity-fingerprint', () => null)
  const blindSpots = useState<BlindSpotData | null>('blind-spots', () => null)

  const isLoading = useState<boolean>('dashboard-loading', () => false)
  const error = useState<string | null>('dashboard-error', () => null)

  /**
   * 获取仪表盘总览
   */
  const fetchOverview = async (userId: number) => {
    if (!userId) {
      console.warn('⚠️ 用户 ID 未提供')
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const data = await $fetch<DashboardOverview>(
        `${config.public.apiBase}/api/v1/dashboard/`,
        {
          method: 'GET',
          params: { user_id: userId }
        }
      )

      overview.value = data
      console.log('✅ 仪表盘总览获取成功:', data)
      return data
    } catch (err) {
      console.error('❌ 仪表盘总览获取失败:', err)
      error.value = err instanceof Error ? err.message : '获取失败'
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 获取知识图谱数据
   */
  const fetchKnowledgeGraph = async (userId: number) => {
    if (!userId) {
      console.warn('⚠️ 用户 ID 未提供')
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const data = await $fetch<KnowledgeGraphData>(
        `${config.public.apiBase}/api/v1/dashboard/knowledge-graph`,
        {
          method: 'GET',
          params: { user_id: userId }
        }
      )

      knowledgeGraph.value = data
      console.log('✅ 知识图谱获取成功:', data.stats)
      return data
    } catch (err) {
      console.error('❌ 知识图谱获取失败:', err)
      error.value = err instanceof Error ? err.message : '获取失败'
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 重建知识图谱
   */
  const rebuildKnowledgeGraph = async (userId: number) => {
    if (!userId) {
      console.warn('⚠️ 用户 ID 未提供')
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const result = await $fetch<{ nodes_created: number; edges_created: number; message: string }>(
        `${config.public.apiBase}/api/v1/dashboard/knowledge-graph/rebuild`,
        {
          method: 'POST',
          params: { user_id: userId }
        }
      )

      console.log('✅ 知识图谱重建成功:', result)

      // 重建后重新获取数据
      await fetchKnowledgeGraph(userId)

      return result
    } catch (err) {
      console.error('❌ 知识图谱重建失败:', err)
      error.value = err instanceof Error ? err.message : '重建失败'
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 获取好奇心指纹
   */
  const fetchCuriosityFingerprint = async (userId: number) => {
    if (!userId) {
      console.warn('⚠️ 用户 ID 未提供')
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const data = await $fetch<CuriosityFingerprintData>(
        `${config.public.apiBase}/api/v1/dashboard/curiosity-fingerprint`,
        {
          method: 'GET',
          params: { user_id: userId }
        }
      )

      curiosityFingerprint.value = data
      console.log('✅ 好奇心指纹获取成功:', data)
      return data
    } catch (err) {
      console.error('❌ 好奇心指纹获取失败:', err)
      error.value = err instanceof Error ? err.message : '获取失败'
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 获取思维盲区
   */
  const fetchBlindSpots = async (userId: number) => {
    if (!userId) {
      console.warn('⚠️ 用户 ID 未提供')
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const data = await $fetch<BlindSpotData>(
        `${config.public.apiBase}/api/v1/dashboard/blind-spots`,
        {
          method: 'GET',
          params: { user_id: userId }
        }
      )

      blindSpots.value = data
      console.log('✅ 思维盲区获取成功:', data)
      return data
    } catch (err) {
      console.error('❌ 思维盲区获取失败:', err)
      error.value = err instanceof Error ? err.message : '获取失败'
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 记录火花点击（埋点）
   */
  const recordSparkClick = async (
    userId: number,
    sparkType: string,
    sparkText: string,
    articleId?: number
  ) => {
    try {
      await $fetch(
        `${config.public.apiBase}/api/v1/analytics/spark-click`,
        {
          method: 'POST',
          body: {
            user_id: userId,
            spark_type: sparkType,
            spark_text: sparkText,
            article_id: articleId
          }
        }
      )

      console.log('✅ 火花点击已记录:', sparkType, sparkText.substring(0, 20))
    } catch (err) {
      console.error('❌ 火花点击记录失败:', err)
    }
  }

  /**
   * 获取主导类型文本
   */
  const getDominantTypeText = computed(() => {
    if (!curiosityFingerprint.value) return ''

    const { spark_distribution } = curiosityFingerprint.value
    const concept = spark_distribution.concept || 0
    const argument = spark_distribution.argument || 0

    if (concept > argument * 1.5) {
      return '💡 你是概念探索者：喜欢深挖专业术语和理论框架'
    } else if (argument > concept * 1.5) {
      return '🔍 你是逻辑思考者：关注论证过程和数据证据'
    } else if (concept > 0 || argument > 0) {
      return '⚖️ 你是均衡学习者：概念和论证并重'
    } else {
      return '🌟 开始你的阅读之旅吧'
    }
  })

  return {
    // 状态
    overview: readonly(overview),
    knowledgeGraph: readonly(knowledgeGraph),
    curiosityFingerprint: readonly(curiosityFingerprint),
    blindSpots: readonly(blindSpots),
    isLoading: readonly(isLoading),
    error: readonly(error),

    // 计算属性
    getDominantTypeText,

    // 方法
    fetchOverview,
    fetchKnowledgeGraph,
    rebuildKnowledgeGraph,
    fetchCuriosityFingerprint,
    fetchBlindSpots,
    recordSparkClick
  }
}
