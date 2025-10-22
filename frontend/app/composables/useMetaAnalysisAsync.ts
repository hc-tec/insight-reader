/**
 * 元分析 Composable（异步版本）
 * 使用后台任务和 SSE 进行非阻塞分析
 */

import { ref } from 'vue'
import { useTaskProgress } from './useTaskProgress'

export interface MetaAnalysisRequest {
  title: string
  author?: string
  publish_date?: string
  full_text: string
  user_id?: number
  source_url?: string
  language?: string
  force_reanalyze?: boolean
}

export interface MetaAnalysisResult {
  id: number
  article_id: number
  generated_title: string
  author_intent: {
    primary: string
    confidence: number
    description: string
    indicators: string[]
  }
  timeliness_score: number
  timeliness_analysis: {
    score: number
    category: string
    decay_rate: string
    best_before: string | null
    context_dependencies: string[]
  }
  bias_analysis: {
    detected: boolean
    types: string[]
    severity: string
    examples: any[]
    overall_balance: string
  }
  knowledge_gaps: {
    prerequisites: string[]
    assumptions: string[]
    missing_context: string[]
    related_concepts: string[]
  }
  analysis_quality: {
    confidence_score: number
    processing_time_ms: number
    llm_model: string
    prompt_version: string
  }
  created_at: string
  updated_at: string
}

export function useMetaAnalysisAsync() {
  const { progress, subscribe, cancel, cleanup } = useTaskProgress()

  const isAnalyzing = ref(false)
  const metaAnalysis = ref<MetaAnalysisResult | null>(null)
  const error = ref<string | null>(null)

  /**
   * 触发元分析
   *
   * @param request - 文章数据
   * @param onComplete - 完成回调
   * @param onError - 错误回调
   */
  const analyze = async (
    request: MetaAnalysisRequest,
    onComplete?: (result: MetaAnalysisResult) => void,
    onError?: (err: string) => void
  ) => {
    isAnalyzing.value = true
    error.value = null
    metaAnalysis.value = null

    try {
      const apiBase = useRuntimeConfig().public.apiBase || ''

      console.log('[MetaAnalysis] Submitting analysis request...')

      const response = await $fetch<{
        article_id: number
        task_id: string | null
        message: string
        status?: string
      }>(
        `${apiBase}/api/v1/meta-analysis/analyze`,
        {
          method: 'POST',
          body: request
        }
      )

      console.log('[MetaAnalysis] Response:', response)

      // 如果已有结果
      if (response.status === 'completed') {
        console.log('[MetaAnalysis] Already completed, fetching result...')

        const result = await fetchMetaAnalysis(response.article_id)
        metaAnalysis.value = result
        isAnalyzing.value = false

        onComplete?.(result)

        return result
      }

      // 订阅 SSE 事件
      if (response.task_id) {
        console.log('[MetaAnalysis] Subscribing to task:', response.task_id)

        subscribe(response.task_id, {
          onProgress: (prog) => {
            console.log('[MetaAnalysis] Progress:', prog)
          },
          onComplete: async (taskResult) => {
            console.log('[MetaAnalysis] Task completed:', taskResult)

            // 获取元分析结果
            try {
              const result = await fetchMetaAnalysis(response.article_id)
              metaAnalysis.value = result
              isAnalyzing.value = false

              onComplete?.(result)
            } catch (err: any) {
              console.error('[MetaAnalysis] Failed to fetch result:', err)
              error.value = err.message || '获取元分析结果失败'
              isAnalyzing.value = false

              onError?.(error.value)
            }
          },
          onError: (err) => {
            console.error('[MetaAnalysis] Task failed:', err)
            error.value = err
            isAnalyzing.value = false

            onError?.(err)
          }
        })
      }
    } catch (err: any) {
      console.error('[MetaAnalysis] Failed to submit:', err)
      error.value = err.message || '提交元分析失败'
      isAnalyzing.value = false

      onError?.(error.value)

      throw err
    }
  }

  /**
   * 获取元分析结果
   *
   * @param articleId - 文章 ID
   */
  const fetchMetaAnalysis = async (
    articleId: number
  ): Promise<MetaAnalysisResult> => {
    try {
      const apiBase = useRuntimeConfig().public.apiBase || ''

      const response = await $fetch<{
        status: string
        message: string
        meta_analysis: MetaAnalysisResult
      }>(
        `${apiBase}/api/v1/meta-analysis/${articleId}`
      )

      console.log('[MetaAnalysis] Result fetched:', response.meta_analysis)

      return response.meta_analysis
    } catch (err: any) {
      console.error('[MetaAnalysis] Failed to fetch:', err)
      throw new Error('获取元分析结果失败')
    }
  }

  /**
   * 取消元分析
   *
   * @param taskId - 任务 ID
   */
  const cancelAnalysis = async (taskId: string) => {
    try {
      await cancel(taskId)
      isAnalyzing.value = false
      console.log('[MetaAnalysis] Analysis cancelled')
    } catch (err) {
      console.error('[MetaAnalysis] Failed to cancel:', err)
    }
  }

  return {
    // 状态
    isAnalyzing,
    progress,
    metaAnalysis,
    error,

    // 方法
    analyze,
    fetchMetaAnalysis,
    cancelAnalysis,
    cleanup
  }
}
