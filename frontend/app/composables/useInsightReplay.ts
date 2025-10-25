/**
 * 洞察回放 Composable
 * 负责加载和展示历史洞察记录，支持"划线回放"功能
 */

export interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
  reasoning?: string  // 仅 assistant 消息有
  timestamp: string
  insight_id?: number | null  // 对应数据库中的洞察记录 ID（用户消息为 null，assistant 消息有值）
}

export interface InsightConversation {
  root_insight_id: number
  selected_text: string
  selected_start: number | null
  selected_end: number | null
  context_before: string | null
  context_after: string | null
  intent: string
  question?: string | null  // ✅ 添加 question 字段（自定义问题）
  created_at: string
  messages: ConversationMessage[]  // 完整的对话历史
}

// 保留旧接口用于向后兼容（内部使用）
interface LegacyInsightHistoryItem {
  id: number
  parent_id: number | null
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

  // 状态：使用新的对话结构
  const insightConversations = useState<InsightConversation[]>('insight-conversations', () => [])
  const isReplayMode = useState<boolean>('is-replay-mode', () => false)
  const selectedConversation = useState<InsightConversation | null>('selected-conversation', () => null)
  const isLoading = useState<boolean>('insight-history-loading', () => false)

  /**
   * 加载文章的洞察历史（对话格式）
   *
   * 权限控制：
   * - 示例文章（is_demo=True）：任何人都可以访问，返回所有洞察
   * - 普通文章：需要登录且是文章所有者，返回该用户的洞察
   */
  const loadInsightHistory = async (articleId: number) => {
    isLoading.value = true
    try {
      const response = await $fetch<{ total: number; conversations: InsightConversation[] }>(
        `${config.public.apiBase}/api/v1/insights/history`,
        {
          params: {
            article_id: articleId
          }
        }
      )

      insightConversations.value = response.conversations
      console.log('✅ 加载了', response.total, '个对话链（共', response.conversations.reduce((sum, c) => sum + c.messages.length, 0), '条消息）')

      return response.conversations
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
      selectedConversation.value = null
    }
  }

  /**
   * 渲染历史标注到 DOM（仅标注根洞察的选中文本）
   * 支持嵌套和重叠的洞察
   */
  const renderHistoryHighlights = (containerEl: HTMLElement, conversations: InsightConversation[]) => {
    // 清除旧的标注
    removeHistoryHighlights(containerEl)

    console.log('🔍 开始渲染', conversations.length, '个对话链的标注')

    // 按选中文本长度从长到短排序（先渲染长的，再渲染短的，这样短的会嵌套在长的内部）
    const sortedConversations = [...conversations].sort((a, b) =>
      b.selected_text.length - a.selected_text.length
    )

    // 为每个对话的根洞察渲染标注
    for (const conversation of sortedConversations) {
      try {
        highlightConversation(containerEl, conversation)
      } catch (error) {
        console.error('❌ 渲染标注失败:', conversation.selected_text.substring(0, 30), error)
      }
    }

    console.log('✅ 历史标注渲染完成')
  }

  /**
   * 在 DOM 中高亮对话的根洞察
   */
  const highlightConversation = (containerEl: HTMLElement, conversation: InsightConversation) => {
    const searchText = conversation.selected_text.trim()
    if (!searchText) return

    // 优先使用位置信息
    if (conversation.selected_start !== null && conversation.selected_end !== null) {
      const success = highlightByPosition(containerEl, conversation)
      if (!success) {
        // 位置高亮失败，降级到文本匹配
        console.warn('⚠️ 位置高亮失败，降级到文本匹配')
        highlightByTextMatch(containerEl, conversation)
      }
    } else {
      // 没有位置信息，直接使用文本匹配
      highlightByTextMatch(containerEl, conversation)
    }
  }

