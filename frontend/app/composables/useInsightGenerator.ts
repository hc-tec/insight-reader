/**
 * 洞察生成 Composable
 */
import type { InsightRequest, Intent } from '~/types/insight'

export const useInsightGenerator = () => {
  const isGenerating = useState<boolean>('is-generating', () => false)
  const currentInsight = useState<string>('current-insight', () => '')
  const currentReasoning = useState<string>('current-reasoning', () => '')
  const error = useState<string | null>('insight-error', () => null)
  const { addHistoryItem } = useHistory()
  const { title, content } = useArticle()
  const { selectedStart, selectedEnd } = useSelection()
  const { user } = useAuth()
  const currentArticleId = useState<number | null>('current-article-id', () => null)
  const config = useRuntimeConfig()

  const generate = async (request: InsightRequest) => {
    isGenerating.value = true
    currentInsight.value = ''
    currentReasoning.value = ''
    error.value = null

    try {
      const { connect } = useSSE()

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

              await $fetch(`${config.public.apiBase}/api/v1/insights/history`, {
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
                  reasoning: currentReasoning.value || null
                }
              })

              console.log('💾 洞察已保存到历史记录')
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

  return {
    isGenerating,
    currentInsight,
    currentReasoning,
    error,
    generate,
    clear
  }
}
