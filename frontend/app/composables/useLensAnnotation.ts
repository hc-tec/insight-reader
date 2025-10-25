/**
 * 透镜注解模式 Composable
 * 负责管理透镜高亮的注解展示
 * 使用 relative + absolute 定位，注解卡片作为句子子元素
 */

export interface LensAnnotation {
  id: string
  sentenceIndex: number
  sentenceText: string
  lensType: 'argument_structure' | 'author_stance'
  annotationContent: string
  position: {
    top: number
    left: number
    width: number
    height: number
  }
}

export const useLensAnnotation = () => {
  // 注解模式开关状态
  const isAnnotationModeActive = useState<boolean>('lens-annotation-mode-active', () => false)

  // 当前激活的注解列表
  const annotations = useState<LensAnnotation[]>('lens-annotations', () => [])

  /**
   * 切换注解模式
   */
  const toggleAnnotationMode = () => {
    isAnnotationModeActive.value = !isAnnotationModeActive.value

    if (isAnnotationModeActive.value) {
      // 开启模式：收集注解并注入DOM
      collectAndInjectAnnotations()
    } else {
      // 关闭模式：清空注解
      clearAnnotations()
    }
  }

  /**
   * 收集所有透镜高亮并直接注入注解卡片到DOM
   */
  const collectAndInjectAnnotations = () => {
    const collectedAnnotations: LensAnnotation[] = []

    // 获取所有透镜高亮（使用 .meta-view-highlight 类名）
    const allHighlights = document.querySelectorAll('.meta-view-highlight')

    allHighlights.forEach((el, index) => {
      const highlightEl = el as HTMLElement
      const lensType = highlightEl.getAttribute('data-lens-type') as 'argument_structure' | 'author_stance' | null
      const tooltip = highlightEl.getAttribute('data-tooltip')

      // 只收集有透镜类型和tooltip的高亮
      if (!lensType || !tooltip) return

      const annotationId = `lens-annotation-${lensType}-${index}`

      // 检查是否已经包装过
      let wrapper = highlightEl.parentElement
      if (!wrapper?.hasAttribute('data-lens-wrapper')) {
        // 创建包装器
        wrapper = document.createElement('span')
        wrapper.style.position = 'relative'
        wrapper.style.display = 'inline-block'
        wrapper.setAttribute('data-lens-wrapper', 'true')
        wrapper.setAttribute('data-annotation-id', annotationId)

        // 包装高亮元素
        const parent = highlightEl.parentNode
        if (parent) {
          parent.insertBefore(wrapper, highlightEl)
          wrapper.appendChild(highlightEl)
        }
      }

      // 检查是否已经有注解卡片
      if (!wrapper.querySelector('.lens-annotation-card')) {
        // 创建注解卡片
        const card = createAnnotationCard({
          id: annotationId,
          sentenceIndex: index,
          sentenceText: highlightEl.textContent || '',
          lensType: lensType,
          annotationContent: tooltip,
          position: { top: 0, left: 0, width: 0, height: 0 }
        })

        wrapper.appendChild(card)
      }

      collectedAnnotations.push({
        id: annotationId,
        sentenceIndex: index,
        sentenceText: highlightEl.textContent || '',
        lensType: lensType,
        annotationContent: tooltip,
        position: { top: 0, left: 0, width: 0, height: 0 }
      })
    })

    annotations.value = collectedAnnotations
    console.log(`📝 收集并注入 ${collectedAnnotations.length} 个透镜注解`)
  }

  /**
   * 创建注解卡片DOM元素
   */
  const createAnnotationCard = (annotation: LensAnnotation): HTMLElement => {
    const card = document.createElement('div')
    card.className = 'lens-annotation-card'
    card.setAttribute('data-annotation-id', annotation.id)

    // 只显示核心内容
    card.innerHTML = `
      <div class="annotation-content-compact">
        ${escapeHtml(annotation.annotationContent)}
      </div>
    `

    // 添加样式
    applyCardStyles(card)

    return card
  }

  /**
   * 应用卡片样式
   */
  const applyCardStyles = (card: HTMLElement) => {
    // 卡片基础样式 - 精简版
    Object.assign(card.style, {
      position: 'absolute',
      top: '0',
      left: 'calc(100% + 20px)',
      width: '240px',
      maxWidth: '300px',
      background: 'rgba(255, 255, 255, 0.98)',
      border: '1px solid rgba(0, 0, 0, 0.08)',
      borderRadius: '6px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      padding: '10px 12px',
      zIndex: '1000',
      fontSize: '13px',
      lineHeight: '1.5',
      color: '#666',
      pointerEvents: 'auto'
    })

    // 添加全局样式（如果还没有）
    if (!document.getElementById('lens-annotation-styles')) {
      const styleEl = document.createElement('style')
      styleEl.id = 'lens-annotation-styles'
      styleEl.textContent = `
        .lens-annotation-card .annotation-content-compact {
          font-size: 13px;
          line-height: 1.5;
          color: #555;
        }
      `
      document.head.appendChild(styleEl)
    }
  }

  /**
   * HTML转义
   */
  const escapeHtml = (text: string): string => {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  /**
   * 刷新注解位置（滚动或窗口大小变化时调用）
   */
  const refreshAnnotationPositions = () => {
    if (!isAnnotationModeActive.value) return
    // 使用 relative + absolute 定位，不需要手动刷新位置
  }

  /**
   * 清空所有注解
   */
  const clearAnnotations = () => {
    // 移除所有注解卡片
    const cards = document.querySelectorAll('.lens-annotation-card')
    cards.forEach(card => card.remove())

    // 解包所有包装器
    const wrappers = document.querySelectorAll('[data-lens-wrapper]')
    wrappers.forEach(wrapper => {
      const parent = wrapper.parentNode
      const child = wrapper.firstChild
      if (parent && child) {
        parent.insertBefore(child, wrapper)
        parent.removeChild(wrapper)
      }
    })

    annotations.value = []
    console.log('🧹 已清空所有透镜注解')
  }

  return {
    isAnnotationModeActive: readonly(isAnnotationModeActive),
    annotations: readonly(annotations),
    toggleAnnotationMode,
    refreshAnnotationPositions,
    clearAnnotations
  }
}
