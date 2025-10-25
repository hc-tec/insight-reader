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
        @article-click="handleDemoArticleClick"
      />

      <!-- 阅读界面：双栏布局 -->
      <ReaderLayout
        v-else
        ref="readerLayoutRef"
      >
      <template #left>
        <ArticlePane
          :content="content"
          :title="title"
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

    <!-- 历史记录面板（只保留侧边栏，按钮已整合到FloatingActions） -->
    <HistoryPanel
      :is-open="isHistoryPanelOpen"
      @close="isHistoryPanelOpen = false"
      @select="handleHistorySelect"
    />

    <!-- 统一的悬浮按钮组 -->
    <FloatingActions
      v-if="isReading"
      :is-insight-panel-expanded="isInsightPanelExpanded"
      :insight-count="insightConversations.length"
      :is-replay-mode="isReplayMode"
      :history-count="history.length"
      :is-meta-view-active="isMetaViewActive"
      :is-meta-analyzing="isMetaAnalyzing"
      @toggle-insight-panel="toggleInsightPanel"
      @toggle-replay="handleToggleReplay"
      @open-history="isHistoryPanelOpen = true"
      @toggle-meta-view="handleToggleMetaView"
    />

    <!-- 透镜注解覆盖层 -->
    <LensAnnotationOverlay
      v-if="isReading"
      :is-active="isLensAnnotationActive"
      :annotations="lensAnnotations"
    />

    <!-- 洞察详情弹窗 -->
    <InsightHistoryModal
      :selected-item="selectedConversation"
      @close="selectConversation(null)"
      @continue-chat="handleContinueChat"
    />

    <!-- 火花洞察现在使用Tooltip显示，不再需要侧边栏 -->

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
import type { InsightConversation } from '~/composables/useInsightReplay'
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
  insightConversations,
  selectedConversation,
  loadInsightHistory,
  clearReplayState,
  selectConversation,
  isReplayMode,
  toggleReplayMode,
  renderHistoryHighlights,
  removeHistoryHighlights
} = useInsightReplay()

// 历史记录相关
const { history } = useHistory()

// 元视角相关
const {
  isMetaViewActive,
  isAnalyzing: isMetaAnalyzing,
  analyzeArticle,
  toggleMetaView
} = useMetaView()

// 思维透镜相关
const {
  enabledLenses,
  lensResults,
  loadingLenses,
  renderHighlightsByType
} = useThinkingLens()

// 透镜注解相关
const {
  isAnnotationModeActive: isLensAnnotationActive,
  annotations: lensAnnotations,
  toggleAnnotationMode,
  refreshAnnotationPositions
} = useLensAnnotation()

// UI状态
const isHistoryPanelOpen = ref(false)
const isInsightPanelExpanded = useState('insight-panel-expanded', () => false)
const readerLayoutRef = ref(null)

// 分析偏好设置
const { fetchPreferences } = useAnalysisPreferences()
const showAnalysisSettings = ref(false)
const analysisPreferences = ref<AnalysisPreferences | null>(null)

const currentArticleId = useState<number | null>('current-article-id', () => null)
const config = useRuntimeConfig()
const { user } = useAuth()

// 统一深度分析相关
const {
  connect,
  disconnect,
  onAnalysisComplete,
  onMetaAnalysisComplete,
  onLensComplete,
  onTaskFailed
} = useAnalysisNotifications()
const {
  renderSparks,
  sparkGroups
} = useSparkRendererV2()

// 保存完整的分析报告数据
const analysisReport = ref<any>(null)

// 显示逻辑：直接使用普通洞察
const displayInsight = computed(() => currentInsight.value)
const displayReasoning = computed(() => currentReasoning.value)
const displayIsGenerating = computed(() => isGenerating.value)
const displayError = computed(() => error.value)

// 保存当前请求信息（用于收藏和暂存）- 使用全局状态
const currentRequest = useState<InsightRequest | undefined>('current-request-global', () => undefined)

// 推理模式状态（全局共享）
const useReasoning = useState('use-reasoning', () => false)

// 标签页切换
const activeTab = ref<'insight' | 'stash'>('insight')

// 暂存数量
const stashCount = computed(() => stashItems.value.length)

// 控制触发按钮显示
const showTrigger = ref(false)

// 标记是否是从历史回放恢复的选中（用于避免弹出意图按钮）- 使用全局状态
const isRestoringFromHistory = useState('is-restoring-from-history', () => false)

