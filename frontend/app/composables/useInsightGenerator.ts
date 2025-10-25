/**
 * 洞察生成 Composable
 */
import type { InsightRequest, Intent } from '~/types/insight'

export const useInsightGenerator = () => {
  const isGenerating = useState<boolean>('is-generating', () => false)
  const currentInsight = useState<string>('current-insight', () => '')
  const currentReasoning = useState<string>('current-reasoning', () => '')
  const currentInsightId = useState<number | null>('current-insight-id', () => null)  // 当前洞察的 ID
  const error = useState<string | null>('insight-error', () => null)
  const { addHistoryItem } = useHistory()
  const { title, content } = useArticle()
  const { selectedStart, selectedEnd } = useSelection()
  const { user } = useAuth()
  const currentArticleId = useState<number | null>('current-article-id', () => null)
  const config = useRuntimeConfig()

  // 获取 SSE 实例（保持引用以便停止）
  const { connect, abort: abortSSE } = useSSE()

  const generate = async (request: InsightRequest) => {
    isGenerating.value = true
    currentInsight.value = ''
    currentReasoning.value = ''
    error.value = null

    try {
      await connect('/api/v1/insights/generate', request, {
        onStart: () => {
          currentInsight.value = ''
          currentReasoning.value = ''
          console.log('🚀 开始生成洞察，推理模式:', request.use_reasoning)
        },
        onDelta: (content: string) => {
          currentInsight.value += content
          console.log('📝 收到内容片段:', content.substring(0, 50))
        },
        onReasoning: (content: string) => {
          currentReasoning.value += content
          console.log('🧠 收到推理片段:', content.substring(0, 50))
        },
        onComplete: async (metadata) => {
          isGenerating.value = false
          console.log('✅ 洞察生成完成', {
            metadata,
            hasReasoning: !!currentReasoning.value,
            reasoningLength: currentReasoning.value.length
          })

          // 注意：初始洞察不添加到 conversationHistory 中
          // 因为它会显示在 currentInsight 区域（顶部）
          // conversationHistory 只用于显示追问对话
          // 当需要追问时，通过 currentInsightId 来追踪初始洞察的 ID

          // 保存到本地历史记录
          if (currentInsight.value) {
            addHistoryItem({
              selectedText: request.selected_text,
              context: request.context,
              intent: request.intent,
              customQuestion: request.custom_question,
              insight: currentInsight.value,
              articleTitle: title.value
            })
          }

          // 保存到后端洞察历史（如果用户已登录且有文章ID）
          console.log('🔍 检查是否保存到后端:', {
            hasInsight: !!currentInsight.value,
            hasUser: !!user.value?.id,
            hasArticleId: !!currentArticleId.value,
            userId: user.value?.id,
            articleId: currentArticleId.value
          })

          if (currentInsight.value && user.value?.id && currentArticleId.value) {
            try {
              // 提取上下文（前后各100字符）
              const articleText = content.value
              const start = selectedStart.value || 0
              const end = selectedEnd.value || 0

              const contextBefore = start > 0
                ? articleText.substring(Math.max(0, start - 100), start)
                : ''

              const contextAfter = end < articleText.length
                ? articleText.substring(end, Math.min(articleText.length, end + 100))
                : ''

              const response = await $fetch<{ status: string; insight_history_id: number }>(`${config.public.apiBase}/api/v1/insights/history`, {
                method: 'POST',
                body: {
                  article_id: currentArticleId.value,
                  selected_text: request.selected_text,
                  selected_start: selectedStart.value,
                  selected_end: selectedEnd.value,
                  context_before: contextBefore,
                  context_after: contextAfter,
                  intent: request.intent,
                  question: request.custom_question || null,
                  insight: currentInsight.value,
                  reasoning: currentReasoning.value || null,
                  parent_id: null  // 初始洞察没有 parent
                }
              })

              // 保存洞察 ID，用于后续追问
              currentInsightId.value = response.insight_history_id
              console.log('💾 洞察已保存到历史记录，ID:', response.insight_history_id)
            } catch (err) {
              console.error('❌ 保存洞察历史失败:', err)
              // 不影响用户体验，只记录错误
            }
          }
        },
        onError: (err) => {
          error.value = err.message || '生成失败'
          isGenerating.value = false
          console.error('❌ 生成错误:', err)
        }
      })
    } catch (err) {
      error.value = err instanceof Error ? err.message : '网络错误，请重试'
      isGenerating.value = false
    }
  }

  const clear = () => {
    currentInsight.value = ''
    currentReasoning.value = ''
    error.value = null
    isGenerating.value = false
  }

  // 停止生成
  const stopGeneration = () => {
    abortSSE()
    isGenerating.value = false
    console.log('⏹️ 停止洞察生成')
  }

  return {
    isGenerating,
    currentInsight,
    currentReasoning,
    currentInsightId,
    error,
    generate,
    clear,
    stopGeneration  // 导出停止方法
  }
}
