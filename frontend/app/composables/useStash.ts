/**
 * 暂存管理 Composable
 */
import type { StashItem } from '~/types/stash'
import type { Intent } from '~/types/insight'
import type { Message } from '~/types/followup'

const STORAGE_KEY = 'insightreader_stash'
const MAX_STASH_ITEMS = 50 // 最多暂存 50 个洞察

export const useStash = () => {
  const stashItems = useState<StashItem[]>('stash-items', () => [])
  const { title: articleTitle, content: articleContent } = useArticle()

  // 添加到暂存
  const addToStash = (item: {
    selectedText: string
    context: string
    intent: Intent
    customQuestion?: string
    insight: string
    reasoning?: string
    conversationHistory?: Message[]
    modelUsed?: string
    tokens?: number
  }) => {
    const newItem: StashItem = {
      id: `stash_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),

      // 文章信息（包含完整原文）
      articleTitle: articleTitle.value,
      articleContent: articleContent.value,

      // 选中文本和上下文
      selectedText: item.selectedText,
      context: item.context,

      // 原始请求信息
      intent: item.intent,
      customQuestion: item.customQuestion,

      // AI 生成的洞察
      insight: item.insight,
      reasoning: item.reasoning,

      // 对话历史（追问记录）
      conversationHistory: item.conversationHistory ? [...item.conversationHistory] : undefined,

      // 元数据
      modelUsed: item.modelUsed,
      tokens: item.tokens
    }

    stashItems.value.unshift(newItem) // 添加到开头

    // 限制数量
    if (stashItems.value.length > MAX_STASH_ITEMS) {
      stashItems.value = stashItems.value.slice(0, MAX_STASH_ITEMS)
    }

    saveToStorage()
    console.log('📌 已暂存洞察:', newItem.selectedText.substring(0, 20), '...')

    return newItem
  }

  // 从暂存移除
  const removeFromStash = (id: string) => {
    const index = stashItems.value.findIndex(item => item.id === id)
    if (index > -1) {
      const removed = stashItems.value.splice(index, 1)[0]
      saveToStorage()
      console.log('🗑️ 已移除暂存:', removed.selectedText.substring(0, 20), '...')
    }
  }

  // 清空暂存
  const clearStash = () => {
    const count = stashItems.value.length
    stashItems.value = []
    if (process.client) {
      localStorage.removeItem(STORAGE_KEY)
    }
    console.log('🗑️ 已清空暂存:', count, '个洞察')
  }

  // 调整顺序
  const reorderStash = (fromIndex: number, toIndex: number) => {
    const item = stashItems.value.splice(fromIndex, 1)[0]
    stashItems.value.splice(toIndex, 0, item)
    saveToStorage()
  }

  // 检查是否已暂存（基于选中文本和洞察内容）
  const isStashed = (selectedText: string, insight: string): boolean => {
    return stashItems.value.some(
      item => item.selectedText === selectedText && item.insight === insight
    )
  }

  // 从 localStorage 加载
  const loadFromStorage = () => {
    if (process.client) {
      try {
        const stored = localStorage.getItem(STORAGE_KEY)
        if (stored) {
          stashItems.value = JSON.parse(stored)
          console.log('📦 从存储加载暂存:', stashItems.value.length, '个洞察')
        }
      } catch (error) {
        console.error('加载暂存失败:', error)
      }
    }
  }

  // 保存到 localStorage
  const saveToStorage = () => {
    if (process.client) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(stashItems.value))
      } catch (error) {
        console.error('保存暂存失败:', error)
      }
    }
  }

  // 获取暂存统计
  const getStats = () => {
    const totalWords = stashItems.value.reduce(
      (sum, item) => sum + item.insight.length + (item.reasoning?.length || 0),
      0
    )
    const totalConversations = stashItems.value.reduce(
      (sum, item) => sum + (item.conversationHistory?.length || 0),
      0
    )

    return {
      count: stashItems.value.length,
      totalWords,
      totalConversations,
      hasConversations: totalConversations > 0,
      hasReasoning: stashItems.value.some(item => item.reasoning)
    }
  }

  // 初始化时加载
  onMounted(() => {
    loadFromStorage()
  })

  return {
    stashItems: readonly(stashItems),
    addToStash,
    removeFromStash,
    clearStash,
    reorderStash,
    isStashed,
    getStats
  }
}
