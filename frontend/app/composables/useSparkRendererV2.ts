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

        // 添加火花样式
        sentenceEl.classList.add('has-sparks')

        // 创建徽章
        const badge = createSparkBadge(group)

        // 添加到句子末尾
        sentenceEl.appendChild(badge)

        // 生成tooltip内容
        const tooltipContent = generateTooltipContent(group)
        sentenceEl.setAttribute('data-spark-tooltip', tooltipContent)

        // 添加点击事件来切换tooltip显示
        sentenceEl.addEventListener('click', (e) => {
          e.stopPropagation()

          // 关闭其他所有tooltip
          document.querySelectorAll('.has-sparks.show-tooltip').forEach(el => {
            if (el !== sentenceEl) {
              el.classList.remove('show-tooltip')
            }
          })

          // 切换当前tooltip
          sentenceEl.classList.toggle('show-tooltip')
        })

        // 添加悬停效果（仅视觉反馈，不显示tooltip）
        sentenceEl.addEventListener('mouseenter', () => {
          sentenceEl.classList.add('spark-hover')
        })

        sentenceEl.addEventListener('mouseleave', () => {
          sentenceEl.classList.remove('spark-hover')
        })

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

    // 添加概念火花
    if (group.concepts.length > 0) {
      const conceptTexts = group.concepts.map(c =>
        `💡 ${c.text} (重要度: ${c.importance_score}/10) - ${c.explanation_hint}`
      )
      parts.push(...conceptTexts)
    }

    // 添加论证火花
    if (group.arguments.length > 0) {
      const argTexts = group.arguments.map(a => {
        const icon = a.type === 'claim' ? '📝' : a.type === 'evidence' ? '📊' : '🔄'
        return `${icon} ${a.role_description}`
      })
      parts.push(...argTexts)
    }

    return parts.join(' | ')
  }

  /**
   * 注入样式
   */
  const injectStyles = () => {
    if (document.getElementById('spark-renderer-v2-styles')) return

    const style = document.createElement('style')
    style.id = 'spark-renderer-v2-styles'
    style.textContent = `
      /* 包含火花的句子 */
      .has-sparks {
        position: relative;
        cursor: pointer !important;
        transition: all 0.2s ease;
        padding: 2px 4px;
        margin: -2px -4px;
        border-radius: 4px;
      }

      .has-sparks:hover,
      .spark-hover {
        background-color: rgba(16, 185, 129, 0.08);
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

      /* 点击提示 */
      .has-sparks::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #10b981, transparent);
        opacity: 0;
        transition: opacity 0.2s;
      }

      .has-sparks:hover::after {
        opacity: 0.5;
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

      // 如果点击的不是火花句子，关闭所有tooltip
      if (!target.closest('.has-sparks')) {
        document.querySelectorAll('.has-sparks.show-tooltip').forEach(el => {
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