  /**
   * 基于位置精确高亮（主方案）
   */
  const highlightByPosition = (containerEl: HTMLElement, conversation: InsightConversation): boolean => {
    if (conversation.selected_start === null || conversation.selected_end === null) {
      return false
    }

    // 获取文章内容
    const { content } = useArticle()
    const fullText = content.value

    if (!fullText) {
      return false
    }

    // 从位置提取目标文本
    const targetText = fullText.substring(conversation.selected_start, conversation.selected_end)

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
      n => n.startOffset < conversation.selected_end! && n.endOffset > conversation.selected_start!
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
    const relativeStart = Math.max(0, conversation.selected_start - targetNode.startOffset)
    const relativeEnd = Math.min(
      node.textContent!.length,
      conversation.selected_end - targetNode.startOffset
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
    const highlightEl = createHistoryHighlightElement(highlightText, conversation)

    // 替换文本节点
    if (beforeText) {
      parent.insertBefore(document.createTextNode(beforeText), node)
    }
    parent.insertBefore(highlightEl, node)
    if (afterText) {
      parent.insertBefore(document.createTextNode(afterText), node)
    }
    parent.removeChild(node)

    console.log('✅ 基于位置高亮成功:', conversation.selected_start, '-', conversation.selected_end)
    return true
  }

  /**
   * 基于文本匹配高亮（降级方案）
   * 支持嵌套高亮：可以在已高亮的区域内继续高亮
   */
  const highlightByTextMatch = (containerEl: HTMLElement, conversation: InsightConversation) => {
    const searchText = conversation.selected_text.trim()
    if (!searchText) return

    // 使用 TreeWalker 查找文本（包括已高亮区域内的文本）
    const walker = document.createTreeWalker(
      containerEl,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          // 移除了对 'insight-replay-highlight' 的过滤，允许嵌套高亮
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

    // 查找所有匹配（而不只是第一个）
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
        const highlightEl = createHistoryHighlightElement(matchText, conversation)

        // 替换文本节点
        if (beforeText) {
          parent.insertBefore(document.createTextNode(beforeText), textNode)
        }
        parent.insertBefore(highlightEl, textNode)
        if (afterText) {
          parent.insertBefore(document.createTextNode(afterText), textNode)
        }
        parent.removeChild(textNode)

        // 注意：不再 break，但为了避免同一文本节点被多次处理，我们只处理一次
        break
      }
    }
  }

