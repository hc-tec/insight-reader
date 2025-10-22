/**
 * 公开示例文章 Composable
 *
 * 只提供列表功能，详情复用现有页面（/?articleId=X）
 */

export interface DemoArticle {
  id: number
  title: string
  author?: string
  word_count?: number
  created_at: string
  demo_order?: number
  has_analysis: boolean
}

export interface DemoArticleListResponse {
  total: number
  articles: DemoArticle[]
}

export const useDemoArticles = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase

  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 获取示例文章列表
   */
  const getDemoArticles = async (limit: number = 10, offset: number = 0): Promise<DemoArticleListResponse | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<DemoArticleListResponse>(
        '/api/v1/public/demo/articles',
        {
          baseURL,
          method: 'GET',
          query: { limit, offset }
        }
      )

      console.log('[Demo] 获取示例文章列表成功:', response.total, '篇')
      return response

    } catch (err: any) {
      console.error('[Demo] 获取示例文章列表失败:', err)
      error.value = err.data?.detail || '获取失败'
      return null

    } finally {
      loading.value = false
    }
  }

  return {
    loading: readonly(loading),
    error: readonly(error),
    getDemoArticles
  }
}
