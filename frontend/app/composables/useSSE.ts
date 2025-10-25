/**
 * SSE 流式响应处理 Composable
 */
import type { InsightRequest, SSEEvent } from '~/types/insight'

interface SSECallbacks {
  onStart?: () => void
  onDelta?: (content: string) => void
  onReasoning?: (content: string) => void
  onComplete?: (metadata: any) => void
  onError?: (error: any) => void
}

export const useSSE = () => {
  const config = useRuntimeConfig()

  // 存储当前的 AbortController
  let currentAbortController: AbortController | null = null

  const connect = async (
    url: string,
    data: InsightRequest,
    callbacks: SSECallbacks
  ) => {
    const fullUrl = `${config.public.apiBase}${url}`

    // 创建新的 AbortController
    currentAbortController = new AbortController()
    const signal = currentAbortController.signal

    try {
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        signal  // 传递 signal
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('无法读取响应流')
      }

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonStr = line.substring(6)
              try {
                const event = JSON.parse(jsonStr) as SSEEvent

                switch (event.type) {
                  case 'start':
                    callbacks.onStart?.()
                    break
                  case 'delta':
                    if (event.content) {
                      callbacks.onDelta?.(event.content)
                    }
                    break
                  case 'reasoning':
                    if (event.content) {
                      callbacks.onReasoning?.(event.content)
                    }
                    break
                  case 'complete':
                    callbacks.onComplete?.(event.metadata)
                    break
                  case 'error':
                    callbacks.onError?.(event)
                    break
                }
              } catch (e) {
                console.error('解析 SSE 事件失败', e)
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
        currentAbortController = null
      }
    } catch (error) {
      // 如果是用户主动取消，不当作错误
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('⏹️ 用户停止了生成')
        return
      }

      callbacks.onError?.({ message: error instanceof Error ? error.message : '未知错误' })
      throw error
    }
  }

  // 停止当前连接
  const abort = () => {
    if (currentAbortController) {
      console.log('⏹️ 停止 SSE 连接')
      currentAbortController.abort()
      currentAbortController = null
    }
  }

  return {
    connect,
    abort
  }
}
