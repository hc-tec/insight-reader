<template>
  <div class="min-h-screen relative flex items-center justify-center overflow-hidden">
    <!-- 网格背景 -->
    <div class="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px] opacity-50"></div>

    <!-- 渐变光效 -->
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-[128px] animate-pulse"></div>
    <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-teal-500/20 rounded-full blur-[128px] animate-pulse" style="animation-delay: 1s;"></div>

    <div class="relative z-10 w-full max-w-5xl mx-auto px-6 py-20">
      <!-- Hero Section -->
      <div class="text-center mb-16 space-y-8">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur-sm border border-gray-200/50 shadow-sm animate-fade-in">
          <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span class="text-sm font-medium text-gray-700">AI-Powered Reading Assistant</span>
        </div>

        <!-- Main Heading -->
        <div class="space-y-4">
          <h1 class="text-6xl md:text-7xl font-bold tracking-tight">
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900">
              深度理解
            </span>
            <br />
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-600">
              每一个字
            </span>
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            划词提问，AI 即时解答。让阅读不再有困惑，让知识触手可及
          </p>
        </div>

        <!-- Stats -->
        <div class="flex items-center justify-center gap-8 text-sm">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span class="text-gray-600">即时解答</span>
          </div>
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
            </svg>
            <span class="text-gray-600">深度分析</span>
          </div>
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
            </svg>
            <span class="text-gray-600">多维视角</span>
          </div>
        </div>
      </div>

      <!-- Input Card -->
      <div class="relative group">
        <!-- Glow effect on hover -->
        <div class="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl opacity-0 group-hover:opacity-20 blur transition duration-500"></div>

        <div class="relative bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-2xl shadow-gray-200/50 overflow-hidden">
          <!-- Example Pills -->
          <div class="px-8 pt-8 pb-4">
            <div class="flex items-center gap-2 mb-4">
              <span class="text-sm font-medium text-gray-500">快速开始</span>
              <div class="flex-1 h-px bg-gradient-to-r from-gray-200 to-transparent"></div>
            </div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="example in examples"
                :key="example.label"
                @click="loadExample(example.content)"
                class="group/btn inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-50 hover:bg-gradient-to-r hover:from-emerald-50 hover:to-teal-50 border border-gray-200/50 hover:border-emerald-200 transition-all text-sm font-medium text-gray-700 hover:text-emerald-700"
              >
                <span>{{ example.label }}</span>
                <svg class="w-4 h-4 opacity-0 group-hover/btn:opacity-100 -translate-x-2 group-hover/btn:translate-x-0 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Divider -->
          <div class="px-8">
            <div class="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent"></div>
          </div>

          <!-- Textarea -->
          <div class="p-8">
            <div class="relative">
              <Textarea
                v-model="content"
                placeholder="在此粘贴文章内容，或使用上方示例快速体验...&#10;&#10;支持的内容：新闻报道、学术论文、技术博客、产品文档等任何文本内容"
                class="min-h-[320px] text-base leading-relaxed resize-none border-0 bg-transparent focus:ring-0 focus:outline-none placeholder:text-gray-400 text-gray-700"
                @keydown.ctrl.enter="handleSubmit"
              />

              <!-- Floating Stats -->
              <div class="absolute bottom-4 left-4 flex items-center gap-4">
                <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/90 backdrop-blur-sm border border-gray-200/50 shadow-sm">
                  <div :class="[
                    'w-1.5 h-1.5 rounded-full transition-colors',
                    canSubmit ? 'bg-emerald-500 shadow-sm shadow-emerald-500/50' : 'bg-gray-300'
                  ]"></div>
                  <span class="text-xs font-medium text-gray-600">
                    {{ charCount }} 字符
                  </span>
                </div>

                <div v-if="charCount > 0" class="px-3 py-1.5 rounded-lg bg-white/90 backdrop-blur-sm border border-gray-200/50 shadow-sm">
                  <div class="flex items-center gap-2">
                    <div class="w-24 h-1 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        class="h-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-300"
                        :style="{ width: `${Math.min((charCount / 50) * 100, 100)}%` }"
                      ></div>
                    </div>
                    <span class="text-xs font-medium text-gray-600">
                      {{ Math.min(Math.floor((charCount / 50) * 100), 100) }}%
                    </span>
                  </div>
                </div>
              </div>

              <!-- Keyboard Hint -->
              <div class="absolute bottom-4 right-4 flex items-center gap-1.5 text-xs text-gray-400">
                <kbd class="px-2 py-1 bg-white/90 border border-gray-200/50 rounded shadow-sm font-medium text-gray-600">⌘</kbd>
                <span>+</span>
                <kbd class="px-2 py-1 bg-white/90 border border-gray-200/50 rounded shadow-sm font-medium text-gray-600">Enter</kbd>
              </div>
            </div>
          </div>

          <!-- Action Bar -->
          <div class="px-8 pb-8">
            <div class="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent mb-6"></div>

            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 text-sm text-gray-500">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <span>你的内容安全且私密</span>
              </div>

              <button
                @click="handleSubmit"
                :disabled="!canSubmit"
                class="group relative inline-flex items-center gap-2 px-8 py-3.5 rounded-xl font-semibold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 disabled:from-gray-300 disabled:to-gray-300 shadow-lg shadow-emerald-500/25 hover:shadow-xl hover:shadow-emerald-500/30 disabled:shadow-none transition-all duration-300 hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
              >
                <span>开始阅读</span>
                <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>

                <!-- Shine effect -->
                <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000"></div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Feature Grid -->
      <div class="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="group relative p-6 rounded-xl bg-white/50 backdrop-blur-sm border border-gray-200/50 hover:bg-white/80 hover:shadow-lg hover:shadow-gray-200/50 transition-all duration-300">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-2">即时理解</h3>
              <p class="text-sm text-gray-600 leading-relaxed">选中任意文字，AI 立即提供深度解析，让复杂概念变得清晰易懂</p>
            </div>
          </div>
        </div>

        <div class="group relative p-6 rounded-xl bg-white/50 backdrop-blur-sm border border-gray-200/50 hover:bg-white/80 hover:shadow-lg hover:shadow-gray-200/50 transition-all duration-300">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-2">多维视角</h3>
              <p class="text-sm text-gray-600 leading-relaxed">从不同角度分析内容，探索反面观点，培养批判性思维</p>
            </div>
          </div>
        </div>

        <div class="group relative p-6 rounded-xl bg-white/50 backdrop-blur-sm border border-gray-200/50 hover:bg-white/80 hover:shadow-lg hover:shadow-gray-200/50 transition-all duration-300">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-2">智能记录</h3>
              <p class="text-sm text-gray-600 leading-relaxed">自动保存你的提问和洞察，随时回顾学习历程</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Props & Emits
