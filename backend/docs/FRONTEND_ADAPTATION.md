# 前端异步适配指南

## 概述

后端已完成异步重构，所有LLM分析接口现在采用"立即返回 + SSE通知"模式。前端需要相应调整以正确处理异步响应。

---

## 需要修改的文件

### 1. `frontend/app/pages/index.vue`

#### ❌ 需要删除的代码

**删除所有 `/api/v1/thinking-lens/apply` 调用**:

```typescript
// ❌ 删除这些代码
await $fetch(`${config.public.apiBase}/api/v1/thinking-lens/apply`, {
  method: 'POST',
  body: {
    meta_analysis_id: metaResponse.meta_analysis.id,
    lens_type: 'argument_structure',
    full_text: articleContent
  }
})
```

**删除同步等待逻辑**:

```typescript
// ❌ 删除所有这种同步等待分析完成的代码
const result = await analyzeArticle(...)  // 不再阻塞等待
```

#### ✅ 需要添加/修改的代码

**1. 处理 pending 响应**:

```typescript
// 修改保存文章的逻辑
const response = await $fetch(`${config.public.apiBase}/api/v1/articles/save-with-analysis`, {
  method: 'POST',
  body: {
    title: title.value || '未命名文章',
    content: articleContent,
    user_id: user.value.id
  }
})

currentArticleId.value = response.article.id

// 检查分析状态
if (response.analysis.status === 'completed') {
  // 已有分析结果，立即加载
  const reportResponse = await $fetch(
    `${config.public.apiBase}/api/v1/articles/${response.article.id}/analysis-report`
  )
  analysisReport.value = reportResponse.report_data
  await renderSparks(reportResponse.report_data)
  console.log('✨ 火花已渲染（来自缓存）')

} else if (response.analysis.status === 'pending') {
  // 等待SSE通知
  console.log('🔄 分析已提交，等待完成通知...', response.analysis.task_id)
  // SSE事件处理器会自动处理
}
```

**2. 修改元视角分析调用**:

```typescript
// 自动触发元视角分析
if (prefs.auto_meta_analysis) {
  console.log('🔍 自动触发元视角分析...')

  const metaResponse = await $fetch(`${config.public.apiBase}/api/v1/meta-analysis/analyze`, {
    method: 'POST',
    body: {
      title: title.value || '未命名文章',
      author: '未知作者',
      full_text: articleContent,
      user_id: user.value.id
    }
  })

  if (metaResponse.status === 'pending') {
    console.log('🔄 元视角分析已提交，任务ID:', metaResponse.task_id)
    // 等待SSE通知
  } else if (metaResponse.status === 'completed') {
    console.log('✅ 元视角分析完成（来自缓存）')
    // 立即更新UI
  }
}
```

**3. 删除自动触发透镜分析**:

```typescript
// ❌ 删除所有自动触发透镜的代码
// 因为透镜分析应该只在用户手动点击时触发
// 且必须通过 /api/v1/articles/{id}/thinking-lens/{type} 接口调用

// ❌ 删除这段
if (prefs.auto_argument_lens) {
  // ... 删除整个 auto_argument_lens 代码块
}

// ❌ 删除这段
if (prefs.auto_stance_lens) {
  // ... 删除整个 auto_stance_lens 代码块
}
```

---

### 2. `frontend/app/composables/useAnalysisSSE.ts`

#### ✅ 增强SSE事件处理

**修改事件监听器以处理所有任务类型**:

```typescript
// 修改 task_completed 事件处理
eventSource.addEventListener('task_completed', async (event: MessageEvent) => {
  const data = JSON.parse(event.data)
  console.log('[SSE] 任务完成:', data.task_type, data.task_id)

  // 文章分析完成
  if (data.task_type === 'article_analysis') {
    if (callbacks.onAnalysisComplete) {
      callbacks.onAnalysisComplete(data.result.article_id)
    }
  }

  // 元视角分析完成
  else if (data.task_type === 'meta_analysis') {
    if (callbacks.onMetaAnalysisComplete) {
      callbacks.onMetaAnalysisComplete(data.result.article_id, data.result.meta_analysis)
    }
  }

  // 思维透镜完成
  else if (data.task_type.startsWith('thinking_lens_')) {
    const lensType = data.task_type.replace('thinking_lens_', '')
    if (callbacks.onLensComplete) {
      callbacks.onLensComplete(lensType, data.result.lens_result)
    }
  }
})

// 添加任务失败事件监听
eventSource.addEventListener('task_failed', async (event: MessageEvent) => {
  const data = JSON.parse(event.data)
  console.error('[SSE] 任务失败:', data.task_type, data.error)

  // 通知用户任务失败
  if (callbacks.onTaskFailed) {
    callbacks.onTaskFailed(data.task_type, data.error)
  }
})
```

