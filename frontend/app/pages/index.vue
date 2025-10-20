<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-zinc-50 relative overflow-hidden">
    <!-- 全屏背景装饰 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-emerald-400/10 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-slate-400/10 rounded-full blur-3xl"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-zinc-400/5 rounded-full blur-3xl"></div>
    </div>

    <!-- 内容区域 -->
    <div class="relative z-10">
      <AppHeader @open-settings="showAnalysisSettings = true" />

      <!-- 未开始阅读：显示输入界面 -->
      <ArticleInput
        v-if="!isReading"
        @submit="handleArticleSubmit"
      />

      <!-- 阅读界面：双栏布局 -->
      <ReaderLayout v-else>
      <template #left>
        <ArticlePane
          :content="content"
          :title="title"
        />

        <!-- 元视角触发器 -->
        <MetaViewTrigger
          v-if="isReading"
          :article-title="title"
          :article-content="content"
        />

        <!-- 元视角信息面板 -->
        <MetaInfoPanel
          v-if="isReading"
          :article-content="content"
        />
      </template>

      <template #right>
        <!-- 标签页切换 -->
        <div class="border-b border-gray-200 bg-white">
          <div class="flex">
            <button
              @click="activeTab = 'insight'"
              class="flex-1 px-4 py-3 text-sm font-medium transition-all"
              :class="[
                activeTab === 'insight'
                  ? 'text-emerald-700 border-b-2 border-emerald-600 bg-emerald-50/50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              ]"
            >
              <span class="flex items-center justify-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <span>AI 洞察</span>
              </span>
            </button>
            <button
              @click="activeTab = 'stash'"
              class="flex-1 px-4 py-3 text-sm font-medium transition-all relative"
              :class="[
                activeTab === 'stash'
                  ? 'text-amber-700 border-b-2 border-amber-600 bg-amber-50/50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              ]"
            >
              <span class="flex items-center justify-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
                <span>暂存</span>
                <span v-if="stashCount > 0" class="ml-1 px-1.5 py-0.5 text-xs bg-amber-600 text-white rounded-full">
                  {{ stashCount }}
                </span>
              </span>
            </button>
          </div>
        </div>

        <!-- 标签页内容 -->
        <div class="flex-1 overflow-hidden">
          <InsightPane
            v-show="activeTab === 'insight'"
            :insight="displayInsight"
            :reasoning="displayReasoning"
            :is-loading="displayIsGenerating"
            :error="displayError"
            :current-request="currentRequest"
            :use-reasoning="useReasoning"
          />
          <StashPanel
            v-show="activeTab === 'stash'"
            @view-item="handleViewStashItem"
          />
        </div>
      </template>
    </ReaderLayout>

    <!-- 选中文字后显示的小按钮 -->
    <SelectionTrigger
      :show="showTrigger"
      :position="position"
      @click="handleTriggerClick"
      @close="handleTriggerClose"
    />

    <!-- 划词弹出框 -->
    <IntentButtons
      :show="showIntentButtons"
      :position="position"
      :selected-text="selectedText"
      @select="handleIntentSelect"
      @close="clearSelection"
    />

    <!-- 历史记录面板 -->
    <HistoryPanel @select="handleHistorySelect" />

    <!-- 洞察回放按钮 -->
    <InsightReplayButton
      v-if="isReading && insightHistory.length > 0"
      :insight-count="insightHistory.length"
    />

    <!-- 洞察详情弹窗 -->
    <InsightHistoryModal
      :selected-item="selectedHistoryItem"
      @close="selectHistoryItem(null)"
      @continue-chat="handleContinueChat"
    />

    <!-- 火花侧边栏 -->
    <SparkSidebar
      :show="showSidebar"
      :sentence-index="selectedSentenceIndex"
      :selected-sentence="getSelectedSparks?.sentence_text || ''"
      :concept-sparks="getSelectedSparks?.concepts || []"
      :argument-sparks="getSelectedSparks?.arguments || []"
      @close="closeSidebar"
    />

    <!-- 分析设置对话框 -->
    <AnalysisSettingsModal
      :is-open="showAnalysisSettings"
      :user-id="user?.id || 0"
      @close="showAnalysisSettings = false"
      @preferences-updated="handlePreferencesUpdated"
    />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Intent, InsightRequest } from '~/types/insight'
