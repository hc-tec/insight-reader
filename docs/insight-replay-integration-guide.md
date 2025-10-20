# 洞察回放功能 - 集成指南

## 完成状态

✅ 后端 API 已完成
✅ Composable 已创建
✅ 组件已创建

## 📝 剩余集成步骤（由用户或我下次完成）

### 1. 修改 `frontend/app/pages/index.vue`

在 `<template>` 中添加（在 `<HistoryPanel>` 之后）：

```vue
<!-- 洞察回放按钮 -->
<InsightReplayButton
  v-if="isReading && currentArticleId && insightHistory.length > 0"
  :insight-count="insightHistory.length"
/>

<!-- 洞察详情弹窗 -->
<InsightHistoryModal
  :selected-item="selectedHistoryItem"
  @close="selectHistoryItem(null)"
/>
```

在 `<script setup>` 中添加：

```typescript
// 洞察回放
const { insightHistory, selectedHistoryItem, loadInsightHistory, clearReplayState, selectHistoryItem } = useInsightReplay()
const currentArticleId = useState<number | null>('current-article-id', () => null)
const config = useRuntimeConfig()
const { user } = useAuth()

// 修改 handleArticleSubmit - 立即保存文章
const handleArticleSubmit = async (articleContent: string) => {
  setArticle(articleContent)

  // 立即保存文章
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
      console.log('✅ 文章已保存:', response.article.id)

      // 如果是已存在的文章，加载洞察历史
      if (!response.article.is_new) {
        await loadInsightHistory(response.article.id, user.value.id)
      }
    } catch (error) {
      console.error('❌ 保存文章失败:', error)
    }
  }
}

// 文章ID变化时加载洞察历史
watch(() => currentArticleId.value, async (articleId) => {
  if (articleId && user.value?.id) {
    await loadInsightHistory(articleId, user.value.id)
  }
})

// 页面卸载时清理
onUnmounted(() => {
  clearReplayState()
})
```

---

### 2. 修改 `frontend/app/composables/useInsightGenerator.ts`

在 `generate()` 函数成功后添加保存逻辑：

```typescript
export const useInsightGenerator = () => {
  const config = useRuntimeConfig()
  const { user } = useAuth()
  const currentArticleId = useState<number | null>('current-article-id', () => null)

  const generate = async (request: InsightRequest) => {
    // ... 现有的生成逻辑

    // 生成成功后保存到历史
    if (currentInsight.value && currentArticleId.value && user.value?.id) {
      try {
        await $fetch(`${config.public.apiBase}/api/v1/insights/history`, {
          method: 'POST',
          body: {
            article_id: currentArticleId.value,
            user_id: user.value.id,
            selected_text: request.selected_text,
            selected_start: null,  // TODO: 计算位置
            selected_end: null,
            context_before: null,  // TODO: 提取上下文
            context_after: null,
            intent: request.intent,
            question: request.custom_question,
            insight: currentInsight.value,
            reasoning: currentReasoning.value
          }
        })

        console.log('✅ 洞察已保存到历史')

        // 重新加载历史列表
        const { loadInsightHistory } = useInsightReplay()
        await loadInsightHistory(currentArticleId.value, user.value.id)
      } catch (error) {
        console.error('❌ 保存洞察历史失败:', error)
      }
    }
  }

  return { generate, currentInsight, currentReasoning, isGenerating, error }
}
```

---

### 3. 添加 CSS 样式到 `ArticlePane.vue`

在 `<style>` 中添加：

```css
/* 洞察回放高亮样式 */
.article-content :deep(.insight-replay-highlight) {
  border-bottom: 3px solid #f97316;
  background-color: rgba(249, 115, 22, 0.1);
  cursor: pointer;
  padding: 0.1em 0.2em;
  border-radius: 0.25em;
  transition: all 0.2s ease;
}

.article-content :deep(.insight-replay-highlight:hover) {
  background-color: rgba(249, 115, 22, 0.2);
  box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2);
}
```

---

## 🧪 测试步骤

### 测试场景一：新文章
1. 登录后输入新文章，点击"开始阅读"
2. 检查浏览器控制台：应该看到 "✅ 文章已保存"
3. 选中一段文字，提问
4. 查看 AI 回答后，控制台应该显示 "✅ 洞察已保存到历史"
5. 右下角应该出现 "历史洞察 (1)" 按钮

### 测试场景二：回放功能
1. 点击 "历史洞察 (1)" 按钮
2. 之前提问的文字应该显示橙色下划线
3. 点击橙色标注，弹出详情卡片
4. 卡片显示：选中文本、问题、AI回答
5. 点击关闭，卡片消失
6. 再次点击回放按钮，标注消失

### 测试场景三：历史文章
1. 从"阅读历史"页面重新打开之前的文章
2. 文章加载后，右下角自动显示 "历史洞察 (X)" 按钮
3. 点击查看所有历史标注

---

## ⚠️ 注意事项

1. **数据库迁移**：运行应用前需要执行数据库迁移创建 `insight_history` 表
2. **登录状态**：洞察保存功能需要用户登录
3. **性能**：如果洞察记录很多（100+），可能需要优化渲染
4. **冲突处理**：回放模式下自动跳过元视角高亮和火花标注

---

## 📄 相关文件清单

### 后端
- ✅ `backend/app/models/models.py` - 添加 InsightHistory 模型
- ✅ `backend/app/api/insight_history.py` - 新建 API 路由
- ✅ `backend/app/main.py` - 注册路由

### 前端
- ✅ `frontend/app/composables/useInsightReplay.ts` - 新建
- ✅ `frontend/app/components/InsightReplayButton.vue` - 新建
- ✅ `frontend/app/components/InsightHistoryModal.vue` - 新建
- 🚧 `frontend/app/pages/index.vue` - 需要修改
- 🚧 `frontend/app/composables/useInsightGenerator.ts` - 需要修改
- 🚧 `frontend/app/components/ArticlePane.vue` - 需要添加样式

### 文档
- ✅ `docs/insight-replay-feature-design.md` - 完整设计文档
- ✅ `docs/insight-replay-progress.md` - 进度追踪
- ✅ `docs/insight-replay-integration-guide.md` - 本文档

---

## 🎯 核心价值

1. **自动保存**：用户开始阅读时自动保存文章
2. **记录思考**：每次 AI 洞察自动记录，无需用户操作
3. **回放功能**：橙色标注清晰展示历史提问位置
4. **完整对话**：点击标注查看完整的问答历史

现在所有关键代码都已完成，只需按照本指南进行集成即可！
