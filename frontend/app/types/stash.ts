/**
 * 暂存相关类型定义
 */
import type { Intent } from './insight'
import type { Message } from './followup'

export interface StashItem {
  id: string
  timestamp: number

  // 文章信息（重要！上下文）
  articleTitle?: string
  articleContent?: string  // 完整文章内容

  // 选中文本和上下文
  selectedText: string
  context: string  // 选中文本的周围上下文

  // 原始请求信息
  intent: Intent
  customQuestion?: string

  // AI 生成的洞察
  insight: string
  reasoning?: string  // 推理内容（如果有）

  // 对话历史（追问记录）
  conversationHistory?: Message[]

  // 元数据
  modelUsed?: string
  tokens?: number
}

export interface ExportFormat {
  type: 'md' | 'txt' | 'pdf'
  label: string
  mimeType: string
  extension: string
}

export interface ExportOptions {
  format: ExportFormat
  filename?: string
  includeMetadata?: boolean  // 是否包含元数据（模型、token 等）
  includeConversations?: boolean  // 是否包含追问对话
  includeReasoning?: boolean  // 是否包含推理过程
}