import type { HistoryItem } from '~/types/history'
import type { StashItem } from '~/types/stash'
import type { InsightHistoryItem } from '~/composables/useInsightReplay'
import type { AnalysisPreferences } from '~/composables/useAnalysisPreferences'

// 使用 Composables
const {
  content,
  title,
  isReading,
  setArticle
} = useArticle()

const {
  selectedText,
  context,
  position,
  showIntentButtons,
  clear: clearSelection,
  selectedStart,
  selectedEnd
} = useSelection()

const {
  currentInsight,
  currentReasoning,
  isGenerating,
  error,
  generate
} = useInsightGenerator()

const { stashItems } = useStash()

// 洞察回放相关
const {
  insightHistory,
  selectedHistoryItem,
  loadInsightHistory,
  clearReplayState,
  selectHistoryItem
} = useInsightReplay()

// 分析偏好设置
const { fetchPreferences } = useAnalysisPreferences()
const showAnalysisSettings = ref(false)
const analysisPreferences = ref<AnalysisPreferences | null>(null)

const currentArticleId = useState<number | null>('current-article-id', () => null)
const config = useRuntimeConfig()
const { user } = useAuth()

// 统一深度分析相关
const { connect, disconnect, onAnalysisComplete } = useAnalysisNotifications()
const {
  renderSparks,
  showSidebar,
  selectedSentenceIndex,
  getSelectedSparks,
  closeSidebar,
  sparkGroups
} = useSparkRendererV2()

// 保存完整的分析报告数据
const analysisReport = ref<any>(null)

// 显示逻辑：直接使用普通洞察
const displayInsight = computed(() => currentInsight.value)
const displayReasoning = computed(() => currentReasoning.value)
const displayIsGenerating = computed(() => isGenerating.value)
const displayError = computed(() => error.value)

// 保存当前请求信息（用于收藏和暂存）
const currentRequest = ref<InsightRequest | undefined>(undefined)

// 推理模式状态（全局共享）
const useReasoning = useState('use-reasoning', () => false)

// 标签页切换
const activeTab = ref<'insight' | 'stash'>('insight')

// 暂存数量
const stashCount = computed(() => stashItems.value.length)

// 控制触发按钮显示
const showTrigger = ref(false)

// 监听选中文本变化，控制触发按钮显示
watch(() => selectedText.value, (newValue) => {
  if (newValue && newValue.length > 0 && !showIntentButtons.value) {
    showTrigger.value = true
  } else {
    showTrigger.value = false
  }
})

// 处理触发按钮点击
const handleTriggerClick = () => {
  showTrigger.value = false
  showIntentButtons.value = true
}

// 处理触发按钮关闭
const handleTriggerClose = () => {
  showTrigger.value = false
  clearSelection()
}

// 键盘快捷键
const { register } = useKeyboard()

// 组件卸载时断开 SSE 连接
onUnmounted(() => {
  disconnect()
})

