/**
 * 分析通知监听 Composable（带自动重连）
 * 使用 SSE (Server-Sent Events) 接收实时任务状态更新
 * 支持: 文章分析、元视角分析、思维透镜等
 *
 * 特性：
 * - 自动重连（指数退避）
 * - 连接状态监控
 * - 心跳检测
 */

export const useAnalysisNotifications = () => {
  const { user, token } = useAuth()
  const config = useRuntimeConfig()

  // SSE 连接实例
  let eventSource: EventSource | null = null

  // 重连控制
  let reconnectTimer: NodeJS.Timeout | null = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 10
  const baseReconnectDelay = 1000 // 1秒
  const maxReconnectDelay = 30000 // 30秒

  // 心跳检测
  let lastHeartbeat = Date.now()
  let heartbeatTimer: NodeJS.Timeout | null = null
  const heartbeatTimeout = 45000 // 45秒无心跳则认为连接断开

  // 连接状态
  const connectionState = useState('sse-connection-state', () => 'disconnected')
  const isManuallyDisconnected = ref(false)

  // 回调函数存储
  const analysisCallbacks = new Map<number, (articleId: number) => void>()
  const metaAnalysisCallbacks: Array<(articleId: number, metaAnalysis: any) => void> = []
  const lensCallbacks: Array<(lensType: string, lensResult: any) => void> = []
  const buttonGenerationCallbacks: Array<(buttons: any[]) => void> = []
  const taskFailedCallbacks: Array<(taskType: string, error: string) => void> = []

  /**
   * 清理重连定时器
   */
  const clearReconnectTimer = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  /**
   * 清理心跳定时器
   */
  const clearHeartbeatTimer = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  /**
   * 启动心跳检测
   */
  const startHeartbeatCheck = () => {
    clearHeartbeatTimer()
    lastHeartbeat = Date.now()

    heartbeatTimer = setInterval(() => {
      const timeSinceLastHeartbeat = Date.now() - lastHeartbeat

      if (timeSinceLastHeartbeat > heartbeatTimeout) {
        console.warn('[SSE] 心跳超时，连接可能已断开，尝试重连')
        // 使用内部断开（不标记为手动断开）
        _internalDisconnect()
        connectionState.value = 'disconnected'
        scheduleReconnect()
      }
    }, 10000) // 每10秒检查一次
  }

  /**
   * 计算重连延迟（指数退避）
   */
  const getReconnectDelay = () => {
    const delay = Math.min(
      baseReconnectDelay * Math.pow(2, reconnectAttempts),
      maxReconnectDelay
    )
    return delay + Math.random() * 1000 // 添加随机抖动
  }

  /**
   * 安排重连
   */
  const scheduleReconnect = () => {
    if (isManuallyDisconnected.value) {
      console.log('[SSE] 手动断开连接，不重连')
      return
    }

    if (reconnectAttempts >= maxReconnectAttempts) {
      console.error('[SSE] 达到最大重连次数，停止重连')
      connectionState.value = 'failed'
      return
    }

    clearReconnectTimer()

    const delay = getReconnectDelay()
    console.log(`[SSE] 安排重连（第 ${reconnectAttempts + 1}/${maxReconnectAttempts} 次），延迟 ${Math.round(delay)}ms`)

    connectionState.value = 'reconnecting'

    reconnectTimer = setTimeout(() => {
      reconnectAttempts++
      connect()
    }, delay)
  }

  /**
   * 建立 SSE 连接（带自动重连）
   */
  const connect = () => {
    if (!user.value || !token.value) {
      console.warn('[SSE] 用户未登录或 token 缺失')
      return
    }

    if (eventSource && eventSource.readyState !== EventSource.CLOSED) {
      console.log('[SSE] 连接已存在')
      return
    }

    const sseUrl = `${config.public.apiBase}/api/v1/sse/analysis-notifications?token=${token.value}`

    console.log('[SSE] 正在连接:', reconnectAttempts > 0 ? `(第 ${reconnectAttempts} 次重连)` : '(首次连接)')

    try {
      eventSource = new EventSource(sseUrl)
      connectionState.value = 'connecting'

      // 监听打开事件
      eventSource.onopen = () => {
        console.log('[SSE] 连接已建立')
        connectionState.value = 'connected'
        reconnectAttempts = 0 // 重置重连计数
        clearReconnectTimer()
        startHeartbeatCheck() // 启动心跳检测
      }

      // 监听连接成功事件
      eventSource.addEventListener('connected', (e) => {
        const data = JSON.parse(e.data)
        console.log('[SSE] 收到连接确认，用户ID:', data.user_id)
        lastHeartbeat = Date.now()
      })

    // 监听任务开始事件
    eventSource.addEventListener('task_started', (e) => {
      const data = JSON.parse(e.data)
      console.log('[SSE] 任务开始:', data.task_type, data.task_id)
    })

    // 监听任务完成事件（新格式）
    eventSource.addEventListener('task_completed', async (e) => {
      const data = JSON.parse(e.data)
      console.log('[SSE] 任务完成:', data.task_type, data.task_id)

      // 文章分析完成
      if (data.task_type === 'article_analysis' || data.task_type === 'article_reanalysis') {
        const articleId = data.result.article_id

        // 触发回调
        const callback = analysisCallbacks.get(articleId)
        if (callback) {
          await callback(articleId)
        }

        // 全局处理
        await handleAnalysisComplete(articleId)
      }

      // 元视角分析完成
      else if (data.task_type === 'meta_analysis') {
        for (const callback of metaAnalysisCallbacks) {
          await callback(data.result.article_id, data.result.meta_analysis)
        }
      }

      // 思维透镜完成
      else if (data.task_type.startsWith('thinking_lens_')) {
        const lensType = data.task_type.replace('thinking_lens_', '')
        for (const callback of lensCallbacks) {
          await callback(lensType, data.result.lens_result)
        }
      }

      // 按钮生成完成
      else if (data.task_type === 'button_generation') {
        for (const callback of buttonGenerationCallbacks) {
          await callback(data.result.buttons)
        }
      }
    })

    // 监听任务失败事件
    eventSource.addEventListener('task_failed', (e) => {
      const data = JSON.parse(e.data)
      console.error('[SSE] 任务失败:', data.task_type, data.error)

      for (const callback of taskFailedCallbacks) {
        callback(data.task_type, data.error)
      }

      // 显示错误提示
      showToast({
        message: `分析失败: ${data.error}`,
        type: 'error'
      })
    })

      // 监听心跳（保持连接）
      eventSource.addEventListener('heartbeat', (e) => {
        lastHeartbeat = Date.now()
        // console.log('[SSE] 收到心跳')
      })

      // 错误处理（带自动重连）
      eventSource.onerror = (error) => {
        console.error('[SSE] 连接错误:', error)

        // 检查连接状态
        if (eventSource?.readyState === EventSource.CONNECTING) {
          console.log('[SSE] 正在尝试重连...')
          connectionState.value = 'reconnecting'
        } else if (eventSource?.readyState === EventSource.CLOSED) {
          console.warn('[SSE] 连接已关闭，尝试重连')
          // 使用内部断开（不标记为手动断开）
          _internalDisconnect()
          connectionState.value = 'disconnected'
          // 安排重连
          scheduleReconnect()
        }
      }

    } catch (error) {
      console.error('[SSE] 创建连接失败:', error)
      connectionState.value = 'failed'
      scheduleReconnect()
    }
  }

  /**
   * 内部断开连接（不标记为手动断开）
   */
  const _internalDisconnect = () => {
    // 清理心跳定时器
    clearHeartbeatTimer()

    // 关闭连接
    if (eventSource) {
      eventSource.close()
      eventSource = null
      console.log('[SSE] 连接已关闭')
    }
  }

  /**
   * 断开 SSE 连接（手动）
   */
  const disconnect = () => {
    // 标记为手动断开（防止自动重连）
    isManuallyDisconnected.value = true

    // 清理所有定时器
    clearReconnectTimer()
    clearHeartbeatTimer()

    // 关闭连接
    if (eventSource) {
      eventSource.close()
      eventSource = null
      console.log('[SSE] 连接已断开')
    }

    // 更新状态
    connectionState.value = 'disconnected'
    reconnectAttempts = 0
  }

  /**
   * 注册文章分析完成回调
   */
  const onAnalysisComplete = (
    articleId: number,
    callback: (articleId: number) => void | Promise<void>
  ) => {
    analysisCallbacks.set(articleId, callback)
  }

  /**
   * 注册元视角分析完成回调
   */
  const onMetaAnalysisComplete = (
    callback: (articleId: number, metaAnalysis: any) => void | Promise<void>
  ) => {
    metaAnalysisCallbacks.push(callback)
  }

  /**
   * 注册思维透镜完成回调
   */
  const onLensComplete = (
    callback: (lensType: string, lensResult: any) => void | Promise<void>
  ) => {
    lensCallbacks.push(callback)
  }

  /**
   * 注册按钮生成完成回调
   */
  const onButtonGenerationComplete = (
    callback: (buttons: any[]) => void
  ) => {
    buttonGenerationCallbacks.push(callback)
  }

  /**
   * 注册任务失败回调
   */
  const onTaskFailed = (
    callback: (taskType: string, error: string) => void
  ) => {
    taskFailedCallbacks.push(callback)
  }

  /**
   * 处理分析完成事件（仅通知，不渲染）
   */
  const handleAnalysisComplete = async (articleId: number) => {
    console.log('📄 分析完成事件触发，文章 ID:', articleId)
    // 注意：不在这里调用 renderSparks，由各页面的回调处理
    // 避免与页面中注册的 onAnalysisComplete 回调重复渲染
  }

  // 自动连接和断开
  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  /**
   * 手动重新连接（重置手动断开标志）
   */
  const reconnect = () => {
    isManuallyDisconnected.value = false
    reconnectAttempts = 0
    connect()
  }

  return {
    // 连接控制
    connect,
    disconnect,
    reconnect,
    // 连接状态
    connectionState: readonly(connectionState),
    isManuallyDisconnected: readonly(isManuallyDisconnected),
    // 回调注册
    onAnalysisComplete,
    onMetaAnalysisComplete,
    onLensComplete,
    onButtonGenerationComplete,
    onTaskFailed
  }
}
