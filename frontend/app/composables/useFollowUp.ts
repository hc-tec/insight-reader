/**
 * 追问管理 Composable
 */
import type { Message, FollowUpButton, ButtonGenerationRequest, FollowUpRequest } from '~/types/followup'
import type { Intent } from '~/types/insight'

export const useFollowUp = () => {
  const config = useRuntimeConfig()

  // 状态管理
  const conversationHistory = useState<Message[]>('followup-conversation', () => [])
  const followUpButtons = useState<FollowUpButton[]>('followup-buttons', () => [])
  const isGeneratingButtons = useState<boolean>('followup-generating-buttons', () => false)
  const isGeneratingAnswer = useState<boolean>('followup-generating-answer', () => false)
  const currentAnswer = useState<string>('followup-current-answer', () => '')
  const currentReasoning = useState<string>('followup-current-reasoning', () => '')
  const error = useState<string | null>('followup-error', () => null)

  // 获取 SSE 实例（保持引用以便停止）
  const { connect, abort: abortSSE } = useSSE()

  // 生成追问按钮（异步版本）
  const generateButtons = async (
    selectedText: string,
    insight: string,
    intent: Intent
  ) => {
    isGeneratingButtons.value = true
    error.value = null

    // 默认按钮（立即显示）
    const defaultButtons: FollowUpButton[] = [
      {
        id: 'example_default',
        label: '举个例子',
        icon: '🌰',
        category: 'example'
      },
      {
        id: 'simplify_default',
        label: '说得简单点',
        icon: '🎯',
        category: 'simplify'
      },
      {
        id: 'extend_default',
        label: '深入了解',
        icon: '📚',
        category: 'extend'
      }
    ]

    try {
      const request: ButtonGenerationRequest = {
        selected_text: selectedText,
        insight,
        intent,
        conversation_history: conversationHistory.value
      }

      const response = await $fetch<{ status: string; buttons: FollowUpButton[] | null; task_id: string | null }>(
        `${config.public.apiBase}/api/v1/insights/generate-buttons`,
        {
          method: 'POST',
          body: request
        }
      )

      if (response.status === 'completed' && response.buttons) {
        // 立即返回结果（缓存或默认）
        followUpButtons.value = response.buttons
        isGeneratingButtons.value = false
        console.log('🎯 生成追问按钮（立即返回）:', response.buttons.length, '个')
      } else if (response.status === 'pending') {
        // 先显示默认按钮，等待 SSE 更新
        followUpButtons.value = defaultButtons
        console.log('🔄 按钮生成中，任务ID:', response.task_id)
        // 保持 isGeneratingButtons.value = true，等待 SSE 回调
      }

    } catch (err) {
      console.error('❌ 生成追问按钮失败:', err)
      error.value = err instanceof Error ? err.message : '生成追问按钮失败'

      // 使用默认按钮
      followUpButtons.value = defaultButtons
      isGeneratingButtons.value = false
    }
  }

  // 发送追问并获取回答
  const askFollowUp = async (
    selectedText: string,
    initialInsight: string,
    question: string,
    useReasoning: boolean = false
  ) => {
    isGeneratingAnswer.value = true
    currentAnswer.value = ''
    currentReasoning.value = ''
    error.value = null

    // 在函数开始时获取所有需要的状态（避免在回调中调用 composables）
    const { user } = useAuth()
    const { content } = useArticle()
    const { selectedStart, selectedEnd } = useSelection()
    const { currentInsightId } = useInsightGenerator()
    const currentArticleId = useState<number | null>('current-article-id', () => null)

    // 将用户问题添加到历史
    const userMessage: Message = {
      role: 'user',
      content: question,
      timestamp: Date.now()
    }
    conversationHistory.value.push(userMessage)

    // 构建完整的对话历史用于发送给后端
    // 注意：conversationHistory 只包含追问对话，不包含初始洞察
    // 所以我们需要构建一个临时的完整历史（包含初始洞察）用于发送
    const fullHistoryForBackend: Message[] = []

    // 如果 conversationHistory 为空或第一条不是 assistant，说明这是第一次追问
    // 需要在发送给后端时包含初始洞察
    if (conversationHistory.value.length === 1 ||
        (conversationHistory.value.length > 1 && conversationHistory.value[0]?.role !== 'assistant')) {
      // 添加初始洞察作为第一条消息（不包含在 conversationHistory 中，只是发送给后端）
      const { currentInsightId, currentInsight, currentReasoning } = useInsightGenerator()
      fullHistoryForBackend.push({
        role: 'assistant',
        content: initialInsight,
        reasoning: currentReasoning.value || undefined,
        timestamp: Date.now(),
        insight_id: currentInsightId.value || null
      })
    }

    // 添加所有追问对话（不包含刚添加的用户问题）
    fullHistoryForBackend.push(...conversationHistory.value.slice(0, -1))

    console.log('📝 对话历史状态:', {
      conversationHistoryLength: conversationHistory.value.length,
      fullHistoryForBackendLength: fullHistoryForBackend.length,
      conversationHistory: conversationHistory.value.map(m => ({ role: m.role, content: m.content.substring(0, 30) })),
      fullHistoryForBackend: fullHistoryForBackend.map(m => ({ role: m.role, content: m.content.substring(0, 30) }))
    })

    try {
      const request: FollowUpRequest = {
        selected_text: selectedText,
        initial_insight: initialInsight,
        conversation_history: fullHistoryForBackend, // 使用完整历史（包含初始洞察）
        follow_up_question: question,
        use_reasoning: useReasoning
      }

      console.log('📤 发送追问请求:', {
        selected_text: request.selected_text.substring(0, 30),
        conversation_history_length: request.conversation_history.length,
        follow_up_question: request.follow_up_question
      })

      await connect('/api/v1/insights/follow-up', request, {
        onStart: () => {
          console.log('🚀 开始生成追问回答')
        },
        onDelta: (content: string) => {
          currentAnswer.value += content
        },
        onReasoning: (content: string) => {
          currentReasoning.value += content
        },
        onComplete: async (metadata) => {
          // 将 AI 回答添加到历史
          const assistantMessage: Message = {
            role: 'assistant',
            content: currentAnswer.value,
            reasoning: currentReasoning.value || undefined,
            timestamp: Date.now(),
            insight_id: null  // 初始时没有 ID，保存后会更新
          }
          conversationHistory.value.push(assistantMessage)

          console.log('✅ 追问回答完成', {
            metadata,
            conversationLength: conversationHistory.value.length
          })

          // 立即停止生成状态，避免光标继续闪烁
          isGeneratingAnswer.value = false

          // 保存追问到后端数据库（如果用户已登录且有文章ID）
          if (currentAnswer.value && user.value?.id && currentArticleId.value) {
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

              // 找到对话历史中最后一条有 insight_id 的 assistant 消息作为 parent_id
              let parentId = currentInsightId.value  // 默认使用原始洞察ID
              const assistantMessages = conversationHistory.value.filter(m => m.role === 'assistant' && m.insight_id)
              if (assistantMessages.length > 0) {
                // parent_id 是最后一条已保存的 assistant 消息的 ID
                parentId = assistantMessages[assistantMessages.length - 1].insight_id
              }

              const response = await $fetch<{ status: string; insight_history_id: number }>(`${config.public.apiBase}/api/v1/insights/history`, {
                method: 'POST',
                body: {
                  article_id: currentArticleId.value,
                  selected_text: selectedText,
                  selected_start: selectedStart.value,
                  selected_end: selectedEnd.value,
                  context_before: contextBefore,
                  context_after: contextAfter,
                  intent: 'follow_up',
                  question: question,
                  insight: currentAnswer.value,
                  reasoning: currentReasoning.value || null,
                  parent_id: parentId  // 使用正确的父洞察 ID
                }
              })

              console.log('💾 追问已保存到历史记录，ID:', response.insight_history_id, '父洞察ID:', parentId)

              // 更新当前 assistant 消息的 insight_id
              assistantMessage.insight_id = response.insight_history_id
            } catch (err) {
              console.error('❌ 保存追问历史失败:', err)
              // 不影响用户体验，只记录错误
            }
          }
        },
        onError: (err) => {
          error.value = err.message || '生成回答失败'
          isGeneratingAnswer.value = false
          // 移除刚添加的用户问题（因为失败了）
          conversationHistory.value.pop()
        }
      })
    } catch (err) {
      error.value = err instanceof Error ? err.message : '网络错误，请重试'
      isGeneratingAnswer.value = false
      conversationHistory.value.pop()
    }
  }

  // 清空对话历史
  const clearConversation = () => {
    conversationHistory.value = []
    followUpButtons.value = []
    currentAnswer.value = ''
    currentReasoning.value = ''
    error.value = null
  }

  // 移除最后一轮对话（撤销）
  const undoLastQuestion = () => {
    if (conversationHistory.value.length >= 2) {
      // 移除最后的用户问题和 AI 回答
      conversationHistory.value.splice(-2, 2)
    }
  }

  // 停止生成追问回答
  const stopFollowUp = () => {
    abortSSE()
    isGeneratingAnswer.value = false
    console.log('⏹️ 停止追问生成')
  }

  return {
    // 状态（暴露为可写，以便 SSE 回调更新）
    conversationHistory,
    followUpButtons,
    isGeneratingButtons,
    isGeneratingAnswer,
    currentAnswer,
    currentReasoning,
    error,

    // 方法
    generateButtons,
    askFollowUp,
    clearConversation,
    undoLastQuestion,
    stopFollowUp  // 导出停止方法
  }
}
