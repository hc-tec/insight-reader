<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-6">
    <Card class="w-full max-w-md">
      <CardContent class="p-8">
        <!-- 加载中 -->
        <div v-if="isVerifying" class="text-center">
          <div class="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <h2 class="text-xl font-semibold text-gray-900 mb-2">验证中...</h2>
          <p class="text-gray-600">正在验证你的登录链接</p>
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
          <h2 class="text-xl font-semibold text-gray-900 mb-2">验证失败</h2>
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
const { verifyMagicLink } = useAuth()

const isVerifying = ref(true)
const isSuccess = ref(false)
const error = ref('')

onMounted(async () => {
  const token = route.query.token as string

  console.log('[Magic] 收到 token:', token ? `${token.substring(0, 20)}...` : 'null')

  if (!token) {
    isVerifying.value = false
    error.value = '缺少验证令牌'
    console.error('[Magic] 缺少 token')
    return
  }

  // 验证魔法链接
  console.log('[Magic] 开始验证魔法链接')
  const result = await verifyMagicLink(token)
  console.log('[Magic] 验证结果:', result)

  isVerifying.value = false

  if (result.success) {
    console.log('[Magic] 验证成功，准备跳转')
    isSuccess.value = true
    // 延迟跳转，让用户看到成功提示
    setTimeout(() => {
      router.push('/')
    }, 1500)
  } else {
    console.error('[Magic] 验证失败:', result.error)
    error.value = result.error || '验证链接失败或已过期'
  }
})

useHead({
  title: '验证登录 - InsightReader'
})
</script>
