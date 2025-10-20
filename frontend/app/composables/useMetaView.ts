/**
 * 元视角模式 Composable
 * 负责元信息分析的状态管理和API调用
 */

export interface AuthorIntent {
  primary: 'inform' | 'persuade' | 'entertain' | 'provoke'
  confidence: number
  description: string
  indicators: string[]
}

export interface TimelinessAnalysis {
  score: number
  category: 'timeless' | 'evergreen' | 'time-sensitive' | 'breaking'
  decay_rate: 'low' | 'medium' | 'high'
  best_before: string | null
  context_dependencies: string[]
}

export interface BiasExample {
  text: string
  type: string
  explanation: string
}

export interface BiasAnalysis {
  detected: boolean
  types: string[]
  severity: 'low' | 'medium' | 'high'
  examples: BiasExample[]
  overall_balance: 'balanced' | 'slightly_biased' | 'heavily_biased'
}

export interface KnowledgeGaps {
  prerequisites: string[]
  assumptions: string[]
  missing_context: string[]
  related_concepts: string[]
}

export interface AnalysisQuality {
  confidence_score: number
  processing_time_ms: number
  llm_model: string
  prompt_version: string
}

export interface MetaAnalysisData {
  id: number
  article_id: number
  author_intent: AuthorIntent
  timeliness_score: number
  timeliness_analysis: TimelinessAnalysis
  bias_analysis: BiasAnalysis
  knowledge_gaps: KnowledgeGaps
  analysis_quality: AnalysisQuality
  created_at: string
  updated_at: string
}

export const useMetaView = () => {
  const config = useRuntimeConfig()

  // 状态
  const isMetaViewActive = useState<boolean>('meta-view-active', () => false)
  const metaAnalysisData = useState<MetaAnalysisData | null>('meta-analysis-data', () => null)
  const isAnalyzing = useState<boolean>('meta-view-analyzing', () => false)
  const analysisError = useState<string | null>('meta-view-error', () => null)

  /**
   * 触发元信息分析
   */
  const analyzeArticle = async (
    title: string,
    author: string,
    publishDate: string,
    fullText: string,
    userId?: number,
    sourceUrl?: string,
    language: string = 'zh',
    forceReanalyze: boolean = false
  ) => {
    isAnalyzing.value = true
    analysisError.value = null

    try {
      const response = await $fetch<{ status: string; meta_analysis: MetaAnalysisData }>(
        `${config.public.apiBase}/api/v1/meta-analysis/analyze`,
        {
          method: 'POST',
          body: {
            title,
            author,
            publish_date: publishDate,
            full_text: fullText,
            user_id: userId,
            source_url: sourceUrl,
            language,
            force_reanalyze: forceReanalyze
          }
        }
      )

      metaAnalysisData.value = response.meta_analysis
      console.log('✅ 元信息分析完成:', response.meta_analysis.id)

      return response.meta_analysis

    } catch (error: any) {
      console.error('❌ 元信息分析失败:', error)
      analysisError.value = error.data?.detail || error.message || '分析失败'
      throw error
    } finally {
      isAnalyzing.value = false
    }
  }

  /**
   * 获取已有的元信息分析结果
   */
  const fetchMetaAnalysis = async (articleId: number) => {
    try {
      const response = await $fetch<{ exists: boolean; meta_analysis: MetaAnalysisData | null }>(
        `${config.public.apiBase}/api/v1/meta-analysis/${articleId}`
      )

      if (response.exists && response.meta_analysis) {
        metaAnalysisData.value = response.meta_analysis
        console.log('✅ 获取到元信息分析:', response.meta_analysis.id)
        return true
      }

      return false

    } catch (error) {
      console.error('❌ 获取元信息失败:', error)
      return false
    }
  }

  /**
   * 切换元视角模式
   */
  const toggleMetaView = () => {
    isMetaViewActive.value = !isMetaViewActive.value
  }

  /**
   * 关闭元视角
   */
  const closeMetaView = () => {
    isMetaViewActive.value = false
  }

  /**
   * 打开元视角
   */
  const openMetaView = () => {
    isMetaViewActive.value = true
  }

  /**
   * 清空数据
   */
  const clearMetaAnalysis = () => {
    metaAnalysisData.value = null
    analysisError.value = null
  }

  /**
   * 提交反馈
   */
  const submitFeedback = async (
    userId: number,
    feedbackType: string,
    metaAnalysisId?: number,
    lensResultId?: number,
    rating?: number,
    comment?: string,
    feedbackData?: any
  ) => {
    try {
      await $fetch(`${config.public.apiBase}/api/v1/meta-analysis/feedback`, {
        method: 'POST',
        body: {
          user_id: userId,
          meta_analysis_id: metaAnalysisId,
          lens_result_id: lensResultId,
          feedback_type: feedbackType,
          rating,
          comment,
          feedback_data: feedbackData
        }
      })

      console.log('✅ 反馈已提交')

    } catch (error) {
      console.error('❌ 提交反馈失败:', error)
      throw error
    }
  }

  return {
    // 状态
    isMetaViewActive: readonly(isMetaViewActive),
    metaAnalysisData: readonly(metaAnalysisData),
    isAnalyzing: readonly(isAnalyzing),
    analysisError: readonly(analysisError),

    // 方法
    analyzeArticle,
    fetchMetaAnalysis,
    toggleMetaView,
    closeMetaView,
    openMetaView,
    clearMetaAnalysis,
    submitFeedback
  }
}
