<template>
  <div class="lens-annotation-card" :style="cardStyle">
    <!-- 卡片头部 -->
    <div class="annotation-header">
      <span class="annotation-icon">{{ lensIcon }}</span>
      <span class="annotation-type">{{ lensTypeLabel }}</span>
      <button
        @click="$emit('close')"
        class="close-btn"
        aria-label="关闭注解"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- 卡片内容 -->
    <div class="annotation-content">
      <p class="text-sm leading-relaxed">{{ annotation.annotationContent }}</p>
    </div>

    <!-- 展开/收起按钮 -->
    <button
      v-if="isCollapsible"
      @click="isExpanded = !isExpanded"
      class="expand-btn"
    >
      <span class="text-xs">{{ isExpanded ? '收起' : '展开详情' }}</span>
      <svg
        class="w-3 h-3 transition-transform"
        :class="{ 'rotate-180': isExpanded }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { LensAnnotation } from '~/composables/useLensAnnotation'

const props = defineProps<{
  annotation: LensAnnotation
  index: number
}>()

defineEmits<{
  close: []
}>()

const isExpanded = ref(false)

// 根据透镜类型显示不同图标
const lensIcon = computed(() => {
  return props.annotation.lensType === 'argument_structure' ? '📝' : '🎭'
})

const lensTypeLabel = computed(() => {
  return props.annotation.lensType === 'argument_structure' ? '论证结构' : '作者意图'
})

// 判断内容是否需要展开/收起
const isCollapsible = computed(() => {
  return props.annotation.annotationContent.length > 100
})
</script>

<style scoped>
.lens-annotation-card {
  position: relative;
  width: 100%;
  background: hsl(var(--popover));
  border: 1px solid hsl(var(--border));
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 12px;
  margin-bottom: 12px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.annotation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid hsl(var(--border));
}

.annotation-icon {
  font-size: 16px;
  line-height: 1;
}

.annotation-type {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: hsl(var(--foreground));
}

.close-btn {
  padding: 2px;
  border-radius: 4px;
  color: hsl(var(--muted-foreground));
  transition: all 0.2s;
}

.close-btn:hover {
  background: hsl(var(--muted));
  color: hsl(var(--foreground));
}

.annotation-content {
  color: hsl(var(--muted-foreground));
  margin-bottom: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.expand-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: hsl(var(--muted-foreground));
  transition: all 0.2s;
}

.expand-btn:hover {
  background: hsl(var(--muted));
  color: hsl(var(--foreground));
}

/* 自定义滚动条 */
.annotation-content::-webkit-scrollbar {
  width: 4px;
}

.annotation-content::-webkit-scrollbar-track {
  background: transparent;
}

.annotation-content::-webkit-scrollbar-thumb {
  background: hsl(var(--muted));
  border-radius: 2px;
}
</style>
