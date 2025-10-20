<template>
  <div ref="panelRef" class="fixed bottom-6 right-6 z-50">
    <!-- 浮动按钮 -->
    <button
      v-if="!isOpen"
      @click.stop="isOpen = true"
      class="w-12 h-12 bg-white rounded-full shadow-lg border border-gray-200 flex items-center justify-center hover:shadow-xl transition-all hover:scale-110 group"
      title="阅读设置"
    >
      <svg class="w-5 h-5 text-gray-600 group-hover:text-emerald-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
      </svg>
    </button>

    <!-- 设置面板 -->
    <Transition
      enter-active-class="transition-all duration-200"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div
        v-if="isOpen"
        class="bg-white rounded-2xl shadow-2xl border border-gray-200 w-80 overflow-hidden"
      >
        <!-- 头部 -->
        <div class="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-teal-50">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
              </div>
              <h3 class="font-semibold text-gray-900">阅读设置</h3>
            </div>
            <button
              @click.stop="isOpen = false"
              class="p-1 rounded-lg hover:bg-white/50 transition-colors"
            >
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 内容 -->
        <div class="p-6 space-y-6">
          <!-- 字体选择 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">
              字体
            </label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="font in fontOptions"
                :key="font.key"
                @click="setFontFamily(font.key as any)"
                :class="[
                  'px-3 py-2 text-sm rounded-lg border-2 transition-all',
                  currentFontKey === font.key
                    ? 'border-emerald-500 bg-emerald-50 text-emerald-700 font-semibold'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                ]"
                :style="{ fontFamily: font.family }"
              >
                {{ font.label }}
              </button>
            </div>
          </div>

          <!-- 字号选择 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">
              字号
            </label>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="size in sizeOptions"
                :key="size.key"
                @click="setFontSize(size.key as any)"
                :class="[
                  'px-3 py-2 text-sm rounded-lg border-2 transition-all',
                  currentSizeKey === size.key
                    ? 'border-emerald-500 bg-emerald-50 text-emerald-700 font-semibold'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                ]"
              >
                {{ size.label }}
              </button>
            </div>
          </div>

          <!-- 预览 -->
          <div class="pt-4 border-t border-gray-100">
            <div class="text-xs text-gray-500 mb-2">预览效果</div>
            <div
              class="p-4 bg-gray-50 rounded-lg"
              :style="{
                fontFamily: settings.fontFamily,
                fontSize: settings.fontSize,
                lineHeight: settings.lineHeight
              }"
            >
              <p class="text-gray-700">
                这是一段示例文字，用于预览当前的字体和字号设置效果。The quick brown fox jumps over the lazy dog.
              </p>
            </div>
          </div>

          <!-- 重置按钮 -->
          <button
            @click="handleReset"
            class="w-full px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            恢复默认设置
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
const {
  settings,
  setFontFamily,
  setFontSize,
  resetSettings,
  getFontOptions,
  getFontSizeOptions,
  getCurrentFontKey,
  getCurrentSizeKey
} = useReadingSettings()

const isOpen = ref(false)
const panelRef = ref<HTMLElement | null>(null)

const fontOptions = getFontOptions()
const sizeOptions = getFontSizeOptions()

const currentFontKey = computed(() => getCurrentFontKey())
const currentSizeKey = computed(() => getCurrentSizeKey())

const handleReset = () => {
  resetSettings()
}

// 点击外部关闭
const handleClickOutside = (e: MouseEvent) => {
  if (panelRef.value && !panelRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  if (process.client) {
    document.addEventListener('click', handleClickOutside)
  }
})

onUnmounted(() => {
  if (process.client) {
    document.removeEventListener('click', handleClickOutside)
  }
})
</script>