// 处理文章提交
const handleArticleSubmit = async (articleContent: string) => {
  setArticle(articleContent)

  // 如果用户已登录，保存文章并触发深度分析
  if (user.value?.id) {
    try {
      // 获取用户的分析偏好设置
      if (!analysisPreferences.value) {
        analysisPreferences.value = await fetchPreferences(user.value.id)
      }

      // 调用新的 save-with-analysis API
      const response = await $fetch(`${config.public.apiBase}/api/v1/articles/save-with-analysis`, {
        method: 'POST',
        body: {
          title: title.value || '未命名文章',
          content: articleContent,
          user_id: user.value.id
        }
      })

      currentArticleId.value = response.article.id
      console.log('✅ 文章已保存, ID:', response.article.id)

      // 如果已有完整分析报告，直接渲染火花
      if (response.analysis.status === 'completed') {
        console.log('📊 检测到已有分析报告，正在加载...')

        // 获取分析报告
        const reportResponse = await $fetch(`${config.public.apiBase}/api/v1/articles/${response.article.id}/analysis-report`)

        // 保存完整报告数据
        analysisReport.value = reportResponse.report_data

        // 渲染火花
        await renderSparks(reportResponse.report_data)
        console.log('✨ 火花已渲染（来自缓存）')
      } else {
        // 注册分析完成回调
        console.log('🔄 正在后台分析文章，分析完成后将自动渲染火花...')

        onAnalysisComplete(response.article.id, async (articleId) => {
          console.log(`📬 收到分析完成通知，文章 ID: ${articleId}`)

          try {
            // 获取分析报告
            const reportResponse = await $fetch(`${config.public.apiBase}/api/v1/articles/${articleId}/analysis-report`)

            // 保存完整报告数据
            analysisReport.value = reportResponse.report_data

            // 渲染火花（瀑布流动画）
            await renderSparks(reportResponse.report_data)

            console.log('✨ 火花已渲染')

            // 显示成功提示
            const sparkCount = (reportResponse.report_data.concept_sparks?.length || 0) +
                               (reportResponse.report_data.argument_sparks?.length || 0)

            if (sparkCount > 0) {
              // 可以添加 toast 提示
              console.log(`🎉 已为您发现 ${sparkCount} 个高价值洞察点`)
            }
          } catch (error) {
            console.error('❌ 获取分析报告失败:', error)
          }
        })
      }

      // 根据用户偏好设置自动触发分析
      if (analysisPreferences.value) {
        const prefs = analysisPreferences.value

        // 自动触发元视角分析
        if (prefs.auto_meta_analysis) {
          console.log('🔍 自动触发元视角分析...')
          try {
            await $fetch(`${config.public.apiBase}/api/v1/meta-analysis/analyze`, {
              method: 'POST',
              body: {
                title: title.value || '未命名文章',
                author: '未知作者',
                full_text: articleContent,
                user_id: user.value.id
              }
            })
            console.log('✅ 元视角分析完成')
          } catch (error) {
            console.error('❌ 元视角分析失败:', error)
          }
        }

        // 自动触发论证透镜
        if (prefs.auto_argument_lens) {
          console.log('🔍 自动触发论证透镜分析...')
          try {
            // 确保已有 meta_analysis
            const metaResponse = await $fetch(`${config.public.apiBase}/api/v1/meta-analysis/analyze`, {
              method: 'POST',
              body: {
                title: title.value || '未命名文章',
                author: '未知作者',
                full_text: articleContent,
                user_id: user.value.id
              }
            })

            if (metaResponse.meta_analysis?.id) {
              await $fetch(`${config.public.apiBase}/api/v1/thinking-lens/apply`, {
                method: 'POST',
                body: {
                  meta_analysis_id: metaResponse.meta_analysis.id,
                  lens_type: 'argument_structure',
                  full_text: articleContent
                }
              })
              console.log('✅ 论证透镜分析完成')
            }
          } catch (error) {
            console.error('❌ 论证透镜分析失败:', error)
          }
        }

        // 自动触发意图透镜
        if (prefs.auto_stance_lens) {
          console.log('🔍 自动触发意图透镜分析...')
          try {
            // 确保已有 meta_analysis
            const metaResponse = await $fetch(`${config.public.apiBase}/api/v1/meta-analysis/analyze`, {
              method: 'POST',
              body: {
                title: title.value || '未命名文章',
                author: '未知作者',
                full_text: articleContent,
                user_id: user.value.id
              }
            })

            if (metaResponse.meta_analysis?.id) {
              await $fetch(`${config.public.apiBase}/api/v1/thinking-lens/apply`, {
                method: 'POST',
                body: {
                  meta_analysis_id: metaResponse.meta_analysis.id,
                  lens_type: 'author_stance',
                  full_text: articleContent
                }
              })
              console.log('✅ 意图透镜分析完成')
            }
          } catch (error) {
            console.error('❌ 意图透镜分析失败:', error)
          }
        }
      }

      // 如果是已存在的文章且有历史洞察，加载历史记录
      if (!response.article.is_new) {
        await loadInsightHistory(response.article.id, user.value.id)
        console.log(`📚 已加载历史洞察`)
      }
    } catch (error) {
      console.error('❌ 保存文章失败:', error)
    }
  }
}

// 处理意图选择
const handleIntentSelect = async (intent: Intent, customQuestion?: string) => {
  // 获取推理模式状态
  const useReasoning = useState('use-reasoning', () => false)

  const request: InsightRequest = {
    selected_text: selectedText.value,
    context: context.value,
    intent,
    custom_question: customQuestion,
    use_reasoning: useReasoning.value
  }

  // 保存请求信息
  currentRequest.value = request

  await generate(request)
  clearSelection()
  showTrigger.value = false
}