**添加新的回调类型**:

```typescript
interface AnalysisCallbacks {
  onAnalysisComplete?: (articleId: number) => void | Promise<void>
  onMetaAnalysisComplete?: (articleId: number, metaAnalysis: any) => void | Promise<void>
  onLensComplete?: (lensType: string, lensResult: any) => void | Promise<void>
  onTaskFailed?: (taskType: string, error: string) => void | Promise<void>
}
```

---

### 3. `frontend/app/composables/useThinkingLens.ts`

#### ✅ 修改透镜加载逻辑

```typescript
/**
 * 通过文章ID加载透镜分析（异步版本）
 */
const loadLens = async (
  articleId: number,
  lensType: LensType,
  forceReanalyze: boolean = false
) => {
  loadingLenses.value.add(lensType)
  lensError.value = null

  try {
    const response = await $fetch<{
      status: string
      lens_result: LensResult | null
      task_id: string | null
    }>(
      `${config.public.apiBase}/api/v1/articles/${articleId}/thinking-lens/${lensType}`,
      {
        params: { force_reanalyze: forceReanalyze }
      }
    )

    if (response.status === 'completed') {
      // 立即返回结果
      lensResults.value.set(lensType, response.lens_result!)
      console.log(`✅ ${lensType} 透镜加载成功（来自缓存）`)
      return response.lens_result

    } else if (response.status === 'pending') {
      // 等待SSE通知
      console.log(`🔄 ${lensType} 透镜分析已提交，任务ID: ${response.task_id}`)
      // SSE回调会自动处理结果
      return null
    }

  } catch (error: any) {
    console.error('❌ 透镜加载失败:', error)
    lensError.value = error.data?.detail || error.message || '透镜加载失败'
    throw error
  } finally {
    loadingLenses.value.delete(lensType)
  }
}
```

**在页面中监听透镜完成事件**:

```typescript
// 在 index.vue 中添加透镜完成回调
onLensComplete(async (lensType, lensResult) => {
  console.log(`📬 收到${lensType}透镜完成通知`)

  // 更新透镜结果
  lensResults.value.set(lensType, lensResult)

  // 应用高亮
  const containerEl = document.querySelector('.article-content')
  if (containerEl && enabledLenses.value.has(lensType)) {
    await applyHighlights(containerEl, lensType, lensResult)
    console.log(`✨ ${lensType} 透镜高亮已应用`)
  }
})
```

---

### 4. `frontend/app/pages/index.vue` - SSE回调完整示例

```typescript
// 注册所有SSE回调
onMounted(() => {
  // 文章分析完成
  onAnalysisComplete(currentArticleId.value, async (articleId) => {
    console.log(`📬 收到文章分析完成通知，ID: ${articleId}`)

    try {
      const reportResponse = await $fetch(
        `${config.public.apiBase}/api/v1/articles/${articleId}/analysis-report`
      )

      analysisReport.value = reportResponse.report_data
      await renderSparks(reportResponse.report_data)

      const sparkCount = (reportResponse.report_data.concept_sparks?.length || 0) +
                         (reportResponse.report_data.argument_sparks?.length || 0)

      console.log(`✨ 火花已渲染，发现 ${sparkCount} 个洞察点`)
    } catch (error) {
      console.error('❌ 获取分析报告失败:', error)
    }
  })

  // 元视角分析完成
  onMetaAnalysisComplete(async (articleId, metaAnalysis) => {
    console.log(`📬 收到元视角分析完成通知，ID: ${articleId}`)
    // 更新元视角UI
    metaAnalysisData.value = metaAnalysis
  })

  // 透镜分析完成
  onLensComplete(async (lensType, lensResult) => {
    console.log(`📬 收到${lensType}透镜完成通知`)

    const containerEl = document.querySelector('.article-content')
    if (containerEl) {
      await applyLensHighlights(containerEl, lensType, lensResult)
      console.log(`✨ ${lensType} 透镜高亮已应用`)
    }
  })

  // 任务失败通知
  onTaskFailed((taskType, error) => {
    console.error(`❌ ${taskType} 任务失败:`, error)
    // 显示错误提示给用户
    showErrorToast(`分析失败: ${error}`)
  })
})
```

