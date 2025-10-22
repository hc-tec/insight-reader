/**
 * 管理员示例文章管理 Composable
 *
 * **需要管理员权限**
 */

import type { Ref } from 'vue'

/**
 * 管理员视图的文章信息
 */
export interface AdminArticle {
  id: number
  title: string
  author?: string
  demo_order?: number
  word_count?: number
  has_analysis: boolean
  has_meta_analysis: boolean
  created_at: string
  owner_id?: number
  is_demo?: boolean
}

/**
 * 标记请求
 */
export interface MarkDemoRequest {
  demo_order?: number
}

/**
 * 管理员示例文章管理
 */
export const useAdminDemo = () => {
  const config = useRuntimeConfig()
  const { token } = useAuth()
  const baseURL = config.public.apiBase

  // 状态管理
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 检查请求头
   */
  const getHeaders = () => {
    if (!token.value) {
      throw new Error('需要登录')
    }
    return {
      'Authorization': `Bearer ${token.value}`
    }
  }

  /**
   * 获取所有示例文章（管理员视图）
   */
  const getDemoArticles = async (): Promise<AdminArticle[] | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<{ total: number; articles: AdminArticle[] }>(
        '/api/v1/admin/demo/articles',
        {
          baseURL,
          method: 'GET',
          headers: getHeaders()
        }
      )

      console.log('[Admin] 获取示例文章列表成功:', response.total, '篇')
      return response.articles

    } catch (err: any) {
      console.error('[Admin] 获取示例文章列表失败:', err)

      if (err.statusCode === 403) {
        error.value = '需要管理员权限'
      } else {
        error.value = err.data?.detail || '获取失败'
      }

      return null

    } finally {
      loading.value = false
    }
  }

  /**
   * 获取所有文章（用于选择标记为示例）
   */
  const getAllArticles = async (): Promise<AdminArticle[] | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<{ total: number; articles: any[] }>(
        '/api/v1/articles',
        {
          baseURL,
          method: 'GET',
          headers: getHeaders(),
          query: {
            limit: 100,
            offset: 0
          }
        }
      )

      console.log('[Admin] 获取所有文章成功:', response.total, '篇')
      return response.articles.map((article: any) => ({
        id: article.id,
        title: article.title,
        author: article.author,
        word_count: article.word_count,
        created_at: article.created_at,
        is_demo: false,
        has_analysis: false,
        has_meta_analysis: false
      }))

    } catch (err: any) {
      console.error('[Admin] 获取文章列表失败:', err)
      error.value = err.data?.detail || '获取失败'
      return null

    } finally {
      loading.value = false
    }
  }

  /**
   * 标记文章为示例
   */
  const markAsDemo = async (
    articleId: number,
    request: MarkDemoRequest = {}
  ): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      await $fetch(
        `/api/v1/admin/demo/articles/${articleId}/mark`,
        {
          baseURL,
          method: 'POST',
          headers: getHeaders(),
          body: {
            demo_order: request.demo_order
          }
        }
      )

      console.log('[Admin] 文章已标记为示例:', articleId)
      return true

    } catch (err: any) {
      console.error('[Admin] 标记失败:', err)
      error.value = err.data?.detail || '标记失败'
      return false

    } finally {
      loading.value = false
    }
  }

  /**
   * 取消示例标记
   */
  const unmarkDemo = async (articleId: number): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      await $fetch(
        `/api/v1/admin/demo/articles/${articleId}/unmark`,
        {
          baseURL,
          method: 'DELETE',
          headers: getHeaders()
        }
      )

      console.log('[Admin] 已取消示例标记:', articleId)
      return true

    } catch (err: any) {
      console.error('[Admin] 取消标记失败:', err)
      error.value = err.data?.detail || '操作失败'
      return false

    } finally {
      loading.value = false
    }
  }

  /**
   * 更新展示顺序
   */
  const updateOrder = async (
    articleId: number,
    order: number
  ): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      await $fetch(
        `/api/v1/admin/demo/articles/${articleId}/order`,
        {
          baseURL,
          method: 'PUT',
          headers: getHeaders(),
          query: { order }
        }
      )

      console.log('[Admin] 顺序已更新:', articleId, '→', order)
      return true

    } catch (err: any) {
      console.error('[Admin] 更新顺序失败:', err)
      error.value = err.data?.detail || '更新失败'
      return false

    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    loading: readonly(loading),
    error: readonly(error),

    // 方法
    getDemoArticles,
    getAllArticles,
    markAsDemo,
    unmarkDemo,
    updateOrder
  }
}
