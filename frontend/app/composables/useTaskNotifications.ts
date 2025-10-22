/**
 * 任务通知 SSE Composable
 * 用于接收后台任务状态更新（文章分析、元视角分析、思维透镜等）
 */

interface TaskCallbacks {
  // 文章分析完成
  onAnalysisComplete?: (articleId: number, reportData: any) => void | Promise<void>

  // 元视角分析完成
  onMetaAnalysisComplete?: (articleId: number, metaAnalysis: any) => void | Promise<void>

  // 透镜分析完成
  onLensComplete?: (lensType: string, lensResult: any) => void | Promise<void>

  // 任务失败
  onTaskFailed?: (taskType: string, error: string) => void | Promise<void>

  // 任务开始
  onTaskStarted?: (taskId: string, taskType: string) => void | Promise<void>
}

export const useTaskNotifications = () => {
  const config = useRuntimeConfig()
  let eventSource: EventSource | null = null
  let callbacks: TaskCallbacks = {}

  /**
   * 建立 SSE 连接
   */
  const connect = (userId: number, taskCallbacks: TaskCallbacks) => {
    if (eventSource) {
      console.log('[SSE] 连接已存在，先关闭旧连接')
      disconnect()
    }

    callbacks = taskCallbacks
    const url = `${config.public.apiBase}/api/v1/sse/analysis-notifications?user_id=${userId}`

    console.log('[SSE] 建立连接:', url)
    eventSource = new EventSource(url)

    // 连接建立
    eventSource.addEventListener('connected', (event: MessageEvent) => {
      const data = JSON.parse(event.data)
      console.log('[SSE] 连接成功，用户ID:', data.user_id)
    })

    // 心跳
    eventSource.addEventListener('heartbeat', (event: MessageEvent) => {
      // console.log('[SSE] 心跳')
    })

    // 任务开始
    eventSource.addEventListener('task_started', async (event: MessageEvent) => {
      const data = JSON.parse(event.data)
      console.log('[SSE] 任务开始:', data.task_type, data.task_id)

      if (callbacks.onTaskStarted) {
        await callbacks.onTaskStarted(data.task_id, data.task_type)
      }
    })

    // 任务完成
    eventSource.addEventListener('task_completed', async (event: MessageEvent) => {
      const data = JSON.parse(event.data)
      console.log('[SSE] 任务完成:', data.task_type, data.task_id)

      // 文章分析完成
      if (data.task_type === 'article_analysis' || data.task_type === 'article_reanalysis') {
        if (callbacks.onAnalysisComplete) {
          await callbacks.onAnalysisComplete(
            data.result.article_id,
            data.result.report_data
          )
        }
      }

      // 元视角分析完成
      else if (data.task_type === 'meta_analysis') {
        if (callbacks.onMetaAnalysisComplete) {
          await callbacks.onMetaAnalysisComplete(
            data.result.article_id,
            data.result.meta_analysis
          )
        }
      }

      // 思维透镜完成
      else if (data.task_type.startsWith('thinking_lens_')) {
        const lensType = data.task_type.replace('thinking_lens_', '')
        if (callbacks.onLensComplete) {
          await callbacks.onLensComplete(lensType, data.result.lens_result)
        }
      }
    })

    // 任务失败
    eventSource.addEventListener('task_failed', async (event: MessageEvent) => {
      const data = JSON.parse(event.data)
      console.error('[SSE] 任务失败:', data.task_type, data.error)

      if (callbacks.onTaskFailed) {
        await callbacks.onTaskFailed(data.task_type, data.error)
      }
    })

    // 错误处理
    eventSource.onerror = (error) => {
      console.error('[SSE] 连接错误:', error)
      // 浏览器会自动重连
    }

    return eventSource
  }

  /**
   * 断开 SSE 连接
   */
  const disconnect = () => {
    if (eventSource) {
      console.log('[SSE] 关闭连接')
      eventSource.close()
      eventSource = null
    }
  }

  /**
   * 检查连接状态
   */
  const isConnected = () => {
    return eventSource !== null && eventSource.readyState === EventSource.OPEN
  }

  return {
    connect,
    disconnect,
    isConnected
  }
}
