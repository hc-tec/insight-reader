/**
 * 任务进度跟踪 Composable
 * 使用 SSE (Server-Sent Events) 订阅后台任务进度
 */

import { ref, onUnmounted } from 'vue'

export interface TaskEvent {
  type: string
  data: any
  timestamp: string
}

export interface TaskProgress {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  result?: any
  error?: string
}

export interface TaskCallbacks {
  onProgress?: (progress: TaskProgress) => void
  onComplete?: (result: any) => void
  onError?: (error: string) => void
}

export function useTaskProgress() {
  const eventSource = ref<EventSource | null>(null)
  const progress = ref<TaskProgress>({
    status: 'pending',
    progress: 0,
    message: ''
  })

  const isSubscribed = ref(false)

  /**
   * 订阅任务进度（SSE）
   *
   * @param taskId - 任务 ID
   * @param callbacks - 回调函数
   */
  const subscribe = (taskId: string, callbacks?: TaskCallbacks) => {
    // 如果已有连接，先关闭
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }

    // 创建 SSE 连接
    const apiBase = useRuntimeConfig().public.apiBase || ''
    const url = `${apiBase}/api/v1/tasks/${taskId}/events`

    console.log('[TaskProgress] Subscribing to:', url)

    eventSource.value = new EventSource(url)
    isSubscribed.value = true

    // 监听 task_created 事件
    eventSource.value.addEventListener('task_created', (e: MessageEvent) => {
      try {
        const event: TaskEvent = JSON.parse(e.data)
        console.log('[TaskProgress] Task created:', event)

        progress.value = {
          status: 'pending',
          progress: 0,
          message: '任务已创建'
        }

        callbacks?.onProgress?.(progress.value)
      } catch (error) {
        console.error('[TaskProgress] Failed to parse task_created event:', error)
      }
    })

    // 监听 task_started 事件
    eventSource.value.addEventListener('task_started', (e: MessageEvent) => {
      try {
        const event: TaskEvent = JSON.parse(e.data)
        console.log('[TaskProgress] Task started:', event)

        progress.value = {
          status: 'processing',
          progress: 10,
          message: '分析开始...'
        }

        callbacks?.onProgress?.(progress.value)
      } catch (error) {
        console.error('[TaskProgress] Failed to parse task_started event:', error)
      }
    })

    // 监听 progress_update 事件
    eventSource.value.addEventListener('progress_update', (e: MessageEvent) => {
      try {
        const event: TaskEvent = JSON.parse(e.data)
        console.log('[TaskProgress] Progress update:', event)

        progress.value = {
          status: 'processing',
          progress: event.data.progress || 50,
          message: event.data.message || '处理中...'
        }

        callbacks?.onProgress?.(progress.value)
      } catch (error) {
        console.error('[TaskProgress] Failed to parse progress_update event:', error)
      }
    })

    // 监听 task_completed 事件
    eventSource.value.addEventListener('task_completed', (e: MessageEvent) => {
      try {
        const event: TaskEvent = JSON.parse(e.data)
        console.log('[TaskProgress] Task completed:', event)

        progress.value = {
          status: 'completed',
          progress: 100,
          message: '分析完成',
          result: event.data.result
        }

        callbacks?.onProgress?.(progress.value)
        callbacks?.onComplete?.(event.data.result)

        // 关闭连接
        cleanup()
      } catch (error) {
        console.error('[TaskProgress] Failed to parse task_completed event:', error)
      }
    })

    // 监听 task_failed 事件
    eventSource.value.addEventListener('task_failed', (e: MessageEvent) => {
      try {
        const event: TaskEvent = JSON.parse(e.data)
        console.error('[TaskProgress] Task failed:', event)

        const errorMsg = event.data.error || '未知错误'

        progress.value = {
          status: 'failed',
          progress: 0,
          message: '分析失败',
          error: errorMsg
        }

        callbacks?.onProgress?.(progress.value)
        callbacks?.onError?.(errorMsg)

        // 关闭连接
        cleanup()
      } catch (error) {
        console.error('[TaskProgress] Failed to parse task_failed event:', error)
      }
    })

    // 监听错误事件
    eventSource.value.onerror = (error) => {
      console.error('[TaskProgress] SSE connection error:', error)

      // 只有在连接已建立后才报错（避免初始连接的误报）
      if (eventSource.value?.readyState === EventSource.CLOSED) {
        const errorMsg = 'SSE 连接失败'

        progress.value = {
          status: 'failed',
          progress: 0,
          message: errorMsg,
          error: errorMsg
        }

        callbacks?.onProgress?.(progress.value)
        callbacks?.onError?.(errorMsg)

        cleanup()
      }
    }

    // 监听 open 事件
    eventSource.value.addEventListener('open', () => {
      console.log('[TaskProgress] SSE connection opened')
    })
  }

  /**
   * 取消任务
   *
   * @param taskId - 任务 ID
   */
  const cancel = async (taskId: string) => {
    try {
      const apiBase = useRuntimeConfig().public.apiBase || ''
      await $fetch(`${apiBase}/api/v1/tasks/${taskId}/cancel`, {
        method: 'POST'
      })

      console.log('[TaskProgress] Task cancelled:', taskId)

      progress.value = {
        status: 'failed',
        progress: 0,
        message: '任务已取消',
        error: '用户取消'
      }

      cleanup()
    } catch (error) {
      console.error('[TaskProgress] Failed to cancel task:', error)
      throw error
    }
  }

  /**
   * 查询任务状态（不使用 SSE）
   *
   * @param taskId - 任务 ID
   */
  const getStatus = async (taskId: string): Promise<TaskProgress> => {
    try {
      const apiBase = useRuntimeConfig().public.apiBase || ''
      const response = await $fetch<any>(`${apiBase}/api/v1/tasks/${taskId}/status`)

      return {
        status: response.status,
        progress: response.progress,
        message: response.message,
        result: response.result,
        error: response.error
      }
    } catch (error) {
      console.error('[TaskProgress] Failed to get task status:', error)
      throw error
    }
  }

  /**
   * 清理资源
   */
  const cleanup = () => {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
      isSubscribed.value = false
      console.log('[TaskProgress] Cleaned up SSE connection')
    }
  }

  // 组件卸载时自动清理
  onUnmounted(() => {
    cleanup()
  })

  return {
    progress,
    isSubscribed,
    subscribe,
    cancel,
    getStatus,
    cleanup
  }
}
