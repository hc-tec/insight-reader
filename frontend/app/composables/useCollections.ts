/**
 * 收藏管理 Composable
 */
import type {
  InsightCardCreate,
  InsightCardResponse,
  InsightCardListResponse
} from '~/types/collection'
import type { Intent } from '~/types/insight'

export const useCollections = () => {
  const config = useRuntimeConfig()
  const { getAuthHeaders, isAuthenticated } = useAuth()

  const collections = useState<InsightCardResponse[]>('collections', () => [])
  const total = useState<number>('collections-total', () => 0)
  const isLoading = useState<boolean>('collections-loading', () => false)
  const error = useState<string | null>('collections-error', () => null)

  // 获取收藏列表
  const fetchCollections = async (params?: {
    skip?: number
    limit?: number
    intent?: Intent
    search?: string
  }) => {
    if (!isAuthenticated.value) {
      error.value = '请先登录'
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const queryParams = new URLSearchParams()
      if (params?.skip) queryParams.append('skip', params.skip.toString())
      if (params?.limit) queryParams.append('limit', params.limit.toString())
      if (params?.intent) queryParams.append('intent', params.intent)
      if (params?.search) queryParams.append('search', params.search)

      const url = `${config.public.apiBase}/api/v1/collections?${queryParams}`

      const response = await fetch(url, {
        headers: getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('获取收藏列表失败')
      }

      const data: InsightCardListResponse = await response.json()
      collections.value = data.items
      total.value = data.total
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取收藏列表失败'
    } finally {
      isLoading.value = false
    }
  }

  // 创建收藏
  const createCollection = async (data: InsightCardCreate) => {
    if (!isAuthenticated.value) {
      throw new Error('请先登录')
    }

    try {
      const response = await fetch(`${config.public.apiBase}/api/v1/collections`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        throw new Error('收藏失败')
      }

      const newCard: InsightCardResponse = await response.json()

      // 添加到列表开头
      collections.value.unshift(newCard)
      total.value += 1

      return { success: true, card: newCard }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : '收藏失败'
      }
    }
  }

  // 删除收藏
  const deleteCollection = async (cardId: number) => {
    if (!isAuthenticated.value) {
      throw new Error('请先登录')
    }

    try {
      const response = await fetch(`${config.public.apiBase}/api/v1/collections/${cardId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('删除失败')
      }

      // 从列表中移除
      collections.value = collections.value.filter(c => c.id !== cardId)
      total.value -= 1

      return { success: true }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : '删除失败'
      }
    }
  }

  // 更新收藏标签
  const updateCollectionTags = async (cardId: number, tags: string[]) => {
    if (!isAuthenticated.value) {
      throw new Error('请先登录')
    }

    try {
      const response = await fetch(`${config.public.apiBase}/api/v1/collections/${cardId}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify({ tags })
      })

      if (!response.ok) {
        throw new Error('更新失败')
      }

      const updatedCard: InsightCardResponse = await response.json()

      // 更新列表中的项
      const index = collections.value.findIndex(c => c.id === cardId)
      if (index !== -1) {
        collections.value[index] = updatedCard
      }

      return { success: true, card: updatedCard }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : '更新失败'
      }
    }
  }

  // 保存洞察到收藏（简化版）
  const saveInsight = async (data: {
    selected_text: string
    context: string
    intent: Intent
    custom_question?: string
    insight: string
  }) => {
    const collectionData: InsightCardCreate = {
      selected_text: data.selected_text,
      context: data.context,
      intent: data.intent,
      custom_question: data.custom_question,
      insight: data.insight,
      tags: []
    }

    return await createCollection(collectionData)
  }

  return {
    collections: readonly(collections),
    total: readonly(total),
    isLoading: readonly(isLoading),
    error: readonly(error),
    fetchCollections,
    createCollection,
    deleteCollection,
    updateCollectionTags,
    saveInsight
  }
}
