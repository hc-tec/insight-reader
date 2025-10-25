/**
 * 火花渲染引擎 V2 - 聚合版本
 *
 * 改进：
 * 1. 按句子聚合所有火花（concept + argument）
 * 2. 使用轻量级徽章代替文本高亮
 * 3. 点击句子显示侧边栏，不使用模态框
 * 4. 完整展示元信息数据
 * 5. 支持使用后端 Stanza 分句结果重新渲染文章
 */

import { useArticleRenderer } from './useArticleRenderer'

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
  sentences?: string[]  // 后端提供的分句结果（Stanza 分句）
}

export interface SentenceSparks {
  sentence_index: number
  sentence_text: string
  concepts: ConceptSpark[]
  arguments: ArgumentSpark[]
  totalCount: number
}

export const useSparkRendererV2 = () => {
  // 火花分组数据
  const sparkGroups = ref<Map<number, SentenceSparks>>(new Map())

  /**
   * 渲染所有火花
   */
  const renderSparks = async (report: AnalysisReport) => {
    const containerEl = document.getElementById('article-content-container')
    if (!containerEl) {
      console.warn('⚠️ 未找到文章容器元素')
      return
    }

    console.log('🎨 开始渲染火花（聚合模式）...')

    // 0. 如果报告中包含后端分句结果，先重新渲染文章
    if (report.sentences && report.sentences.length > 0) {
      console.log(`📊 检测到后端分句结果（Stanza），共 ${report.sentences.length} 个句子`)
      console.log('🔄 使用后端分句重新渲染文章内容...')

      // 动态导入 useArticleRenderer
      const { renderWithBackendSentences } = useArticleRenderer()
      const newHtml = renderWithBackendSentences(report.sentences)

      // 更新容器内容
      containerEl.innerHTML = newHtml

      console.log('✅ 文章内容已使用后端分句重新渲染')
    } else {
      console.log('ℹ️ 使用前端原有分句结果')
    }

    // 1. 聚合火花
    const groups = aggregateSparks(report)
    sparkGroups.value = groups

    console.log(`📊 火花聚合完成：${groups.size} 个句子包含火花`)

    // 2. 渲染徽章
    await renderSparkBadges(containerEl, groups)

    console.log('✅ 火花渲染完成')
  }

  /**
   * 聚合火花：按句子分组
   */
  const aggregateSparks = (report: AnalysisReport): Map<number, SentenceSparks> => {
    const groups = new Map<number, SentenceSparks>()

    // 添加概念火花
    if (report.concept_sparks) {
      report.concept_sparks.forEach(spark => {
        if (!groups.has(spark.sentence_index)) {
          groups.set(spark.sentence_index, {
            sentence_index: spark.sentence_index,
            sentence_text: '',  // 稍后从 DOM 获取
            concepts: [],
            arguments: [],
            totalCount: 0
          })
        }
        const group = groups.get(spark.sentence_index)!
        group.concepts.push(spark)
        group.totalCount++
      })
    }

    // 添加论证火花
    if (report.argument_sparks) {
      report.argument_sparks.forEach(spark => {
        if (!groups.has(spark.sentence_index)) {
          groups.set(spark.sentence_index, {
            sentence_index: spark.sentence_index,
            sentence_text: '',
            concepts: [],
            arguments: [],
            totalCount: 0
          })
        }
        const group = groups.get(spark.sentence_index)!
        group.arguments.push(spark)
        group.totalCount++
      })
    }

    return groups
  }

  /**
   * 渲染火花徽章
   */
  const renderSparkBadges = async (
    container: HTMLElement,
    groups: Map<number, SentenceSparks>
  ) => {
    for (const [sentenceIndex, group] of groups.entries()) {
      // 延迟渲染，制造瀑布流效果
      await new Promise(resolve => setTimeout(resolve, sentenceIndex * 30))

      try {
        const sentenceEl = document.querySelector(`#sentence-${sentenceIndex}`)
        if (!sentenceEl) {
          console.warn(`⚠️ 无法找到句子元素: #sentence-${sentenceIndex}`)
          continue
        }

        // 获取句子文本
        group.sentence_text = sentenceEl.textContent || ''

        // 分别处理概念火花和论证火花
        const hasConceptSparks = group.concepts.length > 0
        const hasArgumentSparks = group.arguments.length > 0

        // 先生成tooltip内容
        const tooltipContent = generateTooltipContent(group)
        sentenceEl.setAttribute('data-spark-tooltip', tooltipContent)

        if (hasConceptSparks) {
          // 概念火花：对具体词语进行高亮（这会修改innerHTML）
          highlightConceptSparks(sentenceEl as HTMLElement, group.concepts)
        }

        if (hasArgumentSparks) {
          // 论证火花：对整个句子添加样式
          sentenceEl.classList.add('has-argument-sparks')
        }

        // 创建徽章（如果有任何类型的火花）
        const badge = createSparkBadge(group)
        sentenceEl.appendChild(badge)

        // ⚠️ 在innerHTML修改之后添加点击事件
        // 添加点击事件来切换tooltip显示（对整个句子）
        sentenceEl.addEventListener('click', (e) => {
          // 如果点击的是概念高亮，不处理（让概念高亮自己的点击事件处理）
          if ((e.target as HTMLElement).classList.contains('concept-spark-highlight')) {
            return
          }

          e.stopPropagation()

          // 关闭所有tooltip（包括概念tooltip和句子tooltip）
          document.querySelectorAll('.concept-spark-highlight.show-concept-tooltip').forEach(el => {
            el.classList.remove('show-concept-tooltip')
          })
          document.querySelectorAll('[data-spark-tooltip].show-tooltip').forEach(el => {
            if (el !== sentenceEl) {
              el.classList.remove('show-tooltip')
            }
          })

          // 切换当前句子tooltip
          sentenceEl.classList.toggle('show-tooltip')
        })

        // 添加悬停效果（仅对论证火花）
        if (hasArgumentSparks) {
          sentenceEl.addEventListener('mouseenter', () => {
            sentenceEl.classList.add('spark-hover')
          })

          sentenceEl.addEventListener('mouseleave', () => {
            sentenceEl.classList.remove('spark-hover')
          })
        }

      } catch (error) {
        console.error(`❌ 渲染火花徽章失败:`, error)
      }
    }

    // 添加全局样式
    injectStyles()

    // 添加全局点击事件，点击其他地方时关闭tooltip
    setupGlobalClickHandler()
  }

  /**
   * 高亮概念火花（只高亮具体的词语）
   */
  const highlightConceptSparks = (sentenceEl: HTMLElement, concepts: ConceptSpark[]) => {
    // 获取句子的文本内容
    let html = sentenceEl.innerHTML

    // 对每个概念词语进行高亮
    concepts.forEach(concept => {
      const keyword = concept.text.trim()
      if (!keyword) return

      // 检测是否包含中文字符
      const hasChinese = /[\u4e00-\u9fa5]/.test(keyword)

      // 使用正则表达式查找并替换词语
      // 中文不使用词边界，英文使用词边界
      // ✅ 使用 'g' 标志，匹配所有出现的位置
      const regex = hasChinese
        ? new RegExp(`(${escapeRegex(keyword)})`, 'g')
        : new RegExp(`\\b(${escapeRegex(keyword)})\\b`, 'gi')

      html = html.replace(regex, (match) => {
        // 为每个概念词语创建高亮span，并附带完整的tooltip信息
        const tooltipText = `💡 ${concept.text} (重要度: ${concept.importance_score}/10)\n${concept.explanation_hint}`
        return `<span class="concept-spark-highlight"
                  data-concept="${escapeHtml(keyword)}"
                  data-importance="${concept.importance_score}"
                  data-tooltip="${escapeHtml(tooltipText)}"
                  title="${escapeHtml(concept.explanation_hint)}">
                  ${match}
                </span>`
      })
    })

    sentenceEl.innerHTML = html

    // 为每个概念高亮添加点击事件
    const conceptHighlights = sentenceEl.querySelectorAll('.concept-spark-highlight')
    conceptHighlights.forEach(el => {
      el.addEventListener('click', (e) => {
        e.stopPropagation()

        // 关闭其他所有tooltip
        document.querySelectorAll('.concept-spark-highlight.show-concept-tooltip').forEach(other => {
          if (other !== el) {
            other.classList.remove('show-concept-tooltip')
          }
        })

        // 切换当前tooltip
        el.classList.toggle('show-concept-tooltip')
      })
    })
  }

  /**
   * 转义正则表达式特殊字符
   */
  const escapeRegex = (str: string): string => {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  }

  /**
   * 转义HTML特殊字符
   */
  const escapeHtml = (str: string): string => {
    const div = document.createElement('div')
    div.textContent = str
    return div.innerHTML
  }

  /**
   * 创建火花徽章
   */
  const createSparkBadge = (group: SentenceSparks): HTMLElement => {
    const badge = document.createElement('span')
    badge.className = 'spark-badge'

    // 根据火花类型选择图标
    const hasConceptunser = group.concepts.length > 0
    const hasArgument = group.arguments.length > 0

    let icon = '💡'  // 默认概念图标
    if (hasArgument && !hasConceptunser) {
      icon = '📝'  // 论证图标
    } else if (hasArgument && hasConceptunser) {
      icon = '✨'  // 混合图标
    }

    badge.innerHTML = `
      <span class="spark-icon">${icon}</span>
    `
    // <span class="spark-count">${group.totalCount}</span>

    return badge
  }

  /**
   * 生成Tooltip内容
   */
  const generateTooltipContent = (group: SentenceSparks): string => {
    const parts: string[] = []

    // 只添加论证火花（不包括概念火花）
    if (group.arguments.length > 0) {
      const argTexts = group.arguments.map(a => {
        const icon = a.type === 'claim' ? '📝' : a.type === 'evidence' ? '📊' : '🔄'
        return `${icon} ${a.role_description}`
      })
      parts.push(...argTexts)
    }

    // 使用换行符分隔，而不是 |
    return parts.join('\n')
  }

  /**
   * 注入样式
   */
  const injectStyles = () => {
    if (document.getElementById('spark-renderer-v2-styles')) return

    const style = document.createElement('style')
    style.id = 'spark-renderer-v2-styles'
    style.textContent = `
      /* 概念火花高亮（词语级别） - 仅在hover时显示效果 */
      .concept-spark-highlight {
        position: relative;
        cursor: pointer;
        padding: 1px 3px;
        margin: 0 1px;
        border-radius: 3px;
        background-color: transparent;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
      }

      /* hover时才显示绿色下划线 */
      .concept-spark-highlight:hover {
        background-color: rgba(16, 185, 129, 0.1);
        border-bottom-color: rgba(16, 185, 129, 0.8);
      }

      /* 概念tooltip弹窗 - 使用shadcn白色背景 */
      .concept-spark-highlight::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%) translateY(-8px);
        padding: 12px 16px;
        background: hsl(var(--popover));
        color: hsl(var(--popover-foreground));
        font-size: 13px;
        line-height: 1.5;
        border-radius: 8px;
        white-space: pre-wrap;
        min-width: 250px;
        max-width: 400px;
        border: 1px solid hsl(var(--border));
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 1000;
        pointer-events: none;
      }

      /* tooltip小箭头 - 使用shadcn颜色 */
      .concept-spark-highlight::before {
        content: '';
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%) translateY(-2px);
        border: 6px solid transparent;
        border-top-color: hsl(var(--popover));
        filter: drop-shadow(0 2px 1px rgba(0, 0, 0, 0.05));
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 1001;
        pointer-events: none;
      }

      /* 显示tooltip */
      .concept-spark-highlight.show-concept-tooltip::after,
      .concept-spark-highlight.show-concept-tooltip::before {
        opacity: 1;
        visibility: visible;
      }

      .concept-spark-highlight.show-concept-tooltip {
        background-color: rgba(16, 185, 129, 0.15);
        border-bottom-color: rgba(16, 185, 129, 0.9);
      }

      /* 包含论证火花的句子（整句高亮） */
      .has-argument-sparks {
        position: relative;
        cursor: pointer !important;
        transition: all 0.2s ease;
        padding: 2px 4px;
        margin: -2px -4px;
        border-radius: 4px;
        border-bottom: 2px solid transparent;
      }

      .has-argument-sparks:hover,
      .spark-hover {
        background-color: rgba(16, 185, 129, 0.08);
        border-bottom-color: rgba(16, 185, 129, 0.6);
      }

      /* 论证火花的tooltip弹窗 */
      .has-argument-sparks::after {
        content: attr(data-spark-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%) translateY(-8px);
        padding: 12px 16px;
        background: hsl(var(--popover));
        color: hsl(var(--popover-foreground));
        font-size: 13px;
        line-height: 1.5;
        border-radius: 8px;
        white-space: pre-wrap;
        min-width: 250px;
        max-width: 400px;
        border: 1px solid hsl(var(--border));
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 1000;
        pointer-events: none;
      }

      /* 论证tooltip小箭头 */
      .has-argument-sparks::before {
        content: '';
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%) translateY(-2px);
        border: 6px solid transparent;
        border-top-color: hsl(var(--popover));
        filter: drop-shadow(0 2px 1px rgba(0, 0, 0, 0.05));
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 1001;
        pointer-events: none;
      }

      /* 显示论证tooltip */
      .has-argument-sparks.show-tooltip::after,
      .has-argument-sparks.show-tooltip::before {
        opacity: 1;
        visibility: visible;
      }

      /* 火花徽章 */
      // .spark-badge {
      //   display: inline-flex;
      //   align-items: center;
      //   gap: 2px;
      //   padding: 1px 6px;
      //   margin-left: 4px;
      //   background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      //   border-radius: 10px;
      //   font-size: 11px;
      //   font-weight: 600;
      //   color: white;
      //   box-shadow: 0 1px 3px rgba(16, 185, 129, 0.3);
      //   animation: badge-appear 0.4s ease-out;
      //   vertical-align: middle;
      //   white-space: nowrap;
      // }

      .spark-icon {
        font-size: 15px;
        line-height: 1;
      }

      .spark-count {
        line-height: 1;
      }

      @keyframes badge-appear {
        from {
          opacity: 0;
          transform: scale(0.8) translateY(-2px);
        }
        to {
          opacity: 1;
          transform: scale(1) translateY(0);
        }
      }
    `
    document.head.appendChild(style)
  }

  /**
   * 设置全局点击处理器，点击其他地方关闭tooltip
   */
  const setupGlobalClickHandler = () => {
    // 移除旧的监听器（如果存在）
    if ((window as any).__sparkTooltipClickHandler) {
      document.removeEventListener('click', (window as any).__sparkTooltipClickHandler)
    }

    // 创建新的监听器
    const handler = (e: Event) => {
      const target = e.target as HTMLElement

      // 如果点击的不是火花相关元素（概念高亮或论证句子），关闭所有tooltip
      if (!target.closest('.concept-spark-highlight') &&
          !target.closest('.has-argument-sparks') &&
          !target.closest('[data-spark-tooltip]')) {
        // 关闭所有概念tooltip
        document.querySelectorAll('.concept-spark-highlight.show-concept-tooltip').forEach(el => {
          el.classList.remove('show-concept-tooltip')
        })

        // 关闭所有句子tooltip
        document.querySelectorAll('[data-spark-tooltip].show-tooltip').forEach(el => {
          el.classList.remove('show-tooltip')
        })
      }
    }

    // 保存引用并添加监听器
    (window as any).__sparkTooltipClickHandler = handler
    document.addEventListener('click', handler)
  }

  return {
    renderSparks,
    sparkGroups
  }
}
