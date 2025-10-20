/**
 * 历史记录管理 Composable
 */
import type { HistoryItem } from '~/types/history'
import type { Intent } from '~/types/insight'

const STORAGE_KEY = 'insightreader_history'
const MAX_HISTORY_ITEMS = 100 // 最多保存100条记录

export const useHistory = () => {
  const history = useState<HistoryItem[]>('history', () => [])

  // 从 localStorage 加载历史记录
  const loadHistory = () => {
    if (process.client) {
      try {
        const stored = localStorage.getItem(STORAGE_KEY)
        if (stored) {
          history.value = JSON.parse(stored)
        }
      } catch (error) {
        console.error('加载历史记录失败:', error)
      }
    }
  }

  // 保存历史记录到 localStorage
  const saveHistory = () => {
    if (process.client) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history.value))
      } catch (error) {
        console.error('保存历史记录失败:', error)
      }
    }
  }

  // 添加新记录
  const addHistoryItem = (item: Omit<HistoryItem, 'id' | 'timestamp'>) => {
    const newItem: HistoryItem = {
      ...item,
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now()
    }

    // 添加到数组开头
    history.value.unshift(newItem)

    // 限制历史记录数量
    if (history.value.length > MAX_HISTORY_ITEMS) {
      history.value = history.value.slice(0, MAX_HISTORY_ITEMS)
    }

    saveHistory()
    return newItem
  }

  // 删除记录
  const deleteHistoryItem = (id: string) => {
    history.value = history.value.filter(item => item.id !== id)
    saveHistory()
  }

  // 清空所有历史记录
  const clearHistory = () => {
    history.value = []
    if (process.client) {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  // 搜索历史记录
  const searchHistory = (keyword: string) => {
    const lowerKeyword = keyword.toLowerCase()
    return history.value.filter(item =>
      item.selectedText.toLowerCase().includes(lowerKeyword) ||
      item.insight.toLowerCase().includes(lowerKeyword) ||
      item.articleTitle?.toLowerCase().includes(lowerKeyword)
    )
  }

  // 按意图筛选
  const filterByIntent = (intent: Intent) => {
    return history.value.filter(item => item.intent === intent)
  }

  // 获取最近N条记录
  const getRecentHistory = (limit: number = 10) => {
    return history.value.slice(0, limit)
  }

  // 初始化时加载
  onMounted(() => {
    loadHistory()
  })

  return {
    history: readonly(history),
    addHistoryItem,
    deleteHistoryItem,
    clearHistory,
    searchHistory,
    filterByIntent,
    getRecentHistory
  }
}