// 处理历史记录选择
const handleHistorySelect = (item: HistoryItem) => {
  // 直接显示历史记录的洞察内容
  currentInsight.value = item.insight

  // 清空当前请求（因为这是历史记录）
  currentRequest.value = undefined

  // 切换到洞察标签页
  activeTab.value = 'insight'

  // 如果有文章标题且与当前不同，可以提示用户
  if (item.articleTitle && item.articleTitle !== title.value) {
    console.log('该记录来自另一篇文章:', item.articleTitle)
  }
}

// 处理继续聊天（从洞察历史）
const handleContinueChat = (item: InsightHistoryItem) => {
  // 恢复选中状态
  selectedText.value = item.selected_text

  // 恢复上下文
  const contextBefore = item.context_before || ''
  const contextAfter = item.context_after || ''
  context.value = contextBefore + item.selected_text + contextAfter

  // 恢复位置信息
  selectedStart.value = item.selected_start
  selectedEnd.value = item.selected_end

  // 显示历史洞察内容
  currentInsight.value = item.insight
  if (item.reasoning) {
    currentReasoning.value = item.reasoning
  }

  // 关闭洞察详情弹窗
  selectHistoryItem(null)

  // 显示意图按钮，允许继续提问
  showIntentButtons.value = true

  console.log('🔄 已恢复选中状态，可以继续提问')
}

// 处理查看暂存项
const handleViewStashItem = (item: StashItem) => {
  // 显示暂存的洞察内容
  currentInsight.value = item.insight
  currentReasoning.value = item.reasoning || ''

  // 恢复请求信息（可选）
  currentRequest.value = {
    selected_text: item.selectedText,
    context: item.context,
    intent: item.intent,
    custom_question: item.customQuestion,
    use_reasoning: !!item.reasoning
  }

  // 切换到洞察标签页查看
  activeTab.value = 'insight'

  console.log('📖 查看暂存项:', item.selectedText.substring(0, 30), '...')
}

// 处理偏好设置更新
const handlePreferencesUpdated = (preferences: AnalysisPreferences) => {
  analysisPreferences.value = preferences
  console.log('✅ 分析偏好设置已更新:', preferences)
}

// 页面元信息
useHead({
  title: 'InsightReader - 划词即问，即刻理解',
  meta: [
    { name: 'description', content: '最好的阅读辅助工具，使用 AI 帮你深度理解文章内容' }
  ]
})

// 监听文章 ID 变化，自动加载历史洞察
watch(() => currentArticleId.value, async (articleId) => {
  if (articleId && user.value?.id) {
    await loadInsightHistory(articleId, user.value.id)
    if (insightHistory.value.length > 0) {
      console.log(`📚 文章 ${articleId} 有 ${insightHistory.value.length} 条历史洞察`)
    }
  } else {
    // 清空历史记录
    clearReplayState()
  }
})

// 从历史记录打开文章
const route = useRoute()

onMounted(async () => {
  // 建立 SSE 连接（用于接收分析完成通知）
  connect()

  register('escape', () => {
    if (showIntentButtons.value) {
      clearSelection()
      showTrigger.value = false
    } else if (showTrigger.value) {
      clearSelection()
      showTrigger.value = false
    }
  })

  // 如果有 articleId，从历史记录加载文章
  const articleId = route.query.articleId
  if (articleId) {
    try {
      // 获取文章详情
      const article = await $fetch<any>(
        `${config.public.apiBase}/api/v1/articles/${articleId}`
      )

      // 加载文章内容
      setArticle(article.content, article.title)

      // 设置文章 ID，触发历史洞察加载
      currentArticleId.value = Number(articleId)

      console.log('✅ 从历史记录加载文章:', article.title)

      // 等待 DOM 更新完成
      await nextTick()

      // 尝试加载分析报告并渲染火花
      try {
        const reportResponse = await $fetch(`${config.public.apiBase}/api/v1/articles/${articleId}/analysis-report`)

        // 保存完整报告数据
        analysisReport.value = reportResponse.report_data

        // 渲染火花
        await renderSparks(reportResponse.report_data)
        console.log('✨ 火花已渲染（历史文章）')
      } catch (reportError) {
        console.log('ℹ️ 该文章暂无分析报告')
      }
    } catch (error) {
      console.error('❌ 加载历史文章失败:', error)
    }
  }
})
</script>
