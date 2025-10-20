/**
 * 收藏卡片相关类型定义
 */
import type { Intent } from './insight'

export interface InsightCardCreate {
  article_title?: string
  article_content?: string
  selected_text: string
  context?: string
  intent: Intent
  custom_question?: string
  insight: string
  model_used?: string
  tokens?: number
  tags?: string[]
}

export interface InsightCardResponse {
  id: number
  user_id: number
  article_title?: string
  selected_text: string
  context?: string
  intent: Intent
  custom_question?: string
  insight: string
  model_used?: string
  tokens?: number
  created_at: string
  tags?: string[]
}

export interface InsightCardListResponse {
  total: number
  items: InsightCardResponse[]
}
