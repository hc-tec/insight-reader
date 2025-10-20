/**
 * 分析通知监听 Composable
 * 使用 SSE (Server-Sent Events) 接收实时分析状态更新
 */

export const useAnalysisNotifications = () => {
  const { user } = useAuth()
  const config = useRuntimeConfig()

  // SSE 连接实例
  let eventSource: EventSource | null = null

  // 分析完成回调函数映射
  const completionCallbacks = new Map<number, (articleId: number) => void>()

  // 进度更新回调函数映射
  const progressCallbacks = new Map<number, (data: any) => void>()

  /**
   * 建立 SSE 连接
   */
  const connect = () => {
    if (!user.value || eventSource) return

    const sseUrl = `${config.public.apiBase}/api/v1/sse/analysis-notifications?user_id=${user.value.id}`

    console.log('🔌 正在连接 SSE:', sseUrl)

    eventSource = new EventSource(sseUrl)

    // 监听连接成功事件
    eventSource.addEventListener('connected', (e) => {
      const data = JSON.parse(e.data)
      console.log('✅ SSE 已连接:', data)
    })

    // 监听分析完成事件
    eventSource.addEventListener('analysis_complete', (e) => {
      const data = JSON.parse(e.data)
      const articleId = data.article_id

      console.log('📬 收到分析完成通知:', articleId)

      // 触发回调
      const callback = completionCallbacks.get(articleId)
      if (callback) {
        callback(articleId)
      }

      // 全局通知
      handleAnalysisComplete(articleId)
    })

    // 监听分析进度事件
    eventSource.addEventListener('analysis_progress', (e) => {
      const data = JSON.parse(e.data)
      const articleId = data.article_id

      console.log(`📊 分析进度更新: ${data.stage} - ${data.progress}%`)

      // 触发回调
      const callback = progressCallbacks.get(articleId)
      if (callback) {
        callback(data)
      }
    })

    // 监听心跳（保持连接）
    eventSource.addEventListener('heartbeat', (e) => {
      console.log('💓 SSE 心跳')
    })

    // 错误处理
    eventSource.onerror = (error) => {
      console.error('❌ SSE 连接错误:', error)
      // EventSource 会自动重连
    }
  }

  /**
   * 断开 SSE 连接
   */
  const disconnect = () => {
    if (eventSource) {
      eventSource.close()
      eventSource = null
      console.log('🔌 SSE 已断开')
    }
  }

  /**
   * 注册分析完成回调
   *
   * @param articleId - 文章 ID
   * @param callback - 完成时调用的回调函数
   */
  const onAnalysisComplete = (
    articleId: number,
    callback: (articleId: number) => void
  ) => {
    completionCallbacks.set(articleId, callback)
  }

  /**
   * 注册进度更新回调
   *
   * @param articleId - 文章 ID
   * @param callback - 进度更新时调用的回调函数
   */
  const onAnalysisProgress = (
    articleId: number,
    callback: (data: any) => void
  ) => {
    progressCallbacks.set(articleId, callback)
  }

  /**
   * 处理分析完成事件
   */
  const handleAnalysisComplete = async (articleId: number) => {
    try {
      // 获取分析报告
      const report = await $fetch(`${config.public.apiBase}/api/v1/articles/${articleId}/analysis-report`)

      console.log('📄 分析报告已获取:', report)

      // 触发火花渲染
      const { renderSparks } = useSparkRenderer()
      await renderSparks(report.report_data)

      // 显示成功通知
      const sparkCount = (report.report_data.concept_sparks?.length || 0) +
                        (report.report_data.argument_sparks?.length || 0)

      showToast({
        message: `✨ 已为您发现 ${sparkCount} 个高价值洞察点`,
        type: 'success',
        duration: 5000
      })

    } catch (error) {
      console.error('❌ 获取分析报告失败:', error)
      showToast({
        message: '获取分析结果失败，请刷新页面重试',
        type: 'error'
      })
    }
  }

  /**
   * 简单的 Toast 通知
   */
  const showToast = (options: { message: string; type: string; duration?: number }) => {
    // 简单实现，实际项目中可使用 UI 库的 Toast 组件
    console.log(`[${options.type.toUpperCase()}] ${options.message}`)

    // 创建临时通知元素
    const toast = document.createElement('div')
    toast.className = `fixed bottom-40 right-8 px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in-up
      ${options.type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white`
    toast.textContent = options.message
    document.body.appendChild(toast)

    setTimeout(() => {
      toast.classList.add('animate-fade-out')
      setTimeout(() => toast.remove(), 300)
    }, options.duration || 3000)
  }

  // 自动连接和断开
  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    connect,
    disconnect,
    onAnalysisComplete,
    onAnalysisProgress
  }
}
