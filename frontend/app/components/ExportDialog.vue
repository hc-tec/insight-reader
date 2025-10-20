<template>
  <!-- 遮罩层 -->
  <Transition
    enter-active-class="transition-opacity duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-150"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="show"
      class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      @click.self="handleClose"
    >
      <!-- 对话框 -->
      <Transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-150"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="show"
          class="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden"
          @click.stop
        >
          <!-- 头部 -->
          <div class="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-emerald-50 to-white">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">导出洞察笔记</h3>
                  <p class="text-sm text-gray-500">将暂存的洞察导出为文件</p>
                </div>
              </div>
              <button
                @click="handleClose"
                class="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 内容 -->
          <div class="px-6 py-5 space-y-5">
            <!-- 统计信息 -->
            <div class="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
              <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>将导出 <strong class="text-emerald-700">{{ itemCount }}</strong> 个洞察卡片</span>
            </div>

            <!-- 格式选择 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择导出格式
              </label>
              <div class="space-y-2">
                <label
                  v-for="format in exportFormats"
                  :key="format.type"
                  class="flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-all"
                  :class="[
                    selectedFormat === format.type
                      ? 'border-emerald-500 bg-emerald-50'
                      : 'border-gray-200 hover:border-emerald-300 hover:bg-gray-50'
                  ]"
                >
                  <input
                    type="radio"
                    :value="format.type"
                    v-model="selectedFormat"
                    class="w-4 h-4 text-emerald-600 focus:ring-emerald-500"
                  />
                  <div class="flex-1">
                    <div class="font-medium text-gray-900">{{ format.label }}</div>
                    <div class="text-xs text-gray-500">
                      {{ getFormatDescription(format.type) }}
                    </div>
                  </div>
                </label>
              </div>
            </div>

            <!-- 文件名 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                文件名（可选）
              </label>
              <div class="flex items-center gap-2">
                <input
                  v-model="customFilename"
                  type="text"
                  placeholder="留空使用默认文件名"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none text-sm"
                />
                <span class="text-sm text-gray-500">.{{ getExtension(selectedFormat) }}</span>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                默认：{{ defaultFilename }}.{{ getExtension(selectedFormat) }}
              </p>
            </div>

            <!-- 导出选项 -->
            <div class="space-y-2">
              <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="includeConversations"
                  class="w-4 h-4 text-emerald-600 focus:ring-emerald-500 rounded"
                />
                <span>包含追问对话记录</span>
              </label>
              <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="includeReasoning"
                  class="w-4 h-4 text-emerald-600 focus:ring-emerald-500 rounded"
                />
                <span>包含推理过程（思维链）</span>
              </label>
            </div>
          </div>

          <!-- 底部按钮 -->
          <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
            <button
              @click="handleClose"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
            <button
              @click="handleExport"
              :disabled="exporting"
              class="px-4 py-2 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <div v-if="exporting" class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
              <span>{{ exporting ? '导出中...' : '下载' }}</span>
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import type { StashItem } from '~/types/stash'

const props = defineProps<{
  show: boolean
  items: StashItem[]
}>()

const emit = defineEmits<{
  close: []
  exported: []
}>()

const { exportInsights, exportFormats } = useExport()

// 状态
const selectedFormat = ref<'md' | 'txt'>('md')
const customFilename = ref('')
const includeConversations = ref(true)
const includeReasoning = ref(true)
const exporting = ref(false)

// 计算属性
const itemCount = computed(() => props.items.length)

const defaultFilename = computed(() => {
  const timestamp = new Date().toISOString().split('T')[0]
  const articleTitle = props.items[0]?.articleTitle || '我的阅读笔记'
  const safeTitle = articleTitle.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '_').substring(0, 30)
  return `${safeTitle}_${timestamp}`
})

// 方法
const getExtension = (format: 'md' | 'txt') => {
  return format === 'md' ? 'md' : 'txt'
}

const getFormatDescription = (format: 'md' | 'txt') => {
  const descriptions = {
    md: '保留格式，适合 Notion、Obsidian 等笔记软件',
    txt: '纯文本，适合剪贴板粘贴'
  }
  return descriptions[format]
}

const handleClose = () => {
  if (exporting.value) return
  emit('close')
}

const handleExport = async () => {
  if (exporting.value || props.items.length === 0) return

  exporting.value = true

  try {
    // 根据选项过滤数据
    const itemsToExport = props.items.map(item => ({
      ...item,
      conversationHistory: includeConversations.value ? item.conversationHistory : undefined,
      reasoning: includeReasoning.value ? item.reasoning : undefined
    }))

    // 执行导出
    exportInsights(
      itemsToExport,
      selectedFormat.value,
      customFilename.value.trim() || undefined
    )

    console.log('✅ 导出成功')

    // 延迟关闭对话框
    setTimeout(() => {
      emit('exported')
      emit('close')
      exporting.value = false
    }, 500)
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败：' + (error instanceof Error ? error.message : '未知错误'))
    exporting.value = false
  }
}

// 监听 show 变化，重置状态
watch(() => props.show, (newShow) => {
  if (newShow) {
    // 重置为默认值
    selectedFormat.value = 'md'
    customFilename.value = ''
    includeConversations.value = true
    includeReasoning.value = true
  }
})
</script>