---

## API响应格式变化

### 旧版本（同步）

```json
{
  "status": "success",
  "result": {
    "analysis_data": {...}
  }
}
```

### 新版本（异步）

#### 已完成（有缓存）

```json
{
  "status": "completed",
  "lens_result": {...},  // 或 meta_analysis, report_data
  "task_id": null
}
```

#### 待处理（新任务）

```json
{
  "status": "pending",
  "lens_result": null,
  "task_id": "uuid-xxx-xxx"
}
```

---

## 用户体验优化

### 1. 加载状态提示

```vue
<!-- 显示分析进行中 -->
<div v-if="analysisStatus === 'pending'" class="loading-indicator">
  <SpinnerIcon />
  <p>AI正在深度分析文章...</p>
</div>

<!-- 显示透镜分析进行中 -->
<div v-if="loadingLenses.has('argument_structure')" class="loading-indicator">
  <SpinnerIcon />
  <p>正在应用论证结构透镜...</p>
</div>
```

### 2. 进度反馈

```typescript
// 可以通过定时器模拟进度
const showAnalysisProgress = () => {
  let progress = 0
  const interval = setInterval(() => {
    progress += 10
    if (progress >= 90) {
      clearInterval(interval)
      // 等待实际完成
    } else {
      updateProgressBar(progress)
    }
  }, 1000)
}
```

### 3. 错误处理

```typescript
onTaskFailed((taskType, error) => {
  const messages = {
    'article_analysis': '文章分析失败，请稍后重试',
    'meta_analysis': '元视角分析失败',
    'thinking_lens_argument_structure': '论证透镜分析失败',
    'thinking_lens_author_stance': '意图透镜分析失败'
  }

  const message = messages[taskType] || '分析失败'
  showErrorToast(`${message}: ${error}`)
})
```

---

## 测试清单

### ✅ 文章分析

- [ ] 上传新文章后立即返回（<100ms）
- [ ] 看到"分析中"提示
- [ ] SSE收到分析完成事件
- [ ] 火花正确渲染

### ✅ 元视角分析

- [ ] 自动触发元视角分析（如果启用）
- [ ] 立即返回pending状态
- [ ] SSE收到完成事件
- [ ] 元视角卡片正确显示

### ✅ 思维透镜

- [ ] 点击透镜按钮立即响应
- [ ] 显示加载状态
- [ ] SSE收到完成事件
- [ ] 高亮正确应用

### ✅ 错误处理

- [ ] 网络断线后自动重连SSE
- [ ] 任务失败时显示错误提示
- [ ] 可以重试失败的任务

---

## 常见问题

### Q: SSE连接何时建立？
A: 用户登录后立即建立SSE连接，并在整个会话期间保持。

### Q: 如果页面刷新怎么办？
A: 重新建立SSE连接。已完成的任务结果保存在数据库中，会立即返回completed状态。

### Q: 多个标签页会建立多个SSE连接吗？
A: 是的，但不影响功能。每个连接都会收到相同的事件。

### Q: 如何避免重复渲染？
A: 通过检查 `analysisReport.value` 等状态变量，只在首次收到结果时渲染。

---

## 迁移检查清单

- [ ] ✅ 删除所有 `/api/v1/thinking-lens/apply` 调用
- [ ] ✅ 修改文章保存逻辑以处理pending响应
- [ ] ✅ 修改元视角分析调用
- [ ] ✅ 删除自动触发透镜分析代码
- [ ] ✅ 修改透镜加载逻辑
- [ ] ✅ 添加SSE任务完成回调
- [ ] ✅ 添加加载状态UI
- [ ] ✅ 添加错误处理
- [ ] ✅ 测试所有场景

---

## 总结

前端异步适配核心要点：

1. **不要等待**: 所有分析接口调用后不再await结果
2. **检查状态**: 根据status字段判断是completed还是pending
3. **监听SSE**: 通过SSE事件获取异步任务结果
4. **删除旧代码**: 移除`/api/v1/thinking-lens/apply`调用
5. **优化体验**: 添加加载状态、进度反馈、错误处理

完成这些修改后，前端将完全适配异步后端，用户体验将大幅提升！
