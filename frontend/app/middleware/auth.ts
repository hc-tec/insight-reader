/**
 * 认证中间件
 * 检查用户是否已登录，如果未登录则重定向到登录页
 */
export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth()

  // 如果未登录，重定向到登录页
  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
