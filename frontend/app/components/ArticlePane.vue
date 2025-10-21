<template>
  <div class="max-w-3xl mx-auto px-12 py-16">
    <!-- 文章头部 -->
    <div v-if="title" class="mb-16 animate-fade-in">
      <!-- Badge -->
      <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100 mb-6">
        <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
        <span class="text-xs font-medium text-emerald-700">正在阅读</span>
      </div>

      <h1
        class="text-5xl font-bold text-gray-900 leading-tight mb-6 tracking-tight"
        :style="{ fontFamily: readingSettings.fontFamily }"
      >
        {{ title }}
      </h1>

      <div class="flex items-center justify-between">
        <div class="flex items-center gap-6 text-sm text-gray-500">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <span class="font-medium">深度阅读</span>
        </div>

        <div class="flex items-center gap-2">
          <div class="w-px h-4 bg-gray-300"></div>
        </div>

        <div class="flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{{ wordCount }} 字</span>
        </div>

        <div class="flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>约 {{ Math.ceil(wordCount / 400) }} 分钟</span>
        </div>
      </div>

      <!-- 阅读设置按钮 -->
      <button
        @click="showSettings = !showSettings"
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-gray-100 transition-colors group text-sm text-gray-600"
        title="阅读设置"
      >
        <svg class="w-4 h-4 group-hover:text-emerald-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
        <span class="group-hover:text-emerald-600 transition-colors">阅读设置</span>
      </button>
    </div>

      <div class="mt-6 h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent"></div>

      <!-- 阅读设置面板 -->
      <Transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showSettings" class="mt-6 bg-white rounded-xl border border-gray-200 shadow-lg p-6">
          <div class="space-y-5">
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

            <!-- 单句成行开关 -->
            <div>
              <label class="flex items-center justify-between cursor-pointer group">
                <div class="flex items-center gap-3">
                  <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                  <div>
                    <span class="text-sm font-medium text-gray-700">单句成行</span>
                    <p class="text-xs text-gray-500">每个句子独立显示为一行</p>
                  </div>
                </div>
                <div class="relative">
                  <input
                    type="checkbox"
                    :checked="readingSettings.singleSentencePerLine"
                    @change="toggleSingleSentencePerLine"
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-emerald-600 transition-colors"></div>
                  <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                </div>
              </label>
            </div>

            <!-- 操作按钮 -->
            <div class="flex items-center justify-between pt-2">
              <button
                @click="resetSettings"
                class="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                恢复默认
              </button>
              <button
                @click="showSettings = false"
                class="px-4 py-2 bg-emerald-600 text-white text-sm rounded-lg hover:bg-emerald-700 transition-colors"
              >
                完成
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 文章内容 -->
    <article class="max-w-none animate-fade-in" style="animation-delay: 0.1s;">
      <div
        id="article-content-container"
        ref="articleContentRef"
        :class="[
          'article-content select-text',
          { 'single-sentence-per-line': readingSettings.singleSentencePerLine }
        ]"
        :style="{
          fontFamily: readingSettings.fontFamily,
          fontSize: readingSettings.fontSize,
          lineHeight: readingSettings.lineHeight,
          textRendering: 'optimizeLegibility',
          WebkitFontSmoothing: 'antialiased'
        }"
        @mouseup="handleMouseUp"
        v-html="renderedContent"
      >
      </div>
    </article>

    <!-- 底部提示 -->
    <div class="mt-20 pt-8 animate-fade-in" style="animation-delay: 0.2s;">
      <div class="relative group">
        <div class="absolute -inset-4 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl"></div>

        <div class="relative flex flex-col items-center gap-4 p-8 rounded-2xl bg-gradient-to-br from-white to-gray-50 border border-gray-100 shadow-sm">
          <div class="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center">
            <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>

          <div class="text-center">
            <p class="text-sm font-semibold text-gray-900 mb-1">开始提问吧！</p>
            <p class="text-sm text-gray-600">选中任意文字，让 AI 帮你深度理解内容</p>
          </div>

          <div class="flex items-center gap-2 text-xs text-gray-500">
            <kbd class="px-2 py-1 bg-white border border-gray-200 rounded shadow-sm font-medium text-gray-600">Shift</kbd>
            <span>+</span>
            <span>鼠标选择</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  content: string
  title?: string
}>()

