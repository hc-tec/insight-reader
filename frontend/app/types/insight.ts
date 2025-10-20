/**
 * 洞察相关类型定义
 */

export type Intent = 'explain' | 'analyze' | 'counter'

export interface InsightRequest {
  selected_text: string
  context: string
  intent: Intent
  custom_question?: string
  use_reasoning?: boolean
}

export interface InsightMetadata {
  model: string
  tokens: number
  duration_ms: number
}

export interface SSEEvent {
  type: 'start' | 'delta' | 'reasoning' | 'complete' | 'error'
  request_id?: string
  content?: string
  full_content?: string
  full_reasoning?: string
  metadata?: InsightMetadata
  message?: string
  code?: string
}
