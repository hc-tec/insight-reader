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

    // 将用户问题添加到历史
    const userMessage: Message = {
      role: 'user',
      content: question,
      timestamp: Date.now()
    }
    conversationHistory.value.push(userMessage)

    try {
      const { connect } = useSSE()

      const request: FollowUpRequest = {
        selected_text: selectedText,
        initial_insight: initialInsight,
        conversation_history: conversationHistory.value.slice(0, -1), // 不包含刚添加的用户问题
        follow_up_question: question,
        use_reasoning: useReasoning
      }

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
        onComplete: (metadata) => {
          // 将 AI 回答添加到历史
          const assistantMessage: Message = {
            role: 'assistant',
            content: currentAnswer.value,
            timestamp: Date.now()
          }
          conversationHistory.value.push(assistantMessage)

          console.log('✅ 追问回答完成', {
            metadata,
            conversationLength: conversationHistory.value.length
          })

          isGeneratingAnswer.value = false
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
    undoLastQuestion
  }
}
