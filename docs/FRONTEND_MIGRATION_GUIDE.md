# 前端异步 API 迁移指南

## 概述

后端已完成异步重构，所有分析 API 现在使用任务管理器和 SSE 推送结果。本指南帮助前端快速迁移到新版异步 API。

---

## 🎯 变更概述

### 旧版工作流

```
提交请求 → 等待 30-60 秒 → 收到结果（或超时）
```

### 新版工作流

```
1. 提交请求 → 立即收到 task_id (< 1秒)
2. 订阅 SSE 事件流 → 实时接收进度更新
3. 任务完成后获取完整结果
```

---

## 📡 核心改动

### 1. 统一分析 API

#### 旧版

```typescript
// 提交后等待完成
const response = await $fetch('/api/v1/articles/save-with-analysis', {
  method: 'POST',
  body: {
    title,
    content,
    user_id
  },
  timeout: 60000 // 60秒超时
});

// 直接获得结果
const { article, analysis } = response;
if (analysis.status === 'completed') {
  // 使用结果
}
```

#### 新版

```typescript
// 1. 提交任务
const response = await $fetch('/api/v1/articles/save-with-analysis', {
  method: 'POST',
  body: {
    title,
    content,
    user_id
  }
  // 无需设置 timeout
});

const { article, analysis } = response;

if (analysis.status === 'completed') {
  // 已有结果，直接使用
  await fetchAndDisplayReport(article.id);
} else if (analysis.task_id) {
  // 2. 订阅 SSE 事件
  subscribeToTaskProgress(analysis.task_id, article.id);
}
```

---

## 🛠️ 实现步骤

### 步骤 1: 创建 SSE 事件订阅 Composable

创建 `composables/useTaskProgress.ts`:

```typescript
import { ref, onUnmounted } from 'vue';

export interface TaskEvent {
  type: string;
  data: any;
  timestamp: string;
}

export interface TaskProgress {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  result?: any;
  error?: string;
}

export function useTaskProgress() {
  const eventSource = ref<EventSource | null>(null);
  const progress = ref<TaskProgress>({
    status: 'pending',
    progress: 0,
    message: ''
  });

  const subscribe = (
    taskId: string,
    onComplete?: (result: any) => void,
    onError?: (error: string) => void
  ) => {
    // 创建 EventSource 连接
    eventSource.value = new EventSource(
      `/api/v1/tasks/${taskId}/events`
    );

    // 监听 task_created 事件
    eventSource.value.addEventListener('task_created', (e) => {
      const event: TaskEvent = JSON.parse(e.data);
      progress.value = {
        status: 'pending',
        progress: 0,
        message: '任务已创建'
      };
    });

    // 监听 task_started 事件
    eventSource.value.addEventListener('task_started', (e) => {
      const event: TaskEvent = JSON.parse(e.data);
      progress.value = {
        status: 'processing',
        progress: 10,
        message: '分析开始...'
      };
    });

    // 监听 progress_update 事件
    eventSource.value.addEventListener('progress_update', (e) => {
      const event: TaskEvent = JSON.parse(e.data);
      progress.value = {
        status: 'processing',
        progress: event.data.progress,
        message: event.data.message
      };
    });

    // 监听 task_completed 事件
    eventSource.value.addEventListener('task_completed', (e) => {
      const event: TaskEvent = JSON.parse(e.data);
      progress.value = {
        status: 'completed',
        progress: 100,
        message: '分析完成',
        result: event.data.result
      };

      // 关闭连接
      eventSource.value?.close();
      eventSource.value = null;

      // 回调
      if (onComplete) {
        onComplete(event.data.result);
      }
    });

    // 监听 task_failed 事件
    eventSource.value.addEventListener('task_failed', (e) => {
      const event: TaskEvent = JSON.parse(e.data);
      progress.value = {
        status: 'failed',
        progress: 0,
        message: '分析失败',
        error: event.data.error
      };

      // 关闭连接
      eventSource.value?.close();
      eventSource.value = null;

      // 回调
      if (onError) {
        onError(event.data.error);
      }
    });

    // 监听错误
    eventSource.value.onerror = (error) => {
      console.error('SSE 连接错误:', error);
      progress.value = {
        status: 'failed',
        progress: 0,
        message: 'SSE 连接失败',
        error: 'Network error'
      };

      eventSource.value?.close();
      eventSource.value = null;

      if (onError) {
        onError('Network error');
      }
    };
  };

  const cancel = async (taskId: string) => {
    try {
      await $fetch(`/api/v1/tasks/${taskId}/cancel`, {
        method: 'POST'
      });
      eventSource.value?.close();
      eventSource.value = null;
    } catch (error) {
      console.error('取消任务失败:', error);
    }
  };

  // 组件卸载时清理
  onUnmounted(() => {
    eventSource.value?.close();
    eventSource.value = null;
  });

  return {
    progress,
    subscribe,
    cancel
  };
}
```

