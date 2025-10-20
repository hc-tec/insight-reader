# 洞察回放功能 - 完整实现指南（包含位置保存和继续聊天）

## ✅ 已完成的工作

1. ✅ 修改 `useSelection.ts` - 添加位置计算逻辑
2. ✅ 后端 API 已完成（支持保存位置）
3. ✅ `useInsightReplay.ts` composable 已创建
4. ✅ 回放按钮和详情弹窗组件已创建

## 🚧 需要完成的集成步骤

### 步骤 1: 修改主页面保存文章逻辑

**文件**: `frontend/app/pages/index.vue`

在 `<script setup>` 中添加：

```typescript
// 1. 引入必要的 composables
const config = useRuntimeConfig()
const { user } = useAuth()
const currentArticleId = useState<number | null>('current-article-id', () => null)
const { insightHistory, selectedHistoryItem, loadInsightHistory, clearReplayState, selectHistoryItem } = useInsightReplay()

// 2. 修改 handleArticleSubmit 函数
const handleArticleSubmit = async (articleContent: string) => {
  setArticle(articleContent)

  // 登录用户自动保存文章
  if (user.value?.id) {
    try {
      const response = await $fetch(`${config.public.apiBase}/api/v1/articles/save`, {
        method: 'POST',
        body: {
          title: title.value,
          author: 'Unknown',
          content: articleContent,
          user_id: user.value.id
        }
      })

      currentArticleId.value = response.article.id
      console.log('✅ 文章已保存, ID:', response.article.id)

      // 如果是已存在的文章，加载洞察历史
      if (!response.article.is_new && response.article.insight_count > 0) {
        await loadInsightHistory(response.article.id, user.value.id)
        console.log('✅ 加载了历史洞察:', insightHistory.value.length, '条')
      }
    } catch (error) {
      console.error('❌ 保存文章失败:', error)
    }
  }
}

// 3. 文章ID变化时加载洞察历史（用于从历史页面打开文章）
watch(() => currentArticleId.value, async (articleId) => {
  if (articleId && user.value?.id) {
    await loadInsightHistory(articleId, user.value.id)
  }
})

// 4. 页面卸载时清理
onUnmounted(() => {
  clearReplayState()
  currentArticleId.value = null
})
```

在 `<template>` 中添加（在 `<HistoryPanel>` 之后）：

```vue
<!-- 洞察回放按钮 -->
<InsightReplayButton
  v-if="isReading && insightHistory.length > 0"
  :insight-count="insightHistory.length"
/>

<!-- 洞察详情弹窗（带继续聊天功能） -->
<InsightHistoryModal
  :selected-item="selectedHistoryItem"
  @close="selectHistoryItem(null)"
  @continue-chat="handleContinueChat"
/>
```

添加继续聊天处理函数：

```typescript
// 5. 处理继续聊天
const handleContinueChat = (item: InsightHistoryItem) => {
  // 恢复选中状态
  const { selectedText, context, selectedStart, selectedEnd } = useSelection()
  selectedText.value = item.selected_text
  context.value = item.context_before + item.selected_text + item.context_after
  selectedStart.value = item.selected_start
  selectedEnd.value = item.selected_end

  // 关闭弹窗
  selectHistoryItem(null)

  // 显示意图按钮，让用户可以继续提问
  showIntentButtons.value = true

  console.log('🔄 已恢复选中状态，可以继续提问')
}
```

---

### 步骤 2: 修改洞察生成器保存历史

**文件**: `frontend/app/composables/useInsightGenerator.ts`

在文件顶部添加获取 composables：

```typescript
export const useInsightGenerator = () => {
  const config = useRuntimeConfig()
  const { user } = useAuth()
  const currentArticleId = useState<number | null>('current-article-id', () => null)
  const { loadInsightHistory } = useInsightReplay()

  // ... 现有代码
```

在 `generate()` 函数成功后添加保存逻辑（在设置 `currentInsight.value` 之后）：

