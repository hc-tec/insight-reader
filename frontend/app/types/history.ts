/**
 * 历史记录相关类型定义
 */
import type { Intent } from './insight'

export interface HistoryItem {
  id: string
  timestamp: number
  selectedText: string
  context: string
  intent: Intent
  customQuestion?: string
  insight: string
  articleTitle?: string
}

export interface HistoryFilter {
  intent?: Intent
  dateRange?: {
    start: number
    end: number
  }
  searchKeyword?: string
}