  /**
   * 创建历史标注元素
   * 支持多层嵌套和点击时选择
   */
  const createHistoryHighlightElement = (text: string, conversation: InsightConversation): HTMLElement => {
    const span = document.createElement('span')
    span.className = 'insight-replay-highlight'
    span.dataset.conversationId = conversation.root_insight_id.toString()

    // 样式：橙色下划线，支持嵌套时的视觉层次
    span.style.borderBottom = '3px solid #f97316'
    span.style.cursor = 'pointer'
    span.style.backgroundColor = 'rgba(249, 115, 22, 0.1)'
    span.style.padding = '0.1em 0.2em'
    span.style.borderRadius = '0.25em'
    span.style.transition = 'all 0.2s ease'
    span.style.position = 'relative'  // 用于嵌套定位
    span.style.display = 'inline'  // 保持内联
    span.textContent = text

    // 点击事件：检测是否有多个重叠的洞察
    span.addEventListener('click', (e) => {
      e.stopPropagation()

      // 收集所有祖先元素中的洞察（嵌套的洞察）
      const overlappingConversations: InsightConversation[] = []
      let currentElement: HTMLElement | null = span

      while (currentElement) {
        if (currentElement.classList?.contains('insight-replay-highlight')) {
          const conversationId = currentElement.dataset.conversationId
          if (conversationId) {
            // 找到对应的 conversation 对象
            const conv = insightConversations.value.find(c => c.root_insight_id === parseInt(conversationId))
            if (conv && !overlappingConversations.find(c => c.root_insight_id === conv.root_insight_id)) {
              overlappingConversations.push(conv)
            }
          }
        }
        currentElement = currentElement.parentElement
      }

      console.log('🔍 检测到', overlappingConversations.length, '个重叠的洞察')

      // 如果有多个重叠的洞察，显示选择菜单
      if (overlappingConversations.length > 1) {
        showConversationSelectionMenu(e, overlappingConversations)
      } else if (overlappingConversations.length === 1) {
        // 只有一个洞察，直接显示
        loadConversation(overlappingConversations[0])
      }
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
   * 显示对话选择菜单（当有多个重叠的洞察时）
   */
  const showConversationSelectionMenu = (event: MouseEvent, conversations: InsightConversation[]) => {
    // 移除已存在的菜单
    const existingMenu = document.querySelector('.conversation-selection-menu')
    if (existingMenu) {
      existingMenu.remove()
    }

    // 创建菜单
    const menu = document.createElement('div')
    menu.className = 'conversation-selection-menu'
    menu.style.position = 'fixed'
    menu.style.left = `${event.clientX}px`
    menu.style.top = `${event.clientY + 10}px`
    menu.style.backgroundColor = 'white'
    menu.style.border = '1px solid #e5e7eb'
    menu.style.borderRadius = '0.5rem'
    menu.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
    menu.style.zIndex = '9999'
    menu.style.minWidth = '200px'
    menu.style.maxWidth = '300px'
    menu.style.padding = '0.5rem 0'

    // 添加标题
    const title = document.createElement('div')
    title.style.padding = '0.5rem 1rem'
    title.style.fontSize = '0.875rem'
    title.style.fontWeight = '600'
    title.style.color = '#6b7280'
    title.style.borderBottom = '1px solid #e5e7eb'
    title.textContent = `选择要查看的对话（${conversations.length}个）`
    menu.appendChild(title)

    // 按文本长度排序（短的在前）
    const sortedConversations = [...conversations].sort((a, b) => a.selected_text.length - b.selected_text.length)

    // 为每个对话创建菜单项
    sortedConversations.forEach((conv, index) => {
      const item = document.createElement('div')
      item.style.padding = '0.75rem 1rem'
      item.style.cursor = 'pointer'
      item.style.fontSize = '0.875rem'
      item.style.transition = 'background-color 0.2s'
      item.style.borderBottom = index < sortedConversations.length - 1 ? '1px solid #f3f4f6' : 'none'

      // 显示选中文本的预览（最多50字）
      const preview = conv.selected_text.length > 50
        ? conv.selected_text.substring(0, 50) + '...'
        : conv.selected_text

      item.innerHTML = `
        <div style="font-weight: 500; color: #111827; margin-bottom: 0.25rem;">
          ${preview}
        </div>
        <div style="font-size: 0.75rem; color: #9ca3af;">
          ${conv.messages.length} 条消息 · ${conv.selected_text.length} 字
        </div>
      `

      // 悬停效果
      item.addEventListener('mouseenter', () => {
        item.style.backgroundColor = '#f9fafb'
      })
      item.addEventListener('mouseleave', () => {
        item.style.backgroundColor = 'transparent'
      })

      // 点击事件
      item.addEventListener('click', () => {
        loadConversation(conv)
        menu.remove()
      })

      menu.appendChild(item)
    })

    // 添加到页面
    document.body.appendChild(menu)

    // 点击其他地方关闭菜单
    const closeMenu = (e: MouseEvent) => {
      if (!menu.contains(e.target as Node)) {
        menu.remove()
        document.removeEventListener('click', closeMenu)
      }
    }
    setTimeout(() => {
      document.addEventListener('click', closeMenu)
    }, 100)
  }

  /**
   * 加载并显示对话
   */
  const loadConversation = (conversation: InsightConversation) => {
    // 标记为从历史恢复，避免弹出意图按钮
    const isRestoringFromHistory = useState('is-restoring-from-history', () => false)
    isRestoringFromHistory.value = true

    // 获取追问管理状态
    const { conversationHistory, clearConversation } = useFollowUp()
    const { currentInsight, currentReasoning } = useInsightGenerator()
    const { selectedText, context, selectedStart, selectedEnd } = useSelection()

    // 清空当前追问历史
    clearConversation()

    // 分离初始对话和追问对话
    // messages 格式：[user_initial, assistant_initial, user_followup1, assistant_followup1, ...]
    const messages = conversation.messages

    // 第一条 assistant 消息是初始洞察
    const initialAssistant = messages.find(m => m.role === 'assistant')

    // 恢复选中状态，允许继续对话
    selectedText.value = conversation.selected_text
    const contextBefore = conversation.context_before || ''
    const contextAfter = conversation.context_after || ''
    context.value = contextBefore + conversation.selected_text + contextAfter
    selectedStart.value = conversation.selected_start
    selectedEnd.value = conversation.selected_end

    // ⚠️ 重要：先通过全局状态设置 currentRequest，再设置 currentInsight
    // 使用 useState 创建全局状态（与 index.vue 共享）
    const currentRequest = useState<any>('current-request-global', () => undefined)
    currentRequest.value = {
      selected_text: conversation.selected_text,
      context: context.value,
      intent: conversation.intent,
      custom_question: conversation.question || undefined,  // ✅ 添加自定义问题
      selected_start: conversation.selected_start ?? undefined,
      selected_end: conversation.selected_end ?? undefined,
      use_reasoning: !!initialAssistant?.reasoning
    }

    // 显示初始洞察到主洞察区
    if (initialAssistant) {
      currentInsight.value = initialAssistant.content
      currentReasoning.value = initialAssistant.reasoning || ''

      // 更新 currentInsightId 为初始洞察的 ID
      const { currentInsightId } = useInsightGenerator()
      currentInsightId.value = initialAssistant.insight_id || null
    }

    // 加载追问对话历史到 conversationHistory（从第三条消息开始，即第一个追问）
    // messages 格式：[user_initial, assistant_initial, user_followup1, assistant_followup1, ...]
    // 初始洞察已经显示在 currentInsight 中，所以对话历史只需要包含追问部分
    const followUpMessages = messages.slice(2)  // 跳过前两条（初始问答），只保留追问对话
    if (followUpMessages.length > 0) {
      conversationHistory.value = followUpMessages.map(msg => ({
        role: msg.role,
        content: msg.content,
        reasoning: msg.reasoning,
        timestamp: new Date(msg.timestamp).getTime(),
        insight_id: msg.insight_id || null  // 保留 insight_id
      }))
      console.log('📖 加载了追问对话历史:', followUpMessages.length, '条消息')
    } else {
      console.log('📖 这是初始洞察，没有追问记录')
    }

    // 打开 AI 洞察侧边栏（使用全局状态）
    const insightPanelExpanded = useState('insight-panel-expanded', () => false)
    if (!insightPanelExpanded.value) {
      insightPanelExpanded.value = true
    }

    console.log('📖 已显示完整对话到右侧面板（总共', conversation.messages.length, '条消息）')
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
   * 选择对话
   */
  const selectConversation = (conversation: InsightConversation | null) => {
    selectedConversation.value = conversation
  }

  /**
   * 清空回放状态
   */
  const clearReplayState = () => {
    insightConversations.value = []
    isReplayMode.value = false
    selectedConversation.value = null
  }

  return {
    // 状态
    insightConversations: readonly(insightConversations),
    isReplayMode: readonly(isReplayMode),
    selectedConversation: readonly(selectedConversation),
    isLoading: readonly(isLoading),

    // 方法
    loadInsightHistory,
    toggleReplayMode,
    renderHistoryHighlights,
    removeHistoryHighlights,
    selectConversation,
    clearReplayState
  }
}