```typescript
const generate = async (request: InsightRequest) => {
  isGenerating.value = true
  error.value = null

  try {
    // ... 现有的 API 调用逻辑

    // 设置当前洞察
    currentInsight.value = data.insight
    currentReasoning.value = data.reasoning || null

    // ✨ 新增：保存洞察历史
    if (currentArticleId.value && user.value?.id) {
      try {
        // 提取上下文
        const { selectedStart, selectedEnd } = useSelection()
        const contextBefore = extractContextBefore(request.context, 50)
        const contextAfter = extractContextAfter(request.context, 50)

        await $fetch(`${config.public.apiBase}/api/v1/insights/history`, {
          method: 'POST',
          body: {
            article_id: currentArticleId.value,
            user_id: user.value.id,
            selected_text: request.selected_text,
            selected_start: selectedStart.value,
            selected_end: selectedEnd.value,
            context_before: contextBefore,
            context_after: contextAfter,
            intent: request.intent,
            question: request.custom_question,
            insight: currentInsight.value,
            reasoning: currentReasoning.value
          }
        })

        console.log('✅ 洞察已保存到历史')

        // 重新加载历史列表
        await loadInsightHistory(currentArticleId.value, user.value.id)
      } catch (saveError) {
        console.error('❌ 保存洞察历史失败:', saveError)
        // 不影响主流程，继续
      }
    }

  } catch (err) {
    // ... 现有的错误处理
  } finally {
    isGenerating.value = false
  }
}
```

添加辅助函数：

```typescript
// 提取前50字上下文
function extractContextBefore(fullContext: string, length: number): string {
  const parts = fullContext.split('\n\n')
  if (parts.length < 2) return ''

  const before = parts[0]
  return before.length > length ? '...' + before.slice(-length) : before
}

// 提取后50字上下文
function extractContextAfter(fullContext: string, length: number): string {
  const parts = fullContext.split('\n\n')
  if (parts.length < 3) return ''

  const after = parts[2]
  return after.length > length ? after.slice(0, length) + '...' : after
}
```

---

### 步骤 3: 修改洞察回放组件支持基于位置的高亮

**文件**: `frontend/app/composables/useInsightReplay.ts`

修改 `highlightHistoryItem` 函数，优先使用位置信息：

```typescript
const highlightHistoryItem = (containerEl: HTMLElement, item: InsightHistoryItem) => {
  const searchText = item.selected_text.trim()
  if (!searchText) return

  // 优先使用位置信息
  if (item.selected_start !== null && item.selected_end !== null) {
    highlightByPosition(containerEl, item)
  } else {
    // 降级到文本匹配
    highlightByTextMatch(containerEl, item)
  }
}

/**
 * 基于位置高亮（精确方案）
 */
const highlightByPosition = (containerEl: HTMLElement, item: InsightHistoryItem) => {
  const { content } = useArticle()
  const fullText = content.value

  if (!fullText || item.selected_start === null || item.selected_end === null) {
    console.warn('⚠️ 缺少位置信息，降级到文本匹配')
    highlightByTextMatch(containerEl, item)
    return
  }

  // 从文章内容中提取目标文本
  const targetText = fullText.substring(item.selected_start, item.selected_end)

  // 使用文本匹配找到对应的 DOM 节点
  const walker = document.createTreeWalker(
    containerEl,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        const parent = node.parentElement
        if (parent?.classList.contains('insight-replay-highlight')) {
          return NodeFilter.FILTER_REJECT
        }
        if (parent?.classList.contains('meta-view-highlight')) {
          return NodeFilter.FILTER_REJECT
        }
        return node.textContent?.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
      }
    }
  )

  const textNodes: Text[] = []
  let currentNode: Node | null
  while ((currentNode = walker.nextNode())) {
    textNodes.push(currentNode as Text)
  }

  // 拼接所有文本节点，构建位置映射
  let currentOffset = 0
  const nodeMap: Array<{ node: Text; startOffset: number; endOffset: number }> = []

  for (const node of textNodes) {
    const text = node.textContent || ''
    nodeMap.push({
      node,
      startOffset: currentOffset,
      endOffset: currentOffset + text.length
    })
    currentOffset += text.length
  }

  // 查找包含目标位置的节点
  const targetNodes = nodeMap.filter(
    n => n.startOffset < item.selected_end! && n.endOffset > item.selected_start!
  )

  if (targetNodes.length === 0) {
    console.warn('⚠️ 未找到目标节点，降级到文本匹配')
    highlightByTextMatch(containerEl, item)
    return
  }

  // 如果跨多个节点，暂时降级
  if (targetNodes.length > 1) {
    console.warn('⚠️ 跨多个节点，降级到文本匹配')
    highlightByTextMatch(containerEl, item)
    return
  }

  // 单节点高亮
  const targetNode = targetNodes[0]
  const node = targetNode.node
  const relativeStart = Math.max(0, item.selected_start! - targetNode.startOffset)
  const relativeEnd = Math.min(
    node.textContent!.length,
    item.selected_end! - targetNode.startOffset
  )

  const textContent = node.textContent || ''
  const beforeText = textContent.substring(0, relativeStart)
  const highlightText = textContent.substring(relativeStart, relativeEnd)
  const afterText = textContent.substring(relativeEnd)

  const parent = node.parentNode
  if (!parent) return

  // 创建高亮元素
  const highlightEl = createHistoryHighlightElement(highlightText, item)

  // 替换文本节点
  if (beforeText) {
    parent.insertBefore(document.createTextNode(beforeText), node)
  }
  parent.insertBefore(highlightEl, node)
  if (afterText) {
    parent.insertBefore(document.createTextNode(afterText), node)
  }
  parent.removeChild(node)

  console.log('✅ 基于位置高亮成功')
}

/**
 * 基于文本匹配高亮（降级方案）
 */
const highlightByTextMatch = (containerEl: HTMLElement, item: InsightHistoryItem) => {
  // ... 现有的文本匹配逻辑
}
```

