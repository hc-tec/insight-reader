/**
 * API 请求拦截器 Plugin
 * 自动为所有 API 请求添加 JWT Authorization header
 */

const TOKEN_KEY = 'insightreader_token'

export default defineNuxtPlugin(() => {
  // 拦截所有 $fetch 请求
  globalThis.$fetch = $fetch.create({
    onRequest({ options }) {
      // 从 localStorage 动态获取 token（每次请求都检查）
      if (process.client) {
        const token = localStorage.getItem(TOKEN_KEY)

        if (token) {
          options.headers = {
            ...options.headers,
            Authorization: `Bearer ${token}`
          }
        }
      }
    },

    onResponseError({ response }) {
      // 处理 401 未授权错误
      if (response.status === 401) {
        console.error('[API] 认证失败，token 可能已过期')
        // 清除过期的认证信息
        if (process.client) {
          localStorage.removeItem(TOKEN_KEY)
          localStorage.removeItem('insightreader_user')
        }
      }
    }
  })
})
