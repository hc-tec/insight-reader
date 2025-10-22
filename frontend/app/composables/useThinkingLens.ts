/**
 * 思维透镜 Composable
 * 负责思维透镜的状态管理、高亮渲染和API调用
 */

export interface Highlight {
  start: number
  end: number
  text: string
  category: string  // 'claim' | 'evidence' | 'subjective' | 'objective' | 'irony'
  color: string
  tooltip: string
}

export interface LensAnnotations {
  summary: string
  key_insights: string[]
  statistics: Record<string, any>
}

export interface LensResult {
  id: number
  meta_analysis_id: number
  lens_type: 'argument_structure' | 'author_stance'
  highlights: Highlight[]
  annotations: LensAnnotations
  created_at: string
}

export type LensType = 'argument_structure' | 'author_stance'

export const useThinkingLens = () => {
  const config = useRuntimeConfig()

  // 状态 - 支持同时启用多个透镜
  const enabledLenses = useState<Set<LensType>>('enabled-lenses', () => new Set())
  const lensResults = useState<Map<LensType, LensResult>>('lens-results', () => new Map())
  const loadingLenses = useState<Set<LensType>>('loading-lenses', () => new Set())
  const lensError = useState<string | null>('lens-error', () => null)

  /**
   * 通过文章ID加载透镜分析（异步版本）
   */
  const loadLens = async (
    articleId: number,
    lensType: LensType,
    forceReanalyze: boolean = false
  ) => {
    // 添加加载状态 - 创建新Set触发响应式
    const newLoadingSet = new Set(loadingLenses.value)
    newLoadingSet.add(lensType)
    loadingLenses.value = newLoadingSet
    lensError.value = null

    try {
      const response = await $fetch<{
        status: string
        lens_result: LensResult | null
        task_id: string | null
      }>(
        `${config.public.apiBase}/api/v1/articles/${articleId}/thinking-lens/${lensType}`,
        {
          params: { force_reanalyze: forceReanalyze }
        }
      )

      if (response.status === 'completed') {
        // 立即返回结果（来自缓存）
        lensResults.value.set(lensType, response.lens_result!)

        // 移除加载状态 - 创建新Set触发响应式
        const updatedLoadingSet = new Set(loadingLenses.value)
        updatedLoadingSet.delete(lensType)
        loadingLenses.value = updatedLoadingSet

        console.log(`✅ ${lensType} 透镜加载成功（来自缓存）:`, response.lens_result!.highlights.length, '个高亮')
        return response.lens_result

      } else if (response.status === 'pending') {
        // 异步任务已提交，等待SSE通知
        console.log(`🔄 ${lensType} 透镜分析已提交，任务ID: ${response.task_id}`)
        // 保持 loading 状态，等待 SSE 回调完成后再删除
        // SSE回调会自动处理结果并更新 lensResults
        return null
      }

    } catch (error: any) {
      console.error('❌ 透镜加载失败:', error)
      lensError.value = error.data?.detail || error.message || '透镜加载失败'

      // 移除加载状态 - 创建新Set触发响应式
      const errorLoadingSet = new Set(loadingLenses.value)
      errorLoadingSet.delete(lensType)
      loadingLenses.value = errorLoadingSet

      throw error
    }
  }

  /**
   * 切换透镜 - 支持同时启用多个透镜（异步版本）
   */
  const toggleLens = async (articleId: number, lensType: LensType, containerEl: HTMLElement) => {
    if (enabledLenses.value.has(lensType)) {
      // 关闭透镜
      removeHighlightsByType(containerEl, lensType)
      enabledLenses.value.delete(lensType)
      console.log(`🔴 ${lensType} 透镜已关闭`)
    } else {
      // 开启透镜
      // 先标记为已启用（这样SSE回调才会应用高亮）
      enabledLenses.value.add(lensType)

      // 检查是否已有数据，没有则加载
      if (!lensResults.value.has(lensType)) {
        const lensData = await loadLens(articleId, lensType)

        if (lensData) {
          // 立即返回结果（来自缓存），应用高亮
          renderHighlightsByType(containerEl, lensData.highlights, lensType)
          console.log(`🟢 ${lensType} 透镜已开启（来自缓存）`)
        } else {
          // pending状态，等待SSE回调
          console.log(`🔄 ${lensType} 透镜分析中，完成后将自动应用高亮`)
        }
      } else {
        // 已有数据，直接应用
        const lensData = lensResults.value.get(lensType)
        if (lensData) {
          renderHighlightsByType(containerEl, lensData.highlights, lensType)
          console.log(`🟢 ${lensType} 透镜已开启`)
        }
      }
    }
  }

  /**
   * 关闭所有透镜
   */
  const clearLens = (containerEl: HTMLElement) => {
    removeHighlights(containerEl)
    enabledLenses.value.clear()
  }

  /**
   * 渲染高亮到DOM（使用批量优化算法）
   */
  const renderHighlights = (containerEl: HTMLElement, highlights: Highlight[]) => {
    if (!containerEl || highlights.length === 0) {
      console.warn('⚠️ 无法渲染高亮：容器不存在或无高亮数据')
      return
    }

    try {
      // 清除旧的高亮
      removeHighlights(containerEl)

      console.log('🔍 开始渲染', highlights.length, '个高亮')
      const startTime = performance.now()

      // 使用批量渲染优化
      renderHighlightsBatch(containerEl, highlights)

      const elapsed = performance.now() - startTime
      console.log(`✅ 高亮渲染完成，耗时: ${elapsed.toFixed(0)}ms`)

    } catch (error) {
      console.error('❌ 高亮渲染失败:', error)
    }
  }

  /**
   * 按类型渲染高亮（支持多透镜同时显示，批量优化版本）
   */
  const renderHighlightsByType = (containerEl: HTMLElement, highlights: Highlight[], lensType: LensType) => {
    if (!containerEl || highlights.length === 0) {
      console.warn('⚠️ 无法渲染高亮：容器不存在或无高亮数据')
      return
    }

    try {
      console.log(`🔍 开始渲染 ${lensType}:`, highlights.length, '个高亮')
      const startTime = performance.now()

      // 批量渲染：只遍历DOM一次
      renderHighlightsBatch(containerEl, highlights, lensType)

      const elapsed = performance.now() - startTime
      console.log(`✅ ${lensType} 高亮渲染完成，耗时: ${elapsed.toFixed(0)}ms`)

    } catch (error) {
      console.error('❌ 高亮渲染失败:', error)
    }
  }

  /**
   * 批量渲染高亮（性能优化：只遍历DOM一次）
   */
  const renderHighlightsBatch = (containerEl: HTMLElement, highlights: Highlight[], lensType?: LensType) => {
    // 创建高亮文本到高亮对象的映射
    const highlightMap = new Map<string, Highlight>()
    highlights.forEach(h => {
      const key = h.text.trim()
      if (key) highlightMap.set(key, h)
    })

    // 只遍历DOM一次，收集所有文本节点
    const walker = document.createTreeWalker(
      containerEl,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          const parent = node.parentElement
          if (parent?.classList.contains('meta-view-highlight')) {
            return NodeFilter.FILTER_REJECT
          }
          return node.textContent?.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
        }
      }
    )

    const textNodes: Text[] = []
    let currentNode: Node | null
    while ((currentNode = walker.nextNode())) {
      textNodes.push(currentNode as Text)
    }

    // 批量处理文本节点
    const processed = new Set<string>()
    for (const textNode of textNodes) {
      const text = textNode.textContent || ''

      // 检查是否包含任何待高亮文本
      for (const [searchText, highlight] of highlightMap.entries()) {
        if (processed.has(searchText)) continue

        const index = text.indexOf(searchText)
        if (index !== -1) {
          const beforeText = text.substring(0, index)
          const matchText = text.substring(index, index + searchText.length)
          const afterText = text.substring(index + searchText.length)

          const parent = textNode.parentNode
          if (parent) {
            const highlightEl = createHighlightElement(matchText, highlight, lensType)

            if (beforeText) {
              parent.insertBefore(document.createTextNode(beforeText), textNode)
            }
            parent.insertBefore(highlightEl, textNode)
            if (afterText) {
              parent.insertBefore(document.createTextNode(afterText), textNode)
            }
            parent.removeChild(textNode)

            processed.add(searchText)
            break // 处理完这个文本节点，继续下一个
          }
        }
      }
    }
  }

  /**
   * 按类型移除高亮
   */
  const removeHighlightsByType = (containerEl: HTMLElement, lensType: LensType) => {
    const highlights = containerEl.querySelectorAll(`.meta-view-highlight[data-lens-type="${lensType}"]`)
    highlights.forEach(el => {
      const parent = el.parentNode
      if (parent) {
        const textNode = document.createTextNode(el.textContent || '')
        parent.replaceChild(textNode, el)
      }
    })
    containerEl.normalize()
    console.log(`🧹 移除了 ${highlights.length} 个 ${lensType} 高亮`)
  }

  /**
   * 在 DOM 中查找并高亮文本（使用文本匹配）
   */
  const highlightTextInDOM = (containerEl: HTMLElement, highlight: Highlight, lensType?: LensType) => {
    const searchText = highlight.text.trim()
    if (!searchText) return

    // 创建 TreeWalker 遍历所有文本节点
    const walker = document.createTreeWalker(
      containerEl,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          // 跳过已高亮的节点
          const parent = node.parentElement
          if (parent?.classList.contains('meta-view-highlight')) {
            return NodeFilter.FILTER_REJECT
          }
          // 只接受有内容的文本节点
          return node.textContent?.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
        }
      }
    )

    const textNodes: Text[] = []
    let currentNode: Node | null
    while ((currentNode = walker.nextNode())) {
      textNodes.push(currentNode as Text)
    }

    // 在所有文本节点中查找匹配
    let found = false
    for (const textNode of textNodes) {
      const text = textNode.textContent || ''
      const index = text.indexOf(searchText)

      if (index !== -1) {
        // 找到匹配，分割文本节点并插入高亮
        const beforeText = text.substring(0, index)
        const matchText = text.substring(index, index + searchText.length)
        const afterText = text.substring(index + searchText.length)

        const parent = textNode.parentNode
        if (!parent) continue

        // 创建高亮元素
        const highlightEl = createHighlightElement(matchText, highlight, lensType)

        // 替换文本节点
        if (beforeText) {
          parent.insertBefore(document.createTextNode(beforeText), textNode)
        }
        parent.insertBefore(highlightEl, textNode)
        if (afterText) {
          parent.insertBefore(document.createTextNode(afterText), textNode)
        }
        parent.removeChild(textNode)

        found = true
        break // 只高亮第一个匹配项
      }
    }

    if (!found) {
      console.warn('⚠️ 未找到匹配文本:', searchText.substring(0, 30) + '...')
    }
  }

  /**
   * 创建高亮元素
   */
  const createHighlightElement = (text: string, highlight: Highlight, lensType?: LensType): HTMLElement => {
    const span = document.createElement('span')
    span.className = 'meta-view-highlight'
    span.dataset.category = highlight.category
    span.dataset.tooltip = highlight.tooltip // 存储tooltip内容供shadcn/ui使用
    if (lensType) {
      span.dataset.lensType = lensType
    }
    span.style.backgroundColor = highlight.color
    span.style.borderBottom = `2px solid ${highlight.color.replace('0.4', '0.6')}`
    span.style.cursor = 'help'
    span.style.padding = '0.1em 0.2em'
    span.style.borderRadius = '0.25em'
    span.style.transition = 'all 0.2s ease'
    span.textContent = text

    // 悬停效果
    span.addEventListener('mouseenter', () => {
      span.style.backgroundColor = highlight.color.replace('0.4', '0.6')
      span.style.boxShadow = '0 0 0 2px rgba(0, 0, 0, 0.1)'
    })
    span.addEventListener('mouseleave', () => {
      span.style.backgroundColor = highlight.color
      span.style.boxShadow = 'none'
    })

    return span
  }

  /**
   * 移除所有高亮
   */
  const removeHighlights = (containerEl: HTMLElement) => {
    const highlights = containerEl.querySelectorAll('.meta-view-highlight')
    highlights.forEach(el => {
      const parent = el.parentNode
      if (parent) {
        // 将高亮元素替换为纯文本节点
        const textNode = document.createTextNode(el.textContent || '')
        parent.replaceChild(textNode, el)
      }
    })

    // 合并相邻的文本节点
    containerEl.normalize()
  }

  /**
   * 清除DOM中的所有高亮（别名）
   */
  const clearHighlights = (containerEl: HTMLElement) => {
    removeHighlights(containerEl)
  }

  /**
   * 清空透镜数据
   */
  const clearLensResults = () => {
    lensResults.value.clear()
    enabledLenses.value.clear()
    lensError.value = null
  }

  return {
    // 状态
    enabledLenses: readonly(enabledLenses),
    lensResults: readonly(lensResults),
    loadingLenses: readonly(loadingLenses),
    error: readonly(lensError),

    // 计算属性
    isArgumentLensEnabled: computed(() => enabledLenses.value.has('argument_structure')),
    isStanceLensEnabled: computed(() => enabledLenses.value.has('author_stance')),
    isLoadingArgumentLens: computed(() => loadingLenses.value.has('argument_structure')),
    isLoadingStanceLens: computed(() => loadingLenses.value.has('author_stance')),

    // 方法
    loadLens,
    toggleLens,
    clearLens,
    renderHighlights,
    renderHighlightsByType,
    removeHighlights,
    removeHighlightsByType,
    clearHighlights,
    clearLensResults
  }
}
