/**
 * 认证相关类型定义 - 无密码设计
 */

export interface User {
  id: number
  email: string
  username?: string
  avatar_url?: string
  oauth_provider?: string
  created_at: string
  last_login: string
  is_active: boolean
}

export interface MagicLinkRequest {
  email: string
}

export interface MagicLinkResponse {
  message: string
  email: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}
