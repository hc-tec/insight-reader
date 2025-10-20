<template>
  <Transition
    enter-active-class="transition-opacity duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-150"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click="close"
    >
      <div
        class="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden"
        @click.stop
      >
        <!-- 头部 -->
        <div class="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">自动分析设置</h3>
                <p class="text-xs text-gray-500">自定义文章加载时的自动分析行为</p>
              </div>
            </div>

            <button
              @click="close"
              class="p-2 rounded-lg hover:bg-white/50 transition-colors"
            >
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 内容 -->
        <div class="p-6 space-y-4">
          <p class="text-sm text-gray-600 mb-4">
            开启后，当您加载新文章时，系统将自动执行已启用的分析。
          </p>

          <!-- 基础分析 -->
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span class="font-medium text-gray-900">基础分析</span>
              </div>
              <p class="text-xs text-gray-500">文章基本信息和内容概览</p>
            </div>
            <Switch
              :model-value="localPreferences.auto_basic_analysis"
              @update:model-value="(val) => handleToggle('auto_basic_analysis', val)"
              :disabled="isLoading"
            />
          </div>

          <!-- 元视角分析 -->
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span class="font-medium text-gray-900">元视角分析</span>
              </div>
              <p class="text-xs text-gray-500">分析作者意图、时效性、潜在偏见和知识缺口</p>
            </div>
            <Switch
              :model-value="localPreferences.auto_meta_analysis"
              @update:model-value="(val) => handleToggle('auto_meta_analysis', val)"
              :disabled="isLoading"
            />
          </div>

          <!-- 论证透镜 -->
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
                <span class="font-medium text-gray-900">论证透镜</span>
              </div>
              <p class="text-xs text-gray-500">高亮文章中的论证结构和论点</p>
            </div>
            <Switch
              :model-value="localPreferences.auto_argument_lens"
              @update:model-value="(val) => handleToggle('auto_argument_lens', val)"
              :disabled="isLoading"
            />
          </div>

          <!-- 意图透镜 -->
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <svg class="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
                <span class="font-medium text-gray-900">意图透镜</span>
              </div>
              <p class="text-xs text-gray-500">高亮作者的立场和观点表达</p>
            </div>
            <Switch
              :model-value="localPreferences.auto_stance_lens"
              @update:model-value="(val) => handleToggle('auto_stance_lens', val)"
              :disabled="isLoading"
            />
          </div>

          <!-- 提示信息 -->
          <div class="mt-6 p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
            <div class="flex items-start gap-2">
              <svg class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-xs text-blue-700">
                这些设置将保存到您的账户中，并在所有设备上同步。
              </p>
            </div>
          </div>
        </div>

        <!-- 底部 -->
        <div class="p-6 border-t border-gray-200 bg-gray-50 flex items-center justify-end gap-3">
          <button
            @click="close"
            class="px-6 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-sm rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all shadow-md"
          >
            完成
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { useAnalysisPreferences } from '~/composables/useAnalysisPreferences'
import type { AnalysisPreferences } from '~/composables/useAnalysisPreferences'
import Switch from '~/components/ui/switch/Switch.vue'

const props = defineProps<{
  isOpen: boolean
  userId: number
}>()

const emit = defineEmits<{
  close: []
  preferencesUpdated: [preferences: AnalysisPreferences]
}>()

// 使用本地状态而不是全局状态
const localPreferences = ref<AnalysisPreferences>({
  auto_basic_analysis: true,
  auto_meta_analysis: false,
  auto_argument_lens: false,
  auto_stance_lens: false
})

const isLoading = ref(false)
const isDataLoaded = ref(false)

// 当对话框打开时获取偏好设置
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen && props.userId) {
    isLoading.value = true
    isDataLoaded.value = false
    try {
      const config = useRuntimeConfig()
      const data = await $fetch<AnalysisPreferences>(
        `${config.public.apiBase}/api/v1/preferences/analysis/${props.userId}`
      )
      localPreferences.value = data
      isDataLoaded.value = true
      console.log('✅ 已加载分析偏好设置:', data)
    } catch (error) {
      console.error('获取偏好设置失败:', error)
    } finally {
      isLoading.value = false
    }
  }
})

const close = () => {
  emit('close')
}

const handleToggle = async (key: keyof AnalysisPreferences, value: boolean) => {
  try {
    isLoading.value = true
    const config = useRuntimeConfig()
    const updated = await $fetch<AnalysisPreferences>(
      `${config.public.apiBase}/api/v1/preferences/analysis/${props.userId}`,
      {
        method: 'PUT',
        body: { [key]: value }
      }
    )
    // 保存成功后更新所有字段
    localPreferences.value = updated
    emit('preferencesUpdated', updated)
    console.log('✅ 偏好设置已更新:', key, '=', value)
  } catch (error) {
    console.error('更新偏好设置失败:', error)
    // 失败时强制刷新，保持和服务器一致
    try {
      const config = useRuntimeConfig()
      const data = await $fetch<AnalysisPreferences>(
        `${config.public.apiBase}/api/v1/preferences/analysis/${props.userId}`
      )
      localPreferences.value = data
    } catch (e) {
      console.error('重新加载失败:', e)
    }
  } finally {
    isLoading.value = false
  }
}
</script>