### 步骤 2: 在组件中使用

#### 统一分析示例

```vue
<script setup lang="ts">
import { ref } from 'vue';
import { useTaskProgress } from '~/composables/useTaskProgress';

const { progress, subscribe } = useTaskProgress();
const isAnalyzing = ref(false);
const analysisResult = ref(null);

async function analyzeArticle(title: string, content: string) {
  isAnalyzing.value = true;

  try {
    // 1. 提交分析任务
    const response = await $fetch('/api/v1/articles/save-with-analysis', {
      method: 'POST',
      body: {
        title,
        content,
        user_id: 1
      }
    });

    const { article, analysis } = response;

    if (analysis.status === 'completed') {
      // 已有结果，直接获取
      const report = await fetchReport(article.id);
      analysisResult.value = report;
      isAnalyzing.value = false;
    } else if (analysis.task_id) {
      // 2. 订阅任务进度
      subscribe(
        analysis.task_id,
        // 完成回调
        async (result) => {
          console.log('分析完成:', result);
          // 获取完整报告
          const report = await fetchReport(article.id);
          analysisResult.value = report;
          isAnalyzing.value = false;
        },
        // 错误回调
        (error) => {
          console.error('分析失败:', error);
          alert(`分析失败: ${error}`);
          isAnalyzing.value = false;
        }
      );
    }
  } catch (error) {
    console.error('提交任务失败:', error);
    alert('提交任务失败');
    isAnalyzing.value = false;
  }
}

async function fetchReport(articleId: number) {
  const response = await $fetch(
    `/api/v1/articles/${articleId}/analysis-report`
  );
  return response;
}
</script>

<template>
  <div>
    <!-- 进度条 -->
    <div v-if="isAnalyzing" class="progress-container">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${progress.progress}%` }"
        ></div>
      </div>
      <p class="progress-message">
        {{ progress.message || '处理中...' }}
        ({{ progress.progress }}%)
      </p>
    </div>

    <!-- 分析结果 -->
    <div v-if="analysisResult">
      <!-- 显示分析结果 -->
    </div>
  </div>
</template>

<style scoped>
.progress-container {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(to right, #3b82f6, #10b981);
  transition: width 0.3s ease;
}

.progress-message {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}
</style>
```

#### 元分析示例

```typescript
async function analyzeMetaInfo(article: Article) {
  const { progress, subscribe } = useTaskProgress();

  // 1. 提交元分析任务
  const response = await $fetch('/api/v1/meta-analysis/analyze', {
    method: 'POST',
    body: {
      title: article.title,
      author: article.author,
      full_text: article.content,
      language: 'zh'
    }
  });

  const { task_id, article_id } = response;

  if (task_id) {
    // 2. 订阅进度
    subscribe(
      task_id,
      async (result) => {
        // 获取元分析结果
        const metaAnalysis = await $fetch(
          `/api/v1/meta-analysis/${article_id}`
        );
        console.log('元分析完成:', metaAnalysis);
      },
      (error) => {
        console.error('元分析失败:', error);
      }
    );
  }
}
```

#### 思维透镜示例

```typescript
async function applyThinkingLens(articleId: number, lensType: string) {
  const { progress, subscribe } = useTaskProgress();

  // 1. 提交透镜分析任务
  const response = await $fetch(
    `/api/v1/articles/${articleId}/thinking-lens/${lensType}`
  );

  const { status, task_id, lens_result } = response;

  if (status === 'completed' && lens_result) {
    // 已有结果
    displayLensResult(lens_result);
  } else if (task_id) {
    // 2. 订阅进度
    subscribe(
      task_id,
      async (result) => {
        // 显示透镜结果
        displayLensResult(result.lens_result);
      },
      (error) => {
        console.error('透镜分析失败:', error);
      }
    );
  }
}
```

---

## 🎨 UI 组件示例

### 进度指示器组件

创建 `components/TaskProgress.vue`:

```vue
<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
}>();

const progressColor = computed(() => {
  switch (props.status) {
    case 'processing':
      return 'bg-blue-500';
    case 'completed':
      return 'bg-green-500';
    case 'failed':
      return 'bg-red-500';
    default:
      return 'bg-gray-500';
  }
});

const statusIcon = computed(() => {
  switch (props.status) {
    case 'processing':
      return '⏳';
    case 'completed':
      return '✅';
    case 'failed':
      return '❌';
    default:
      return '⏸️';
  }
});
</script>

