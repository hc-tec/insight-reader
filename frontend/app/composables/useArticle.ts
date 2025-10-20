/**
 * 文章状态管理 Composable
 */
import type { Article, Sentence } from '~/types/article'
import { splitIntoSentences } from '~/utils/textParser'

export const useArticle = () => {
  const content = useState<string>('article-content', () => '')
  const title = useState<string>('article-title', () => '')
  const sentences = useState<Sentence[]>('article-sentences', () => [])
  const isReading = useState<boolean>('is-reading', () => false)

  const hasContent = computed(() => content.value.trim().length > 0)
  const sentenceCount = computed(() => sentences.value.length)
  const characterCount = computed(() => content.value.length)

  const setArticle = (articleContent: string, articleTitle?: string) => {
    content.value = articleContent
    title.value = articleTitle || extractTitle(articleContent)

    // 句子分割
    sentences.value = splitIntoSentences(articleContent)
    isReading.value = true
  }

  const clearArticle = () => {
    content.value = ''
    title.value = ''
    sentences.value = []
    isReading.value = false
  }

  const extractTitle = (text: string): string => {
    // 取前50个字符作为标题
    const firstLine = text.split('\n')[0]
    return firstLine.substring(0, 50) + (firstLine.length > 50 ? '...' : '')
  }

  return {
    content,
    title,
    sentences,
    isReading,
    hasContent,
    sentenceCount,
    characterCount,
    setArticle,
    clearArticle
  }
}
