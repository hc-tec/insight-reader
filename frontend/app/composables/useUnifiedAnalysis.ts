/**
 * 统一分析 Composable（异步版本）
 * 使用后台任务和 SSE 进行非阻塞分析
 */

import { ref } from 'vue'
import { useTaskProgress } from './useTaskProgress'

export interface SaveArticleRequest {
  title: string
  author?: string
  source_url?: string
  content: string
  user_id?: number
}

export interface SaveArticleResponse {
  article: {
    id: number
    is_new: boolean
  }
  analysis: {
    status: 'completed' | 'pending' | 'processing'
    task_id: string | null
  }
}

export interface AnalysisReport {
  report_data: {
    meta_info: any
    concept_sparks: any[]
    argument_sparks: any[]
    knowledge_graph_nodes: string[]
    summary: string
    tags: string[]
    sentences: string[]
  }
  metadata: {
    model_used: string
    tokens_used: number
    processing_time_ms: number
    completed_at: string
  }
}

export function useUnifiedAnalysis() {
  const { progress, subscribe, cancel, cleanup } = useTaskProgress()

  const isAnalyzing = ref(false)
  const articleId = ref<number | null>(null)
  const analysisReport = ref<AnalysisReport | null>(null)
  const error = ref<string | null>(null)

  /**
   * 保存文章并触发分析
   *
   * @param request - 文章数据
   * @param onComplete - 分析完成回调
   * @param onError - 错误回调
   */
  const saveAndAnalyze = async (
    request: SaveArticleRequest,
    onComplete?: (report: AnalysisReport) => void,
    onError?: (err: string) => void
  ) => {
    isAnalyzing.value = true
    error.value = null
    analysisReport.value = null

    try {
      const apiBase = useRuntimeConfig().public.apiBase || ''

      // 1. 提交分析任务
      console.log('[UnifiedAnalysis] Submitting article for analysis...')

      const response = await $fetch<SaveArticleResponse>(
        `${apiBase}/api/v1/articles/save-with-analysis`,
        {
          method: 'POST',
          body: request
        }
      )

      articleId.value = response.article.id

      console.log('[UnifiedAnalysis] Article saved:', response.article)

      // 2. 检查分析状态
      if (response.analysis.status === 'completed') {
        // 已有分析结果，直接获取
        console.log('[UnifiedAnalysis] Analysis already completed, fetching report...')

        const report = await fetchAnalysisReport(response.article.id)
        analysisReport.value = report
        isAnalyzing.value = false

        onComplete?.(report)

        return {
          articleId: response.article.id,
          report
        }
      } else if (response.analysis.task_id) {
        // 订阅 SSE 事件
        console.log('[UnifiedAnalysis] Subscribing to task:', response.analysis.task_id)

        subscribe(response.analysis.task_id, {
          onProgress: (prog) => {
            console.log('[UnifiedAnalysis] Progress:', prog)
          },
          onComplete: async (result) => {
            console.log('[UnifiedAnalysis] Task completed:', result)

            // 获取完整报告
            try {
              const report = await fetchAnalysisReport(response.article.id)
              analysisReport.value = report
              isAnalyzing.value = false

              onComplete?.(report)
            } catch (err: any) {
              console.error('[UnifiedAnalysis] Failed to fetch report:', err)
              error.value = err.message || '获取分析报告失败'
              isAnalyzing.value = false

              onError?.(error.value)
            }
          },
          onError: (err) => {
            console.error('[UnifiedAnalysis] Task failed:', err)
            error.value = err
            isAnalyzing.value = false

            onError?.(err)
          }
        })

        return {
          articleId: response.article.id,
          taskId: response.analysis.task_id
        }
      }
    } catch (err: any) {
      console.error('[UnifiedAnalysis] Failed to submit article:', err)
      error.value = err.message || '提交分析失败'
      isAnalyzing.value = false

      onError?.(error.value)

      throw err
    }
  }

  /**
   * 获取分析报告
   *
   * @param articleId - 文章 ID
   */
  const fetchAnalysisReport = async (
    id: number
  ): Promise<AnalysisReport> => {
    try {
      const apiBase = useRuntimeConfig().public.apiBase || ''

      const report = await $fetch<AnalysisReport>(
        `${apiBase}/api/v1/articles/${id}/analysis-report`
      )

      console.log('[UnifiedAnalysis] Report fetched:', report)

      return report
    } catch (err: any) {
      console.error('[UnifiedAnalysis] Failed to fetch report:', err)
      throw new Error('获取分析报告失败')
    }
  }

  /**
   * 获取分析状态
   *
   * @param articleId - 文章 ID
   */
  const getAnalysisStatus = async (id: number) => {
    try {
      const apiBase = useRuntimeConfig().public.apiBase || ''

      const status = await $fetch<any>(
        `${apiBase}/api/v1/articles/${id}/analysis-status`
      )

      return status
    } catch (err: any) {
      console.error('[UnifiedAnalysis] Failed to get status:', err)
      throw err
    }
  }

  /**
   * 重新分析
   *
   * @param id - 文章 ID
   * @param onComplete - 完成回调
   * @param onError - 错误回调
   */
  const reanalyze = async (
    id: number,
    onComplete?: (report: AnalysisReport) => void,
    onError?: (err: string) => void
  ) => {
    isAnalyzing.value = true
    error.value = null

    try {
      const apiBase = useRuntimeConfig().public.apiBase || ''

      console.log('[UnifiedAnalysis] Requesting reanalysis for article:', id)

      const response = await $fetch<{ task_id: string; message: string }>(
        `${apiBase}/api/v1/articles/${id}/reanalyze`,
        {
          method: 'POST'
        }
      )

      // 订阅 SSE 事件
      subscribe(response.task_id, {
        onComplete: async (result) => {
          console.log('[UnifiedAnalysis] Reanalysis completed:', result)

          // 获取新报告
          try {
            const report = await fetchAnalysisReport(id)
            analysisReport.value = report
            isAnalyzing.value = false

            onComplete?.(report)
          } catch (err: any) {
            error.value = err.message || '获取分析报告失败'
            isAnalyzing.value = false

            onError?.(error.value)
          }
        },
        onError: (err) => {
          error.value = err
          isAnalyzing.value = false

          onError?.(err)
        }
      })
    } catch (err: any) {
      error.value = err.message || '重新分析失败'
      isAnalyzing.value = false

      onError?.(error.value)

      throw err
    }
  }

  /**
   * 取消当前分析
   *
   * @param taskId - 任务 ID
   */
  const cancelAnalysis = async (taskId: string) => {
    try {
      await cancel(taskId)
      isAnalyzing.value = false
      console.log('[UnifiedAnalysis] Analysis cancelled')
    } catch (err) {
      console.error('[UnifiedAnalysis] Failed to cancel:', err)
    }
  }

  return {
    // 状态
    isAnalyzing,
    progress,
    articleId,
    analysisReport,
    error,

    // 方法
    saveAndAnalyze,
    fetchAnalysisReport,
    getAnalysisStatus,
    reanalyze,
    cancelAnalysis,
    cleanup
  }
}
