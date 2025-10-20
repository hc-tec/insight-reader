<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-6">
    <Card class="w-full max-w-md">
      <CardContent class="p-8">
        <!-- 加载中 -->
        <div v-if="isProcessing" class="text-center">
          <div class="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <h2 class="text-xl font-semibold text-gray-900 mb-2">正在登录...</h2>
          <p class="text-gray-600">正在完成认证</p>
        </div>

        <!-- 成功 -->
        <div v-else-if="isSuccess" class="text-center">
          <div class="bg-green-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
            <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-900 mb-2">登录成功！</h2>
          <p class="text-gray-600 mb-6">正在跳转...</p>
        </div>

        <!-- 失败 -->
        <div v-else class="text-center">
          <div class="bg-red-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
            <svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-900 mb-2">登录失败</h2>
          <p class="text-red-600 mb-6">{{ error }}</p>
          <NuxtLink to="/login">
            <Button>返回登录</Button>
          </NuxtLink>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

const isProcessing = ref(true)
const isSuccess = ref(false)
const error = ref('')

onMounted(async () => {
  // 从 URL 获取 token
  const token = route.query.token as string

  if (!token) {
    isProcessing.value = false
    error.value = '未收到认证令牌'
    return
  }

  try {
    // 使用 token 获取用户信息
    const response = await fetch(`${config.public.apiBase}/api/v1/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('验证令牌失败')
    }

    const user = await response.json()

    // 保存到 localStorage
    if (process.client) {
      localStorage.setItem('insightreader_token', token)
      localStorage.setItem('insightreader_user', JSON.stringify(user))
    }

    isProcessing.value = false
    isSuccess.value = true

    // 延迟跳转到首页
    setTimeout(() => {
      router.push('/')
    }, 1500)

  } catch (err) {
    isProcessing.value = false
    error.value = err instanceof Error ? err.message : '认证失败'
  }
})

useHead({
  title: '登录中 - InsightReader'
})
</script>