const { handleSelection } = useSelection()
const { renderArticleWithSentenceIds } = useArticleRenderer()
const {
  settings: readingSettings,
  setFontFamily,
  setFontSize,
  resetSettings,
  getFontOptions,
  getFontSizeOptions,
  getCurrentFontKey,
  getCurrentSizeKey,
  toggleSingleSentencePerLine
} = useReadingSettings()

// DOM 引用
const articleContentRef = ref<HTMLElement | null>(null)

// 设置面板显示状态
const showSettings = ref(false)

// 字体和字号选项
const fontOptions = getFontOptions()
const sizeOptions = getFontSizeOptions()

// 当前选中的选项
const currentFontKey = computed(() => getCurrentFontKey())
const currentSizeKey = computed(() => getCurrentSizeKey())

// 渲染内容：使用统一的句子级渲染引擎
const renderedContent = computed(() => {
  if (!props.content) return ''

  // 使用 renderArticleWithSentenceIds 进行渲染
  // 它会自动检测 Markdown/纯文本，并添加句子 ID
  return renderArticleWithSentenceIds(props.content)
})

// 提取纯文本内容（用于字数统计）
const plainTextContent = computed(() => {
  // 直接使用原始content，因为渲染器只是添加了HTML结构
  return props.content
})

// 计算字数
const wordCount = computed(() => {
  return plainTextContent.value.replace(/\s/g, '').length
})

const handleMouseUp = () => {
  // 延迟执行，确保选中文本已经生效
  setTimeout(() => {
    handleSelection()
  }, 10)
}

// 注意：火花分析现在由统一深度分析引擎（Unified Deep Analysis Engine）处理
// 分析在后台异步完成，完成后会通过 SSE 通知前端，火花会自动渲染
// 详见: useAnalysisNotifications.ts 和 useSparkRenderer.ts
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out forwards;
  opacity: 0;
}

/* 选中文本的高亮样式 */
::selection {
  background-color: rgba(16, 185, 129, 0.2);
  color: inherit;
}

::-moz-selection {
  background-color: rgba(16, 185, 129, 0.2);
  color: inherit;
}

/* 文章内容基础样式 */
.article-content {
  /* font-size 和 line-height 现在由阅读设置动态控制 */
  /* font-family 也由阅读设置动态控制 */
  color: #1f2937;
}

/* Markdown 内容样式 - 使用 :deep() 确保样式应用到 v-html 渲染的内容 */
.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3),
.article-content :deep(h4),
.article-content :deep(h5),
.article-content :deep(h6) {
  font-weight: 600;
  margin-top: 1.5em;
  margin-bottom: 0.75em;
  color: #111827;
  line-height: 1.3;
}

.article-content :deep(h1) {
  font-size: 2em;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.3em;
  margin-top: 0;
}

.article-content :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.2em;
}

.article-content :deep(h3) {
  font-size: 1.25em;
}

.article-content :deep(h4) {
  font-size: 1.1em;
}

.article-content :deep(p) {
  margin-top: 0;
  margin-bottom: 1em;
  line-height: 2;
  text-indent: 2em;
}

/* 单句成行模式 */
.single-sentence-per-line :deep(.article-sentence) {
  display: block;
  margin-bottom: 0.8em;
  text-indent: 0;
}

.single-sentence-per-line :deep(p) {
  text-indent: 0;
}

.article-content :deep(a) {
  color: #10b981;
  text-decoration: underline;
  transition: color 0.2s;
}

