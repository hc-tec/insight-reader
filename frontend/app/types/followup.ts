/**
 * 追问相关类型定义
 */

export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: number
}

export interface FollowUpButton {
  id: string
  label: string
  icon: string
  category: 'example' | 'simplify' | 'compare' | 'extend'
}

export interface ButtonGenerationRequest {
  selected_text: string
  insight: string
  intent: 'explain' | 'analyze' | 'counter'
  conversation_history: Message[]
}

export interface ButtonGenerationResponse {
  buttons: FollowUpButton[]
}

export interface FollowUpRequest {
  selected_text: string
  initial_insight: string
  conversation_history: Message[]
  follow_up_question: string
  use_reasoning?: boolean
}
