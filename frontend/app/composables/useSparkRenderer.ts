/**
 * 火花渲染引擎 Composable
 * 用于在文章中渲染概念火花、论证火花等智能标注
 */

export interface ConceptSpark {
  text: string
  sentence_index: number
  importance_score: number
  explanation_hint: string
  dom_path: string
}

export interface ArgumentSpark {
  type: 'claim' | 'evidence' | 'transition'
  text: string
  sentence_index: number
  role_description: string
  dom_path: string
}

export interface AnalysisReport {
  meta_info: any
  concept_sparks: ConceptSpark[]
  argument_sparks?: ArgumentSpark[]
  knowledge_graph_nodes: string[]
  summary: string
  tags: string[]
}

export const useSparkRenderer = () => {
  /**
   * 渲染所有火花
   *
   * @param report - 分析报告数据
   */
  const renderSparks = async (report: AnalysisReport) => {
    const containerEl = document.getElementById('article-content-container')
    if (!containerEl) {
      console.warn('⚠️ 未找到文章容器元素')
      return
    }

    console.log('🎨 开始渲染火花...')

    // 1. 渲染概念火花
    if (report.concept_sparks && report.concept_sparks.length > 0) {
      await renderConceptSparks(containerEl, report.concept_sparks)
    }

    // 2. 渲染论证火花（如果有）
    if (report.argument_sparks && report.argument_sparks.length > 0) {
      await renderArgumentSparks(containerEl, report.argument_sparks)
    }

    console.log('✅ 火花渲染完成')
  }

  /**
   * 渲染概念火花
   *
   * @param container - 容器元素
   * @param sparks - 概念火花列表
   */
  const renderConceptSparks = async (
    container: HTMLElement,
    sparks: ConceptSpark[]
  ) => {
    console.log(`🌟 渲染 ${sparks.length} 个概念火花`)

    for (let i = 0; i < sparks.length; i++) {
      const spark = sparks[i]

      // 延迟渲染，制造瀑布流效果
      await new Promise(resolve => setTimeout(resolve, i * 50))

      try {
        const targetElement = document.querySelector(spark.dom_path)
        if (!targetElement) {
          console.warn(`⚠️ 无法找到目标元素: ${spark.dom_path}`)
          continue
        }

        // 创建火花元素
        const sparkEl = createConceptSparkElement(spark)

        // 高亮目标文本
        highlightTextInElement(targetElement as HTMLElement, spark.text, sparkEl)

      } catch (error) {
        console.error(`❌ 渲染火花失败:`, error)
      }
    }
  }

  /**
   * 创建概念火花元素
   *
   * @param spark - 概念火花数据
   * @returns HTML 元素
   */
  const createConceptSparkElement = (spark: ConceptSpark): HTMLElement => {
    const span = document.createElement('span')
    span.className = 'concept-spark'
    span.dataset.sparkText = spark.text
    span.dataset.hint = spark.explanation_hint

    // 样式：绿色虚线下划线
    span.style.borderBottom = '2px dotted #10b981'
    span.style.cursor = 'pointer'
    span.style.position = 'relative'
    span.style.transition = 'all 0.2s ease'
    span.style.opacity = '0'
    span.style.animation = 'fade-in-up 0.6s ease-out forwards'

    // 点击事件：显示解释卡片
    span.addEventListener('click', async (e) => {
      e.stopPropagation()
      await showConceptExplanation(spark)
    })

    // 悬停效果
    span.addEventListener('mouseenter', () => {
      span.style.backgroundColor = 'rgba(16, 185, 129, 0.1)'
      span.style.borderBottomWidth = '3px'
    })

    span.addEventListener('mouseleave', () => {
      span.style.backgroundColor = 'transparent'
      span.style.borderBottomWidth = '2px'
    })

    return span
  }

  /**
   * 在元素中高亮文本
   *
   * @param container - 容器元素
   * @param text - 要高亮的文本
   * @param highlightEl - 高亮元素
   */
  const highlightTextInElement = (
    container: HTMLElement,
    text: string,
    highlightEl: HTMLElement
  ) => {
    const walker = document.createTreeWalker(
      container,
      NodeFilter.SHOW_TEXT
    )

    let node: Text | null
    while (node = walker.nextNode() as Text) {
      const content = node.textContent || ''
      const index = content.indexOf(text)

      if (index >= 0) {
        const parent = node.parentNode
        if (!parent) continue

        const before = content.substring(0, index)
        const after = content.substring(index + text.length)

        highlightEl.textContent = text

        if (before) parent.insertBefore(document.createTextNode(before), node)
        parent.insertBefore(highlightEl, node)
        if (after) parent.insertBefore(document.createTextNode(after), node)
        parent.removeChild(node)

        break
      }
    }
  }

  /**
   * 显示概念解释卡片
   *
   * @param spark - 概念火花数据
   */
  const showConceptExplanation = async (spark: ConceptSpark) => {
    console.log(`💡 显示概念解释: ${spark.text}`)

    // 调用 AI 生成解释
    const config = useRuntimeConfig()

    try {
      const response = await $fetch(`${config.public.apiBase}/api/v1/sparks/explain`, {
        method: 'POST',
        body: {
          hint: spark.explanation_hint,
          concept: spark.text
        }
      })

      // 显示卡片（可以使用模态框或弹出卡片）
      showSparkCard({
        title: spark.text,
        content: response.explanation,
        type: 'concept',
        score: spark.importance_score
      })

    } catch (error) {
      console.error('❌ 获取概念解释失败:', error)
      // 降级：显示提示词
      showSparkCard({
        title: spark.text,
        content: spark.explanation_hint,
        type: 'concept',
        score: spark.importance_score
      })
    }
  }

  /**
   * 显示火花卡片
   *
   * @param data - 卡片数据
   */
  const showSparkCard = (data: {
    title: string
    content: string
    type: string
    score?: number
  }) => {
    // 简单实现：创建一个模态框
    // 实际项目中可以使用更精美的 UI 组件

    const modal = document.createElement('div')
    modal.className = 'fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex items-center justify-center'
    modal.onclick = () => modal.remove()

    const card = document.createElement('div')
    card.className = 'bg-white rounded-2xl shadow-2xl max-w-2xl p-6 m-4'
    card.onclick = (e) => e.stopPropagation()

    card.innerHTML = `
      <div class="border-b pb-4 mb-4">
        <h3 class="text-2xl font-bold text-gray-900">${data.title}</h3>
        ${data.score ? `<p class="text-sm text-green-600 mt-1">重要性: ${data.score}/10</p>` : ''}
      </div>
      <div class="text-gray-700 leading-relaxed">
        ${data.content}
      </div>
      <div class="mt-6 flex justify-end">
        <button class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
          关闭
        </button>
      </div>
    `

    const closeBtn = card.querySelector('button')
    closeBtn?.addEventListener('click', () => modal.remove())

    modal.appendChild(card)
    document.body.appendChild(modal)
  }

  /**
   * 渲染论证火花
   *
   * @param container - 容器元素
   * @param sparks - 论证火花列表
   */
  const renderArgumentSparks = async (
    container: HTMLElement,
    sparks: ArgumentSpark[]
  ) => {
    console.log(`📊 渲染 ${sparks.length} 个论证火花`)

    // 简化实现：与概念火花类似，但使用不同颜色
    for (const spark of sparks) {
      const targetElement = document.querySelector(spark.dom_path)
      if (!targetElement) continue

      const sparkEl = document.createElement('span')
      sparkEl.className = 'argument-spark'
      sparkEl.style.borderBottom = '2px solid #3b82f6'  // 蓝色
      sparkEl.style.cursor = 'pointer'

      sparkEl.onclick = () => {
        showSparkCard({
          title: `${spark.type === 'claim' ? '核心观点' : spark.type === 'evidence' ? '支撑证据' : '转折'}`,
          content: `${spark.role_description}\n\n"${spark.text}"`,
          type: 'argument'
        })
      }

      highlightTextInElement(targetElement as HTMLElement, spark.text, sparkEl)
    }
  }

  /**
   * 清除所有火花
   */
  const clearSparks = () => {
    document.querySelectorAll('.concept-spark, .argument-spark').forEach(el => {
      const text = el.textContent || ''
      el.replaceWith(document.createTextNode(text))
    })
  }

  return {
    renderSparks,
    renderConceptSparks,
    renderArgumentSparks,
    clearSparks
  }
}