// 监听选中文本变化，控制触发按钮显示
watch(() => selectedText.value, (newValue) => {
  // 如果是从历史回放恢复的选中，不显示意图按钮
  if (isRestoringFromHistory.value) {
    showTrigger.value = false
    isRestoringFromHistory.value = false  // 重置标志
    return
  }

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

// 处理示例文章点击
const handleDemoArticleClick = async (articleId: number) => {
  try {
    // 获取文章详情
    const article = await $fetch<any>(
      `${config.public.apiBase}/api/v1/articles/${articleId}`
    )

    // 加载文章内容
    setArticle(article.content, article.title)

    // 设置文章 ID，触发历史洞察加载
    currentArticleId.value = Number(articleId)

    console.log('✅ 从示例文章加载:', article.title)

    // 等待 DOM 更新完成
    await nextTick()

    // 尝试加载分析报告并渲染火花
    try {
      const reportResponse = await $fetch(`${config.public.apiBase}/api/v1/articles/${articleId}/analysis-report`)

      // 保存完整报告数据
      analysisReport.value = reportResponse.report_data

      // 渲染火花
      await renderSparks(reportResponse.report_data)
      console.log('✨ 火花已渲染（示例文章）')
    } catch (reportError) {
      console.log('ℹ️ 该文章暂无分析报告')
    }
  } catch (error) {
    console.error('❌ 加载示例文章失败:', error)
  }
}

// 处理文章提交
const handleArticleSubmit = async (articleContent: string) => {
  setArticle(articleContent)

  // 如果用户已登录，保存文章并触发深度分析
  if (user.value?.id) {
    try {
      // 调用新的 save-with-analysis API（快速返回）
      const response = await $fetch(`${config.public.apiBase}/api/v1/articles/save-with-analysis`, {
        method: 'POST',
        body: {
          title: title.value || '未命名文章',
          content: articleContent
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

      // 异步获取并应用用户偏好（不阻塞主流程）
      if (!analysisPreferences.value && user.value?.id) {
        fetchPreferences(user.value.id).then(prefs => {
          analysisPreferences.value = prefs

          // 应用偏好设置：自动触发元视角分析
          if (prefs.auto_meta_analysis && currentArticleId.value) {
            console.log('🔍 自动触发元视角分析...')
            $fetch(`${config.public.apiBase}/api/v1/meta-analysis/analyze`, {
              method: 'POST',
              body: {
                title: title.value || '未命名文章',
                author: '未知作者',
                full_text: articleContent
              }
            }).then(metaResponse => {
              if (metaResponse.status === 'completed') {
                console.log('✅ 元视角分析完成（来自缓存）')
              } else if (metaResponse.status === 'pending') {
                console.log('🔄 元视角分析已提交，任务ID:', metaResponse.task_id)
              }
            }).catch(error => {
              console.error('❌ 元视角分析失败:', error)
            })
          }
        }).catch(err => {
          console.warn('获取分析偏好失败:', err)
        })
      } else if (analysisPreferences.value?.auto_meta_analysis) {
        // 已有偏好设置，立即触发
        console.log('🔍 自动触发元视角分析...')
        $fetch(`${config.public.apiBase}/api/v1/meta-analysis/analyze`, {
          method: 'POST',
          body: {
            title: title.value || '未命名文章',
            author: '未知作者',
            full_text: articleContent
          }
        }).then(metaResponse => {
          if (metaResponse.status === 'completed') {
            console.log('✅ 元视角分析完成（来自缓存）')
          } else if (metaResponse.status === 'pending') {
            console.log('🔄 元视角分析已提交，任务ID:', metaResponse.task_id)
          }
        }).catch(error => {
          console.error('❌ 元视角分析失败:', error)
        })
      }

      // 如果是已存在的文章且有历史洞察，加载历史记录
      if (!response.article.is_new) {
        await loadInsightHistory(response.article.id)
        console.log(`📚 已加载历史洞察`)
      }
    } catch (error) {
      console.error('❌ 保存文章失败:', error)
    }
  }
}

// 处理意图选择
const handleIntentSelect = async (intent: Intent, customQuestion?: string, includeFullText?: boolean) => {
  // 如果侧边栏关闭，自动打开它
  if (!isInsightPanelExpanded.value) {
    toggleInsightPanel()
  }

  // 获取推理模式状态
  const useReasoning = useState('use-reasoning', () => false)

  const request: InsightRequest = {
    selected_text: selectedText.value,
    context: context.value,
    intent,
    custom_question: customQuestion,
    use_reasoning: useReasoning.value,
    include_full_text: includeFullText || false
  }

  // 如果需要附带全文，添加full_text字段
  if (includeFullText && content.value) {
    request.full_text = content.value
  }

  // 保存请求信息
  currentRequest.value = request

  // 清空对话历史（因为这是新的洞察）
  const { clearConversation } = useFollowUp()
  clearConversation()
  console.log('🆕 生成新洞察，清空对话历史')

  await generate(request)
  clearSelection()
  showTrigger.value = false
}

// 处理历史记录选择
const handleHistorySelect = (item: HistoryItem) => {
  // 如果侧边栏关闭，自动打开它
  if (!isInsightPanelExpanded.value) {
    toggleInsightPanel()
  }

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
const handleContinueChat = (conversation: InsightConversation) => {
  // 标记为从历史恢复，避免弹出意图按钮
  isRestoringFromHistory.value = true

  // 如果侧边栏关闭，自动打开它
  if (!isInsightPanelExpanded.value) {
    toggleInsightPanel()
  }

  // 恢复选中状态
  selectedText.value = conversation.selected_text

  // 恢复上下文
  const contextBefore = conversation.context_before || ''
  const contextAfter = conversation.context_after || ''
  context.value = contextBefore + conversation.selected_text + contextAfter

  // 恢复位置信息
  selectedStart.value = conversation.selected_start
  selectedEnd.value = conversation.selected_end

  // 加载对话历史到追问组件
  const { conversationHistory, clearConversation } = useFollowUp()
  clearConversation()

  // 分离初始对话和追问对话
  const messages = conversation.messages

  // 第一条 assistant 消息是初始洞察
  const initialAssistant = messages.find(m => m.role === 'assistant')

  // ⚠️ 重要：必须先设置 currentRequest，再设置 currentInsight
  // 因为设置 currentInsight 会触发组件更新，此时需要 currentRequest 已经就绪
  currentRequest.value = {
    selected_text: conversation.selected_text,
    context: context.value,
    intent: conversation.intent as Intent,
    custom_question: conversation.question || undefined,  // ✅ 添加自定义问题
    selected_start: conversation.selected_start ?? undefined,
    selected_end: conversation.selected_end ?? undefined,
    use_reasoning: !!initialAssistant?.reasoning
  }

  // 显示初始洞察到主洞察区
  if (initialAssistant) {
    currentInsight.value = initialAssistant.content
    currentReasoning.value = initialAssistant.reasoning || ''
  }

  // 后续的消息（索引 >= 2）是追问对话，加载到 conversationHistory
  const followUpMessages = messages.slice(2)  // 跳过前两条（初始 user + assistant）
  if (followUpMessages.length > 0) {
    conversationHistory.value = followUpMessages.map(msg => ({
      role: msg.role,
      content: msg.content,
      reasoning: msg.reasoning,
      timestamp: new Date(msg.timestamp).getTime(),
      insight_id: msg.insight_id  // 重要：保留 insight_id
    }))
    console.log('🔄 已恢复完整对话（', followUpMessages.length, '条追问消息）')
  } else {
    console.log('🔄 这是初始洞察，没有追问记录')
  }

  // 关闭洞察详情弹窗
  selectConversation(null)

  // 切换到洞察标签页
  activeTab.value = 'insight'

  console.log('🔄 已恢复对话，可以继续提问')
}

// 处理查看暂存项
const handleViewStashItem = (item: StashItem) => {
  // 如果侧边栏关闭，自动打开它
  if (!isInsightPanelExpanded.value) {
    toggleInsightPanel()
  }

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

// 切换AI洞察面板
const toggleInsightPanel = () => {
  // 直接切换全局状态，ReaderLayout 会自动响应
  isInsightPanelExpanded.value = !isInsightPanelExpanded.value
}

// 处理回放切换
const handleToggleReplay = () => {
  toggleReplayMode()

  // 渲染或移除标注
  const containerEl = document.getElementById('article-content-container')
  if (!containerEl) return

  if (isReplayMode.value) {
    renderHistoryHighlights(containerEl, insightConversations.value)
  } else {
    removeHistoryHighlights(containerEl)
  }
}

// 处理元视角切换
const handleToggleMetaView = async () => {
  if (!isMetaViewActive.value) {
    // 开启元视角：触发分析
    try {
      await analyzeArticle(
        title.value || '未命名文章',
        '未知作者',
        new Date().toISOString(),
        content.value,
        user.value?.id,
        undefined
      )

      // 分析成功后打开面板
      toggleMetaView()
    } catch (error) {
      console.error('元信息分析失败:', error)
      // 分析失败时也打开面板显示错误
      toggleMetaView()
    }
  } else {
    // 关闭元视角
    toggleMetaView()
  }
}

// 页面元信息
useHead({
  title: 'InsightReader - 划词即问，即刻理解',
  meta: [
    { name: 'description', content: '最好的阅读辅助工具，使用 AI 帮你深度理解文章内容' }
  ]
})

// 监听文章 ID 变化，自动加载历史洞察
// 支持示例文章（无需登录）和普通文章（需要登录）
watch(() => currentArticleId.value, async (articleId) => {
  if (articleId) {
    await loadInsightHistory(articleId)
    if (insightConversations.value.length > 0) {
      console.log(`📚 文章 ${articleId} 有 ${insightConversations.value.length} 个对话链`)
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

  // 预加载用户偏好设置（避免首次提交文章时阻塞）
  if (user.value?.id && !analysisPreferences.value) {
    fetchPreferences(user.value.id).then(prefs => {
      analysisPreferences.value = prefs
      console.log('✅ 用户偏好设置已预加载')
    }).catch(err => {
      console.warn('预加载用户偏好失败:', err)
    })
  }

  // 注册元视角分析完成回调
  onMetaAnalysisComplete(async (articleId, metaAnalysis) => {
    console.log(`📬 收到元视角分析完成通知，文章 ID: ${articleId}`)

    // 更新元视角分析数据（使用 useState 直接访问共享状态）
    const metaAnalysisData = useState<any>('meta-analysis-data', () => null)
    const isMetaAnalyzing = useState<boolean>('meta-view-analyzing', () => false)

    metaAnalysisData.value = metaAnalysis
    isMetaAnalyzing.value = false

    console.log('✅ 元视角分析结果已更新')

    // 如果AI生成了标题，更新文章标题
    if (metaAnalysis.generated_title) {
      title.value = metaAnalysis.generated_title
      console.log('✅ 已更新AI生成的标题:', metaAnalysis.generated_title)
    }
  })

  // 注册思维透镜完成回调
  onLensComplete(async (lensType, lensResult) => {
    console.log(`📬 收到 ${lensType} 透镜分析完成通知`)

    // 获取可写的状态引用
    const writableLensResults = useState<Map<any, any>>('lens-results')
    const writableLoadingLenses = useState<Set<any>>('loading-lenses')

    // 存储透镜结果
    writableLensResults.value.set(lensType, lensResult)

    // 移除加载状态 - 创建新Set触发响应式更新
    const newLoadingSet = new Set(writableLoadingLenses.value)
    newLoadingSet.delete(lensType)
    writableLoadingLenses.value = newLoadingSet

    console.log(`🔄 加载状态已更新，剩余加载中的透镜: ${writableLoadingLenses.value.size}`)

    // 如果该透镜当前已启用，应用高亮
    if (enabledLenses.value.has(lensType as any)) {
      const containerEl = document.querySelector('.article-content')
      if (containerEl) {
        renderHighlightsByType(containerEl as HTMLElement, lensResult.highlights, lensType as any)
        console.log(`✨ ${lensType} 透镜高亮已应用`)
      }
    }

    console.log(`✅ ${lensType} 透镜结果已保存，共 ${lensResult.highlights?.length || 0} 个高亮`)
  })

  // 注册任务失败回调
  onTaskFailed((taskType, error) => {
    console.error(`❌ ${taskType} 任务失败:`, error)
    // 显示错误提示给用户
    const taskNames: Record<string, string> = {
      'article_analysis': '文章分析',
      'article_reanalysis': '文章重新分析',
      'meta_analysis': '元视角分析',
      'thinking_lens_argument_structure': '论证结构透镜',
      'thinking_lens_author_stance': '作者意图透镜'
    }
    const taskName = taskNames[taskType] || '分析'
    console.log(`⚠️ ${taskName}失败: ${error}`)
  })

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
