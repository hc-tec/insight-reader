<template>
  <header class="h-16 border-b border-gray-200/50 bg-white/70 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-40 shadow-sm/50">
    <div class="flex items-center gap-4">
      <!-- 返回按钮 -->
      <Transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 -translate-x-2"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition-all duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <Button
          v-if="isReading"
          variant="ghost"
          size="sm"
          @click="handleBack"
          class="hover:bg-gray-100 transition-colors"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </Button>
      </Transition>

      <!-- Logo -->
      <button @click="goHome" class="flex items-center gap-2.5 group">
        <div class="w-9 h-9 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg transition-all group-hover:scale-105">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-bold bg-gradient-to-r from-slate-800 to-zinc-700 bg-clip-text text-transparent">
            InsightReader
          </h1>
          <p class="text-[10px] text-gray-500 -mt-1">深度阅读助手</p>
        </div>
      </button>
    </div>

    <div class="flex items-center gap-3">
      <!-- 推理模式开关 -->
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50/80 border border-gray-200/50">
        <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <span class="text-xs font-medium text-gray-700">推理模式</span>
        <button
          @click="toggleReasoning"
          :class="[
            'relative inline-flex h-5 w-9 items-center rounded-full transition-colors',
            useReasoning ? 'bg-emerald-500' : 'bg-gray-300'
          ]"
        >
          <span
            :class="[
              'inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm',
              useReasoning ? 'translate-x-5' : 'translate-x-0.5'
            ]"
          ></span>
        </button>
      </div>

      <!-- 分析设置按钮 -->
      <button
        v-if="isAuthenticated"
        @click="$emit('open-settings')"
        class="p-2 rounded-lg hover:bg-gray-100 transition-colors group"
        title="分析设置"
      >
        <svg class="w-5 h-5 text-gray-600 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>

      <!-- 已登录 -->
      <div v-if="isAuthenticated" class="flex items-center gap-2">
        <!-- 仪表盘按钮 -->
        <NuxtLink to="/dashboard">
          <Button variant="ghost" size="sm" class="hover:bg-gray-100 transition-colors group">
            <svg class="mr-2 h-4 w-4 group-hover:text-emerald-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            仪表盘
          </Button>
        </NuxtLink>

        <!-- 历史按钮 -->
        <NuxtLink to="/history">
          <Button variant="ghost" size="sm" class="hover:bg-gray-100 transition-colors group">
            <svg class="mr-2 h-4 w-4 group-hover:text-purple-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            阅读历史
          </Button>
        </NuxtLink>

        <!-- 收藏按钮 -->
        <NuxtLink to="/collections">
          <Button variant="ghost" size="sm" class="hover:bg-gray-100 transition-colors group">
            <svg class="mr-2 h-4 w-4 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
            我的收藏
          </Button>
        </NuxtLink>

        <!-- 用户菜单 -->
        <div class="relative">
          <Button
            variant="ghost"
            size="sm"
            @click="showUserMenu = !showUserMenu"
            class="flex items-center gap-2 hover:bg-gray-100 transition-colors pl-2 pr-3"
          >
            <!-- 头像 -->
            <div v-if="user?.avatar_url" class="w-8 h-8 rounded-full overflow-hidden border-2 border-gray-200">
              <img :src="user.avatar_url" :alt="user.username || user.email" class="w-full h-full object-cover" />
            </div>
            <div v-else class="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white text-sm font-semibold shadow-sm">
              {{ userInitial }}
            </div>
            <!-- 用户名 -->
            <span class="text-sm font-medium hidden md:block">{{ displayName }}</span>
            <!-- 下拉图标 -->
            <svg :class="['w-4 h-4 transition-transform', showUserMenu && 'rotate-180']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </Button>

          <!-- 用户菜单下拉 -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-1"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="showUserMenu"
              class="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-2xl border border-gray-100 z-50 overflow-hidden"
            >
              <!-- 用户信息卡片 -->
              <div class="p-4 bg-gradient-to-br from-slate-50 to-zinc-50 border-b border-gray-200">
                <div class="flex items-center gap-3">
                  <div v-if="user?.avatar_url" class="w-12 h-12 rounded-full overflow-hidden border-2 border-white shadow-sm">
                    <img :src="user.avatar_url" :alt="user.username || user.email" class="w-full h-full object-cover" />
                  </div>
                  <div v-else class="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-semibold shadow-sm">
                    {{ userInitial }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-gray-900 truncate">{{ displayName }}</p>
                    <p class="text-xs text-gray-600 truncate">{{ user?.email }}</p>
                    <div v-if="user?.oauth_provider" class="flex items-center gap-1 mt-1">
                      <span class="text-[10px] px-2 py-0.5 bg-white/60 rounded-full text-gray-600 capitalize">
                        {{ user.oauth_provider }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 菜单项 -->
              <div class="py-2">
                <NuxtLink to="/dashboard" @click="showUserMenu = false">
                  <button class="w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 transition-colors flex items-center gap-3">
                    <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <span>仪表盘</span>
                  </button>
                </NuxtLink>

                <NuxtLink to="/history" @click="showUserMenu = false">
                  <button class="w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 transition-colors flex items-center gap-3">
                    <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    <span>阅读历史</span>
                  </button>
                </NuxtLink>

                <NuxtLink to="/collections" @click="showUserMenu = false">
                  <button class="w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 transition-colors flex items-center gap-3">
                    <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                    </svg>
                    <span>我的收藏</span>
                  </button>
                </NuxtLink>

                <button
                  @click="handleLogout"
                  class="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors flex items-center gap-3 border-t border-gray-100"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>退出登录</span>
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <!-- 未登录 -->
      <div v-else class="flex items-center gap-2">
        <NuxtLink to="/login">
          <Button variant="ghost" size="sm" class="hover:bg-gray-100 transition-colors">
            登录
          </Button>
        </NuxtLink>
        <NuxtLink to="/login">
          <Button size="sm" class="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 shadow-sm hover:shadow-md transition-all">
            开始使用
          </Button>
        </NuxtLink>
      </div>
    </div>

    <!-- 点击外部关闭菜单 -->
    <div
      v-if="showUserMenu"
      class="fixed inset-0 z-40"
      @click="showUserMenu = false"
    />
  </header>
</template>

<script setup lang="ts">
const router = useRouter()
const { isReading, clearArticle } = useArticle()
const { isAuthenticated, user, logout } = useAuth()

const emit = defineEmits<{
  'open-settings': []
}>()

const showUserMenu = ref(false)

// 推理模式状态（使用 useState 全局共享）
const useReasoning = useState('use-reasoning', () => false)

const toggleReasoning = () => {
  useReasoning.value = !useReasoning.value
}

const userInitial = computed(() => {
  if (user.value?.username) {
    return user.value.username.charAt(0).toUpperCase()
  }
  if (user.value?.email) {
    return user.value.email.charAt(0).toUpperCase()
  }
  return 'U'
})

const displayName = computed(() => {
  return user.value?.username || user.value?.email?.split('@')[0] || '用户'
})

const handleBack = () => {
  clearArticle()
}

const goHome = () => {
  router.push('/')
}

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    logout()
    showUserMenu.value = false
  }
}

// 点击外部关闭菜单（键盘事件）
onMounted(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && showUserMenu.value) {
      showUserMenu.value = false
    }
  }
  window.addEventListener('keydown', handleEscape)
  onUnmounted(() => {
    window.removeEventListener('keydown', handleEscape)
  })
})
</script>