---

### 步骤 4: 修改详情弹窗添加继续聊天按钮

**文件**: `frontend/app/components/InsightHistoryModal.vue`

在弹窗底部添加按钮：

```vue
<template>
  <Transition ...>
    <div v-if="selectedItem" ...>
      <!-- 头部 -->
      <div class="p-6 border-b ...">...</div>

      <!-- 内容 -->
      <div class="p-6 overflow-y-auto ...">
        <!-- ... 现有内容 -->
      </div>

      <!-- 底部操作按钮 -->
      <div class="p-6 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
        <button
          @click="close"
          class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
        >
          关闭
        </button>

        <button
          @click="handleContinueChat"
          class="px-6 py-2 bg-gradient-to-r from-orange-500 to-amber-600 text-white text-sm rounded-lg hover:from-orange-600 hover:to-amber-700 transition-all shadow-md flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          继续聊天
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
// ... 现有代码

const emit = defineEmits<{
  close: []
  continueChat: [item: InsightHistoryItem]
}>()

const handleContinueChat = () => {
  emit('continueChat', props.selectedItem!)
}
</script>
```

---

## 🧪 完整测试流程

### 1. 测试位置保存

1. 登录后输入文章，点击"开始阅读"
2. 控制台应该显示：`✅ 文章已保存, ID: XXX`
3. 选中一段文字（比如第100-150字符）
4. 控制台应该显示：`📍 选中位置: 100 - 150`
5. 提问并获得回答
6. 控制台应该显示：`✅ 洞察已保存到历史`

### 2. 测试回放高亮

1. 刷新页面或重新打开文章
2. 点击"历史洞察(1)"按钮
3. 之前选中的文字应该显示**橙色下划线**
4. 高亮位置应该**精确**（基于位置信息）

### 3. 测试继续聊天

1. 点击橙色标注，弹出详情卡片
2. 查看历史对话内容
3. 点击"继续聊天"按钮
4. 卡片关闭，意图按钮面板打开
5. 可以针对同一段文字继续提问

---

## 🎯 核心改进点

### 改进1: 精确位置保存 ✅
- 保存 `selected_start` 和 `selected_end`
- 基于文章纯文本的字符索引

### 改进2: 优先位置匹配 ✅
- 优先使用位置信息高亮
- 文本匹配作为降级方案

### 改进3: 继续聊天功能 ✅
- 点击"继续聊天"恢复选中状态
- 可以针对同一段文字继续提问
- 形成完整的对话历史

---

## 📊 数据流程图

```
用户选中文字
    ↓
计算在文章中的位置 (start: 100, end: 150)
    ↓
提问并获得洞察
    ↓
保存到数据库：
  - selected_text: "这是一段文字"
  - selected_start: 100
  - selected_end: 150
  - insight: "AI的回答"
    ↓
重新打开文章
    ↓
加载洞察历史
    ↓
基于位置精确高亮 (100-150字符)
    ↓
点击高亮 → 显示历史对话
    ↓
点击"继续聊天" → 恢复选中状态 → 可继续提问
```

---

## ⚠️ 注意事项

1. **文章内容不变**: 如果文章内容被编辑，位置信息会失效
2. **降级处理**: 位置信息失败时自动降级到文本匹配
3. **跨节点处理**: 当前版本不支持跨多个DOM节点的高亮

---

按照这个指南完成集成后，就能实现完整的"基于位置的洞察回放 + 继续聊天"功能了！
