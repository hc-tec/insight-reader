/**
 * 文本处理工具函数
 */
import type { Sentence } from '~/types/article'

/**
 * 简单的句子分割（MVP版本）
 * 使用正则表达式按标点符号分割
 */
export function splitIntoSentences(text: string): Sentence[] {
  // 简单的句子分割正则
  const sentenceRegex = /[^.!?。！？]+[.!?。！？]+/g
  const matches = text.match(sentenceRegex) || []

  let currentPos = 0
  return matches.map((text, index) => {
    const start = currentPos
    const end = start + text.length
    currentPos = end

    return {
      id: index,
      text: text.trim(),
      start,
      end
    }
  })
}

/**
 * 提取上下文
 * 找到选中文本所在位置，返回前后各一定范围的文本
 */
export function extractContext(
  fullText: string,
  selectedText: string,
  contextWindow: number = 200
): string {
  const startIndex = fullText.indexOf(selectedText)

  if (startIndex === -1) {
    return selectedText
  }

  const contextStart = Math.max(0, startIndex - contextWindow)
  const contextEnd = Math.min(fullText.length, startIndex + selectedText.length + contextWindow)

  return fullText.substring(contextStart, contextEnd)
}
