/**
 * 用户认证 Composable - 无密码设计
 */
import type { User, MagicLinkRequest, AuthResponse } from '~/types/auth'

const TOKEN_KEY = 'insightreader_token'
const USER_KEY = 'insightreader_user'

export const useAuth = () => {
  const config = useRuntimeConfig()
  const token = useState<string | null>('auth-token', () => null)
  const user = useState<User | null>('auth-user', () => null)
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 从 localStorage 加载认证状态
  const loadAuth = () => {
    if (process.client) {
      try {
        const storedToken = localStorage.getItem(TOKEN_KEY)
        const storedUser = localStorage.getItem(USER_KEY)

        if (storedToken && storedUser) {
          token.value = storedToken
          user.value = JSON.parse(storedUser)
        }
      } catch (error) {
        console.error('加载认证状态失败:', error)
        clearAuth()
      }
    }
  }

  // 保存认证状态到 localStorage
  const saveAuth = (authData: AuthResponse) => {
    token.value = authData.access_token
    user.value = authData.user

    if (process.client) {
      localStorage.setItem(TOKEN_KEY, authData.access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(authData.user))
    }
  }

  // 清除认证状态
  const clearAuth = () => {
    token.value = null
    user.value = null

    if (process.client) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    }
  }

  // Google 登录
  const loginWithGoogle = () => {
    if (process.client) {
      window.location.href = `${config.public.apiBase}/api/v1/auth/google/login`
    }
  }

  // GitHub 登录
  const loginWithGithub = () => {
    if (process.client) {
      window.location.href = `${config.public.apiBase}/api/v1/auth/github/login`
    }
  }

  // 请求魔法链接
  const requestMagicLink = async (email: string) => {
    try {
      console.log('[useAuth] 请求魔法链接:', email)
      console.log('[useAuth] API Base:', config.public.apiBase)

      const data = await $fetch(`${config.public.apiBase}/api/v1/auth/magic-link/request`, {
        method: 'POST',
        body: { email }
      })

      console.log('[useAuth] 魔法链接请求成功:', data)
      return { success: true, message: data.message }
    } catch (error: any) {
      console.error('[useAuth] 魔法链接请求失败:', error)
      return {
        success: false,
        error: error?.data?.detail || error?.message || '发送魔法链接失败'
      }
    }
  }

  // 验证魔法链接
  const verifyMagicLink = async (token: string) => {
    try {
      console.log('[useAuth] 验证魔法链接, token:', token.substring(0, 20) + '...')
      console.log('[useAuth] 验证 URL:', `${config.public.apiBase}/api/v1/auth/magic-link/verify`)

      const data = await $fetch<AuthResponse>(
        `${config.public.apiBase}/api/v1/auth/magic-link/verify?token=${token}`
      )

      console.log('[useAuth] 验证成功，用户信息:', data.user)
      saveAuth(data)

      return { success: true, user: data.user }
    } catch (error: any) {
      console.error('[useAuth] 验证失败:', error)
      return {
        success: false,
        error: error?.data?.detail || error?.message || '验证魔法链接失败或已过期'
      }
    }
  }

  // 处理 OAuth 回调（通用）
  const handleOAuthCallback = (authData: AuthResponse) => {
    saveAuth(authData)
  }

  // 登出
  const logout = () => {
    clearAuth()
    // 可以导航到首页
    if (process.client) {
      window.location.href = '/'
    }
  }

  // 获取认证头
  const getAuthHeaders = () => {
    if (!token.value) {
      throw new Error('未登录')
    }

    return {
      'Authorization': `Bearer ${token.value}`,
      'Content-Type': 'application/json'
    }
  }

  // 初始化时加载
  onMounted(() => {
    loadAuth()
  })

  return {
    token: readonly(token),
    user: readonly(user),
    isAuthenticated,
    loginWithGoogle,
    loginWithGithub,
    requestMagicLink,
    verifyMagicLink,
    handleOAuthCallback,
    logout,
    getAuthHeaders
  }
}
