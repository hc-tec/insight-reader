<template>
  <!-- 透镜注解模式不需要额外的 overlay 组件 -->
  <!-- 注解卡片会直接注入到 DOM 中作为高亮元素的子元素 -->
</template>

<script setup lang="ts">
// 这个组件现在只是一个占位符
// 实际的注解卡片由 useLensAnnotation composable 直接注入到 DOM
defineProps<{
  isActive: boolean
  annotations: any[]
}>()
</script>