const emit = defineEmits<{
  submit: [content: string]
}>()

// State
const content = ref('')

// Examples
const examples = [
  {
    label: '🤖 AI 技术',
    content: '人工智能正在深刻改变我们的生活方式。从自动驾驶汽车到智能家居，从医疗诊断到金融分析，AI 技术的应用已经渗透到社会的各个角落。然而，随着 AI 能力的不断提升，我们也面临着诸多挑战：如何确保 AI 系统的安全性和可控性？如何处理 AI 可能带来的就业冲击？如何在享受 AI 便利的同时保护个人隐私？这些问题需要技术专家、政策制定者和全社会共同思考和解决。'
  },
  {
    label: '📚 教育变革',
    content: '在线教育的兴起正在重塑传统的教育模式。学习者不再受限于地理位置和时间，可以随时随地访问全球最优质的教育资源。个性化学习成为可能，AI 助教能够根据每个学生的学习进度和特点提供定制化的辅导。然而，这种转变也带来了新的问题：如何确保在线学习的质量？如何维持学生的学习动力？如何培养批判性思维而不仅仅是知识的灌输？'
  },
  {
    label: '🌍 气候行动',
    content: '气候变化已成为人类面临的最严峻挑战之一。全球平均气温持续上升，极端天气事件频发，生物多样性加速丧失。为应对这一危机，各国政府纷纷制定碳中和目标，推动可再生能源发展，促进产业绿色转型。但仅靠政府行动还不够，企业需要承担更多社会责任，个人也应该从日常生活做起，减少碳足迹。只有全社会共同努力，才能为子孙后代留下一个宜居的地球。'
  }
]

// Computed
const charCount = computed(() => content.value.length)
const canSubmit = computed(() => charCount.value >= 50)

// Methods
const loadExample = (exampleContent: string) => {
  content.value = exampleContent
}

const handleSubmit = () => {
  if (!canSubmit.value) return
  emit('submit', content.value)
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}

/* 移除 Textarea 的默认样式 */
textarea {
  font-family: inherit;
}

textarea::placeholder {
  line-height: 1.8;
}
</style>