<template>
  <div class="task-progress">
    <div class="flex items-center gap-2 mb-2">
      <span class="text-2xl">{{ statusIcon }}</span>
      <span class="text-sm font-medium text-gray-700">
        {{ message || '处理中...' }}
      </span>
    </div>

    <div class="progress-bar">
      <div
        class="progress-fill"
        :class="progressColor"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>

    <div class="text-xs text-gray-500 mt-1 text-right">
      {{ progress }}%
    </div>
  </div>
</template>

<style scoped>
.task-progress {
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}
</style>
```

使用:

```vue
<TaskProgress
  :status="progress.status"
  :progress="progress.progress"
  :message="progress.message"
/>
```

---

## 🔄 迁移检查清单

### 必须修改的文件

- [ ] `composables/useTaskProgress.ts` - 创建任务进度订阅 composable
- [ ] `components/TaskProgress.vue` - 创建进度指示器组件
- [ ] `pages/reader/index.vue` - 更新统一分析调用
- [ ] `composables/useMetaAnalysis.ts` - 更新元分析调用
- [ ] `composables/useThinkingLens.ts` - 更新思维透镜调用

### API 端点变更

| 功能 | 旧端点 | 新端点 | 变化 |
|------|-------|--------|-----|
| 统一分析 | `POST /api/v1/articles/save-with-analysis` | 同样 | 返回值增加 `task_id` |
| 元分析 | `POST /api/v1/meta-analysis/analyze` | 同样 | 返回值增加 `task_id` |
| 思维透镜 | `POST /api/v1/thinking-lens/apply` | 同样 | 返回值增加 `task_id` |
| 任务状态 | - | `GET /api/v1/tasks/{task_id}/status` | 新增 |
| SSE 事件 | - | `GET /api/v1/tasks/{task_id}/events` | 新增 |
| 取消任务 | - | `POST /api/v1/tasks/{task_id}/cancel` | 新增 |

---

## ⚠️ 常见陷阱

### 1. EventSource 不会自动关闭

```typescript
// ❌ 错误：忘记关闭连接
const eventSource = new EventSource('/api/v1/tasks/123/events');

// ✅ 正确：在完成或组件卸载时关闭
eventSource.addEventListener('task_completed', () => {
  eventSource.close();
});

onUnmounted(() => {
  eventSource?.close();
});
```

### 2. 重复订阅

```typescript
// ❌ 错误：每次渲染都创建新连接
watch(taskId, (newId) => {
  subscribe(newId);  // 可能导致多个连接
});

// ✅ 正确：先关闭旧连接
watch(taskId, (newId, oldId) => {
  if (eventSource.value) {
    eventSource.value.close();
  }
  subscribe(newId);
});
```

### 3. 错误处理不完整

```typescript
// ❌ 错误：只处理 task_failed 事件
eventSource.addEventListener('task_failed', handleError);

// ✅ 正确：同时处理网络错误
eventSource.addEventListener('task_failed', handleError);
eventSource.onerror = handleNetworkError;
```

---

## 🚀 性能优化

### 1. 使用单例 EventSource

```typescript
// 避免为同一个任务创建多个连接
const eventSourceCache = new Map<string, EventSource>();

function getEventSource(taskId: string): EventSource {
  if (!eventSourceCache.has(taskId)) {
    const source = new EventSource(`/api/v1/tasks/${taskId}/events`);
    eventSourceCache.set(taskId, source);

    source.addEventListener('task_completed', () => {
      source.close();
      eventSourceCache.delete(taskId);
    });

    source.addEventListener('task_failed', () => {
      source.close();
      eventSourceCache.delete(taskId);
    });
  }

  return eventSourceCache.get(taskId)!;
}
```

### 2. 延迟订阅

```typescript
// 只在用户查看页面时订阅
const { isVisible } = usePageVisibility();

watchEffect(() => {
  if (isVisible.value && taskId.value) {
    subscribe(taskId.value);
  } else {
    eventSource.value?.close();
  }
});
```

---

## 📚 参考资源

- [EventSource API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [Server-Sent Events 规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [后端异步重构指南](./backend/ASYNC_REFACTORING_GUIDE.md)

---

## ✅ 总结

通过这次迁移，前端将获得：

1. **更好的用户体验** - 实时进度反馈，不再有"黑盒"等待
2. **更高的可靠性** - 无超时限制，长任务也能完成
3. **更灵活的控制** - 可以取消任务、查询状态
4. **更好的性能** - 非阻塞请求，界面不会卡顿

关键步骤：
1. ✅ 创建 `useTaskProgress` composable
2. ✅ 在组件中订阅 SSE 事件
3. ✅ 显示进度 UI
4. ✅ 处理完成和错误事件
5. ✅ 组件卸载时清理连接
