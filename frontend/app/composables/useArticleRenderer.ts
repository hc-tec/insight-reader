/**
 * 文章渲染引擎 Composable
 *
 * 负责将文章内容拆分为句子和段落，并渲染为带句子 ID 的 HTML
 * 支持 Markdown 和纯文本
 *
 * 设计原则：
 * 1. 句子 ID 全局连续（跨段落）
 * 2. 保留段落结构
 * 3. 前后端使用相同的拆分逻辑
 */

import { marked } from 'marked'

/**
 * 句子数据结构
 */
export interface Sentence {
  index: number        // 全局句子索引
  text: string         // 句子文本��包含标点）
  paragraphIndex: number  // 所属段落索引
}

/**
 * 段落数据结构
 */
export interface Paragraph {
  index: number        // 段落索引
  sentences: Sentence[] // 该段落的句子列表
}

export const useArticleRenderer = () => {
  /**
   * 智能拆分句子
   *
   * 规则：
   * - 中文：按 。！？…\n 拆分
   * - 英文：按 .!?\n 拆分，处理常见缩写
   * - 保留标点符号
   * - 过滤空句子
   *
   * @param text 纯文本（不包含 HTML 标签）
   * @returns 句子数组
   */
  const splitIntoSentences = (text: string): string[] => {
    // 预处理：统一换行符
    text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n')

    // 句子分隔符（中文和英文）
    // 注意：\n 也作为句子分隔符（段落内的换行）
    const sentenceDelimiters = /([。！？!?.…]+[\s\n]|[\n])/g

    // 拆分并保留分隔符
    const parts = text.split(sentenceDelimiters)

    const sentences: string[] = []
    let currentSentence = ''

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i]

      if (!part) continue

      // 如果是分隔符
      if (sentenceDelimiters.test(part)) {
        currentSentence += part

        // 检查是否是真正的句子结束（排除缩写等）
        if (isValidSentenceEnd(currentSentence, parts[i + 1])) {
          const trimmed = currentSentence.trim()
          if (trimmed.length > 0) {
            sentences.push(trimmed)
            currentSentence = ''
          }
        }
      } else {
        currentSentence += part
      }
    }

    // 处理最后一个句子
    const trimmed = currentSentence.trim()
    if (trimmed.length > 0) {
      sentences.push(trimmed)
    }

    return sentences.filter(s => s.length > 0)
  }

  /**
   * 判断是否为有效的句子结束
   *
   * 排除常见缩写：
   * - Mr. Mrs. Dr. Prof. etc.
   * - U.S. U.K. etc.
   */
  const isValidSentenceEnd = (sentence: string, nextPart?: string): boolean => {
    // 如果句子以换行结束，一定是句子结束
    if (sentence.endsWith('\n')) return true

    // 常见英文缩写
    const abbreviations = [
      'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Sr.', 'Jr.',
      'etc.', 'vs.', 'e.g.', 'i.e.', 'U.S.', 'U.K.',
      'Inc.', 'Ltd.', 'Co.', 'Corp.'
    ]

    for (const abbr of abbreviations) {
      if (sentence.trim().endsWith(abbr)) {
        // 如果下一个部分以小写字母开头，说明不是句子结束
        if (nextPart && /^[a-z]/.test(nextPart.trim())) {
          return false
        }
      }
    }

    return true
  }

  /**
   * 将纯文本拆分为段落和句子
   *
   * @param text 纯文本
   * @returns 段落数组，每个段落包含句子列表
   */
  const splitIntoParagraphs = (text: string): Paragraph[] => {
    // 按双换行拆分段落
    const rawParagraphs = text.split(/\n\n+/).filter(p => p.trim().length > 0)

    const paragraphs: Paragraph[] = []
    let globalSentenceIndex = 0

    rawParagraphs.forEach((paragraphText, paragraphIndex) => {
      // 拆分该段落的句子
      const sentenceTexts = splitIntoSentences(paragraphText)

      const sentences: Sentence[] = sentenceTexts.map(sentenceText => {
        const sentence: Sentence = {
          index: globalSentenceIndex++,
          text: sentenceText,
          paragraphIndex
        }
        return sentence
      })

      paragraphs.push({
        index: paragraphIndex,
        sentences
      })
    })

    return paragraphs
  }

  /**
   * 将 Markdown 渲染为 HTML，然后提取纯文本进行拆分
   *
   * 策略：
   * 1. 先用 marked 渲染 Markdown
   * 2. 提取渲染后的纯文本
   * 3. 按段落和句子拆分
   * 4. 将句子 ID 插入到原始 HTML 中
   *
   * 注意：这是简化版本，复杂的 Markdown 可能需要更精细的处理
   */
  const renderMarkdownWithSentenceIds = (markdown: string): string => {
    // 1. 渲染 Markdown
    const html = marked(markdown, {
      breaks: true,
      gfm: true
    }) as string

    // 2. 提取纯文本（移除 HTML 标签）
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = html
    const plainText = tempDiv.textContent || ''

    // 3. 拆分段落和句子
    const paragraphs = splitIntoParagraphs(plainText)

    // 4. 构建带句子 ID 的 HTML
    // 简化版本：直接按段落和句子重新构建 HTML
    let resultHtml = ''

    paragraphs.forEach(paragraph => {
      resultHtml += `<p data-paragraph-index="${paragraph.index}" class="article-paragraph">`

      paragraph.sentences.forEach(sentence => {
        resultHtml += `<span id="sentence-${sentence.index}" data-sentence-index="${sentence.index}" class="article-sentence">${escapeHtml(sentence.text)}</span>`
      })

      resultHtml += '</p>'
    })

    return resultHtml
  }

  /**
   * 将纯文本渲染为带句子 ID 的 HTML
   *
   * @param text 纯文本
   * @returns 带句子 ID 的 HTML
   */
  const renderPlainTextWithSentenceIds = (text: string): string => {
    const paragraphs = splitIntoParagraphs(text)

    let html = ''

    paragraphs.forEach(paragraph => {
      html += `<p data-paragraph-index="${paragraph.index}" class="article-paragraph">`

      paragraph.sentences.forEach(sentence => {
        html += `<span id="sentence-${sentence.index}" data-sentence-index="${sentence.index}" class="article-sentence">${escapeHtml(sentence.text)}</span>`
      })

      html += '</p>'
    })

    return html
  }

  /**
   * 检测内容是否为 Markdown
   */
  const isMarkdown = (text: string): boolean => {
    const markdownPatterns = [
      /^#{1,6}\s/m,           // 标题 # ## ###
      /\*\*.*\*\*/,           // 粗体 **text**
      /\*.*\*/,               // 斜体 *text*
      /\[.*\]\(.*\)/,         // 链接 [text](url)
      /```[\s\S]*```/,        // 代码块
      /^[-*+]\s/m,            // 无序列表
      /^\d+\.\s/m,            // 有序列表
      /^>\s/m,                // 引���
      /!\[.*\]\(.*\)/,        // 图片
    ]

    return markdownPatterns.some(pattern => pattern.test(text))
  }

  /**
   * 主渲染函数：自动检测格式并渲染
   *
   * @param content 文章内容（Markdown 或纯文本）
   * @returns 带句子 ID 的 HTML
   */
  const renderArticleWithSentenceIds = (content: string): string => {
    if (!content) return ''

    // 检测是否为 Markdown
    if (isMarkdown(content)) {
      console.log('📝 检测到 Markdown 格式，使用 Markdown 渲染')
      return renderMarkdownWithSentenceIds(content)
    } else {
      console.log('📝 使用纯文本渲染')
      return renderPlainTextWithSentenceIds(content)
    }
  }

  /**
   * HTML 转义
   */
  const escapeHtml = (text: string): string => {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  /**
   * 根据句子 ID 获取句子元素
   */
  const getSentenceElement = (sentenceIndex: number): HTMLElement | null => {
    return document.getElementById(`sentence-${sentenceIndex}`)
  }

  /**
   * 获取文章的句子数据（用于后端分析）
   *
   * @param content 文章内容
   * @returns 段落和句子数据
   */
  const extractSentenceData = (content: string): Paragraph[] => {
    // 如果是 Markdown，先提取纯文本
    let plainText = content

    if (isMarkdown(content)) {
      const html = marked(content, { breaks: true, gfm: true }) as string
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = html
      plainText = tempDiv.textContent || ''
    }

    return splitIntoParagraphs(plainText)
  }

  /**
   * 清理文章内容（移除已有的句子 ID）
   */
  const cleanContent = (html: string): string => {
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = html

    // 移除所有 sentence-* ID
    const sentences = tempDiv.querySelectorAll('[id^="sentence-"]')
    sentences.forEach(el => {
      const text = el.textContent || ''
      el.replaceWith(document.createTextNode(text))
    })

    return tempDiv.textContent || ''
  }

  /**
   * 使用后端提供的分句结果重新渲染文章
   *
   * @param sentences 后端分析返回的句子数组
   * @returns 带句子 ID 的 HTML
   */
  const renderWithBackendSentences = (sentences: string[]): string => {
    if (!sentences || sentences.length === 0) return ''

    console.log(`📝 使用后端分句结果重新渲染，共 ${sentences.length} 个句子`)

    // 智能段落分组：根据句子内容推断段落
    // 简化版：每10个句子或遇到明显段落标记时换段
    let html = ''
    let currentParagraph: string[] = []
    let paragraphIndex = 0

    const flushParagraph = () => {
      if (currentParagraph.length > 0) {
        html += `<p data-paragraph-index="${paragraphIndex}" class="article-paragraph">`
        html += currentParagraph.join('')
        html += '</p>'
        currentParagraph = []
        paragraphIndex++
      }
    }

    sentences.forEach((sentenceText, index) => {
      // 添加句子 span
      const sentenceHtml = `<span id="sentence-${index}" data-sentence-index="${index}" class="article-sentence">${escapeHtml(sentenceText)} </span>`
      currentParagraph.push(sentenceHtml)

      // 每10个句子换一段（简化版逻辑）
      // 更好的方式是后端提供段落信息
      if ((index + 1) % 10 === 0) {
        flushParagraph()
      }
    })

    // 处理最后一个段落
    flushParagraph()

    return html
  }

  return {
    // 主要方法
    renderArticleWithSentenceIds,
    extractSentenceData,
    renderWithBackendSentences,  // 新增方法

    // 辅助方法
    splitIntoSentences,
    splitIntoParagraphs,
    getSentenceElement,
    cleanContent,
    isMarkdown,

    // 工具方法
    escapeHtml
  }
}
