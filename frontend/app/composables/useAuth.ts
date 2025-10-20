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
      const response = await fetch(`${config.public.apiBase}/api/v1/auth/magic-link/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || '发送魔法链接失败')
      }

      const data = await response.json()
      return { success: true, message: data.message }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '发送魔法链接失败'
      }
    }
  }

  // 验证魔法链接
  const verifyMagicLink = async (token: string) => {
    try {
      const response = await fetch(
        `${config.public.apiBase}/api/v1/auth/magic-link/verify?token=${token}`,
        {
          method: 'GET',
        }
      )

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || '验证魔法链接失败')
      }

      const data: AuthResponse = await response.json()
      saveAuth(data)

      return { success: true, user: data.user }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : '验证魔法链接失败'
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
