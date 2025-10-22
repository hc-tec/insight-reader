/**
 * 洞察回放 Composable
 * 负责加载和展示历史洞察记录，支持"划线回放"功能
 */

export interface InsightHistoryItem {
  id: number
  selected_text: string
  selected_start: number | null
  selected_end: number | null
  context_before: string | null
  context_after: string | null
  intent: string
  question: string | null
  insight: string
  reasoning: string | null
  created_at: string
}

export const useInsightReplay = () => {
  const config = useRuntimeConfig()

  // 状态
  const insightHistory = useState<InsightHistoryItem[]>('insight-history', () => [])
  const isReplayMode = useState<boolean>('is-replay-mode', () => false)
  const selectedHistoryItem = useState<InsightHistoryItem | null>('selected-history-item', () => null)
  const isLoading = useState<boolean>('insight-history-loading', () => false)

  /**
   * 加载文章的洞察历史
   *
   * 权限控制：
   * - 示例文章（is_demo=True）：任何人都可以访问，返回所有洞察
   * - 普通文章：需要登录且是文章所有者，返回该用户的洞察
   */
  const loadInsightHistory = async (articleId: number) => {
    isLoading.value = true
    try {
      const response = await $fetch<{ total: number; insights: InsightHistoryItem[] }>(
        `${config.public.apiBase}/api/v1/insights/history`,
        {
          params: {
            article_id: articleId
          }
        }
      )

      insightHistory.value = response.insights
      console.log('✅ 加载了', response.total, '条洞察历史')

      return response.insights
    } catch (error) {
      console.error('❌ 加载洞察历史失败:', error)
      return []
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 切换回放模式
   */
  const toggleReplayMode = () => {
    isReplayMode.value = !isReplayMode.value

    if (!isReplayMode.value) {
      selectedHistoryItem.value = null
    }
  }

  /**
   * 渲染历史标注到 DOM
   */
  const renderHistoryHighlights = (containerEl: HTMLElement, history: InsightHistoryItem[]) => {
    // 清除旧的标注
    removeHistoryHighlights(containerEl)

    console.log('🔍 开始渲染', history.length, '条历史标注')

    // 使用文本匹配算法渲染每个标注
    for (const item of history) {
      try {
        highlightHistoryItem(containerEl, item)
      } catch (error) {
        console.error('❌ 渲染标注失败:', item.selected_text.substring(0, 30), error)
      }
    }

    console.log('✅ 历史标注渲染完成')
  }

  /**
   * 在 DOM 中高亮历史项
   */
  const highlightHistoryItem = (containerEl: HTMLElement, item: InsightHistoryItem) => {
    const searchText = item.selected_text.trim()
    if (!searchText) return

    // 优先使用位置信息
    if (item.selected_start !== null && item.selected_end !== null) {
      const success = highlightByPosition(containerEl, item)
      if (!success) {
        // 位置高亮失败，降级到文本匹配
        console.warn('⚠️ 位置高亮失败，降级到文本匹配')
        highlightByTextMatch(containerEl, item)
      }
    } else {
      // 没有位置信息，直接使用文本匹配
      highlightByTextMatch(containerEl, item)
    }
  }

  /**
   * 基于位置精确高亮（主方案）
   */
  const highlightByPosition = (containerEl: HTMLElement, item: InsightHistoryItem): boolean => {
    if (item.selected_start === null || item.selected_end === null) {
      return false
    }

    // 获取文章内容
    const { content } = useArticle()
    const fullText = content.value

    if (!fullText) {
      return false
    }

    // 从位置提取目标文本
    const targetText = fullText.substring(item.selected_start, item.selected_end)

    // 使用 TreeWalker 收集所有文本节点
    const walker = document.createTreeWalker(
      containerEl,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          const parent = node.parentElement
          if (parent?.classList.contains('insight-replay-highlight')) {
            return NodeFilter.FILTER_REJECT
          }
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

    // 构建位置映射：DOM文本节点 -> 文章位置
    let currentOffset = 0
    const nodeMap: Array<{ node: Text; startOffset: number; endOffset: number }> = []

    for (const node of textNodes) {
      const text = node.textContent || ''
      nodeMap.push({
        node,
        startOffset: currentOffset,
        endOffset: currentOffset + text.length
      })
      currentOffset += text.length
    }

    // 查找包含目标区间的节点
    const targetNodes = nodeMap.filter(
      n => n.startOffset < item.selected_end! && n.endOffset > item.selected_start!
    )

    if (targetNodes.length === 0) {
      console.warn('⚠️ 未找到目标节点')
      return false
    }

    // 简化：只处理单节点情况
    if (targetNodes.length > 1) {
      console.warn('⚠️ 跨多个节点，降级到文本匹配')
      return false
    }

    // 单节点高亮
    const targetNode = targetNodes[0]
    const node = targetNode.node
    const relativeStart = Math.max(0, item.selected_start - targetNode.startOffset)
    const relativeEnd = Math.min(
      node.textContent!.length,
      item.selected_end - targetNode.startOffset
    )

    const textContent = node.textContent || ''
    const beforeText = textContent.substring(0, relativeStart)
    const highlightText = textContent.substring(relativeStart, relativeEnd)
    const afterText = textContent.substring(relativeEnd)

    // 验证提取的文本是否匹配
    if (highlightText !== targetText) {
      console.warn('⚠️ 位置提取的文本不匹配')
      console.log('期望:', targetText.substring(0, 50))
      console.log('实际:', highlightText.substring(0, 50))
      return false
    }

    const parent = node.parentNode
    if (!parent) return false

    // 创建高亮元素
    const highlightEl = createHistoryHighlightElement(highlightText, item)

    // 替换文本节点
    if (beforeText) {
      parent.insertBefore(document.createTextNode(beforeText), node)
    }
    parent.insertBefore(highlightEl, node)
    if (afterText) {
      parent.insertBefore(document.createTextNode(afterText), node)
    }
    parent.removeChild(node)

    console.log('✅ 基于位置高亮成功:', item.selected_start, '-', item.selected_end)
    return true
  }

  /**
   * 基于文本匹配高亮（降级方案）
   */
  const highlightByTextMatch = (containerEl: HTMLElement, item: InsightHistoryItem) => {
    const searchText = item.selected_text.trim()
    if (!searchText) return

    // 使用 TreeWalker 查找文本
    const walker = document.createTreeWalker(
      containerEl,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          const parent = node.parentElement
          if (parent?.classList.contains('insight-replay-highlight')) {
            return NodeFilter.FILTER_REJECT
          }
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

    // 查找匹配
    for (const textNode of textNodes) {
      const text = textNode.textContent || ''
      const index = text.indexOf(searchText)

      if (index !== -1) {
        const beforeText = text.substring(0, index)
        const matchText = text.substring(index, index + searchText.length)
        const afterText = text.substring(index + searchText.length)

        const parent = textNode.parentNode
        if (!parent) continue

        // 创建标注元素
        const highlightEl = createHistoryHighlightElement(matchText, item)

        // 替换文本节点
        if (beforeText) {
          parent.insertBefore(document.createTextNode(beforeText), textNode)
        }
        parent.insertBefore(highlightEl, textNode)
        if (afterText) {
          parent.insertBefore(document.createTextNode(afterText), textNode)
        }
        parent.removeChild(textNode)

        break
      }
    }
  }

  /**
   * 创建历史标注元素
   */
  const createHistoryHighlightElement = (text: string, item: InsightHistoryItem): HTMLElement => {
    const span = document.createElement('span')
    span.className = 'insight-replay-highlight'
    span.dataset.insightId = item.id.toString()

    // 样式：橙色下划线
    span.style.borderBottom = '3px solid #f97316'
    span.style.cursor = 'pointer'
    span.style.backgroundColor = 'rgba(249, 115, 22, 0.1)'
    span.style.padding = '0.1em 0.2em'
    span.style.borderRadius = '0.25em'
    span.style.transition = 'all 0.2s ease'
    span.textContent = text

    // 点击显示到右侧洞察区域
    span.addEventListener('click', (e) => {
      e.stopPropagation()

      // 获取洞察生成器状态（用于显示到右侧面板）
      const { currentInsight, currentReasoning } = useInsightGenerator()

      // 获取选中状态（用于恢复上下文）
      const { selectedText, context, selectedStart, selectedEnd, showIntentButtons } = useSelection()

      // 显示历史洞察内容到右侧面板
      currentInsight.value = item.insight
      if (item.reasoning) {
        currentReasoning.value = item.reasoning
      }

      // 恢复选中状态，允许继续对话
      selectedText.value = item.selected_text
      const contextBefore = item.context_before || ''
      const contextAfter = item.context_after || ''
      context.value = contextBefore + item.selected_text + contextAfter
      selectedStart.value = item.selected_start
      selectedEnd.value = item.selected_end

      // 显示意图按钮，允许继续提问
      showIntentButtons.value = true

      console.log('📖 已显示历史洞察到右侧面板，可以继续对话')
    })

    // 悬停效果
    span.addEventListener('mouseenter', () => {
      span.style.backgroundColor = 'rgba(249, 115, 22, 0.2)'
      span.style.boxShadow = '0 0 0 2px rgba(249, 115, 22, 0.2)'
    })
    span.addEventListener('mouseleave', () => {
      span.style.backgroundColor = 'rgba(249, 115, 22, 0.1)'
      span.style.boxShadow = 'none'
    })

    return span
  }

  /**
   * 移除历史标注
   */
  const removeHistoryHighlights = (containerEl: HTMLElement) => {
    const highlights = containerEl.querySelectorAll('.insight-replay-highlight')
    highlights.forEach(el => {
      const parent = el.parentNode
      if (parent) {
        const textNode = document.createTextNode(el.textContent || '')
        parent.replaceChild(textNode, el)
      }
    })
    containerEl.normalize()
  }

  /**
   * 选择历史项
   */
  const selectHistoryItem = (item: InsightHistoryItem | null) => {
    selectedHistoryItem.value = item
  }

  /**
   * 清空回放状态
   */
  const clearReplayState = () => {
    insightHistory.value = []
    isReplayMode.value = false
    selectedHistoryItem.value = null
  }

  return {
    // 状态
    insightHistory: readonly(insightHistory),
    isReplayMode: readonly(isReplayMode),
    selectedHistoryItem: readonly(selectedHistoryItem),
    isLoading: readonly(isLoading),

    // 方法
    loadInsightHistory,
    toggleReplayMode,
    renderHistoryHighlights,
    removeHistoryHighlights,
    selectHistoryItem,
    clearReplayState
  }
}