.article-content :deep(a:hover) {
  color: #059669;
}

.article-content :deep(strong) {
  font-weight: 700;
  color: #111827;
}

.article-content :deep(em) {
  font-style: italic;
}

.article-content :deep(code) {
  background: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-size: 0.875em;
  color: #e11d48;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.article-content :deep(pre) {
  background: #1f2937;
  color: #f3f4f6;
  padding: 1em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin: 1.5em 0;
  line-height: 1.6;
}

.article-content :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
  font-size: 0.95em;
}

.article-content :deep(blockquote) {
  border-left: 4px solid #10b981;
  padding-left: 1em;
  margin: 1.5em 0;
  color: #6b7280;
  font-style: italic;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.article-content :deep(li) {
  margin: 0.5em 0;
}

.article-content :deep(ul) {
  list-style-type: disc;
}

.article-content :deep(ol) {
  list-style-type: decimal;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5em;
  margin: 1.5em 0;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.75em;
  text-align: left;
}

.article-content :deep(th) {
  background: #f9fafb;
  font-weight: 600;
}

.article-content :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 2em 0;
}

/* 元视角思维透镜高亮样式 */
.article-content :deep(.meta-view-highlight) {
  padding: 0.1em 0.2em;
  border-radius: 0.25em;
  transition: all 0.2s ease;
  cursor: help;
  position: relative;
}

.article-content :deep(.meta-view-highlight:hover) {
  filter: brightness(0.95);
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

/* Tooltip样式 - 使用data-tooltip属性 */
.article-content :deep(.meta-view-highlight[data-tooltip])::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-8px);
  padding: 0.75rem 1rem;
  background-color: hsl(var(--popover));
  color: hsl(var(--popover-foreground));
  border: 1px solid hsl(var(--border));
  border-radius: 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: normal;
  max-width: 300px;
  min-width: 200px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 50;
  text-indent: 0; /* 重置首行缩进 */
}

.article-content :deep(.meta-view-highlight[data-tooltip]:hover)::after {
  opacity: 1;
  transform: translateX(-50%) translateY(-4px);
}

/* 火花洞察Tooltip样式 - 点击触发 */
.article-content :deep(.has-sparks[data-spark-tooltip])::before {
  content: attr(data-spark-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-8px);
  padding: 0.75rem 1rem;
  background-color: hsl(var(--popover));
  color: hsl(var(--popover-foreground));
  border: 1px solid hsl(var(--border));
  border-radius: 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: normal;
  max-width: 400px;
  min-width: 250px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 50;
  text-indent: 0; /* 重置首行缩进 */
}

/* 点击后显示tooltip */
.article-content :deep(.has-sparks.show-tooltip[data-spark-tooltip])::before {
  opacity: 1;
  transform: translateX(-50%) translateY(-4px);
  pointer-events: auto;
}

/* 论证结构透镜的高亮样式 */
.article-content :deep(.meta-view-highlight[data-category="claim"]) {
  background-color: rgba(191, 219, 254, 0.4);
  border-bottom: 2px solid #3b82f6;
}

.article-content :deep(.meta-view-highlight[data-category="evidence"]) {
  background-color: rgba(187, 247, 208, 0.4);
  border-bottom: 2px solid #10b981;
}

.article-content :deep(.meta-view-highlight[data-category="reasoning"]) {
  background-color: rgba(254, 240, 138, 0.4);
  border-bottom: 2px solid #f59e0b;
}

/* 作者立场透镜的高亮样式 */
.article-content :deep(.meta-view-highlight[data-category="objective"]) {
  background-color: rgba(199, 210, 254, 0.4);
  border-bottom: 2px solid #6366f1;
}

.article-content :deep(.meta-view-highlight[data-category="subjective"]) {
  background-color: rgba(254, 205, 211, 0.4);
  border-bottom: 2px solid #f43f5e;
}
</style>
