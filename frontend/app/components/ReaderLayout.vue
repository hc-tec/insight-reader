<template>
  <div class="flex h-[calc(100vh-64px)]">
    <!-- 左侧：文章面板 -->
    <div class="flex-1 overflow-auto relative">
      <!-- 装饰性渐变 -->
      <div class="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <slot name="left" />
    </div>

    <!-- 分隔线 - 只在展开时显示 -->
    <div
      v-show="isExpanded"
      class="w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent shadow-sm"
    ></div>

    <!-- 右侧：洞察面板 - 可折叠 -->
    <transition name="slide-fade">
      <div
        v-show="isExpanded"
        class="w-[580px] overflow-auto relative bg-gradient-to-br from-white via-slate-50/30 to-white"
      >
        <!-- 装饰性网格 -->
        <div class="absolute inset-0 bg-[radial-gradient(#e5e7eb_0.5px,transparent_0.5px)] [background-size:12px_12px] opacity-20 pointer-events-none"></div>

        <div class="relative z-10">
          <slot name="right" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
// 使用全局状态，与父组件共享
const isExpanded = useState('insight-panel-expanded', () => false)

const togglePanel = () => {
  isExpanded.value = !isExpanded.value
}

// 暴露方法和状态给父组件
defineExpose({
  togglePanel,
  isPanelExpanded: () => isExpanded.value
})
</script>

<style scoped>
/* 自定义滚动条 - 更细腻的设计 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, rgba(16, 185, 129, 0.3), rgba(20, 184, 166, 0.3));
  border-radius: 10px;
  border: 2px solid transparent;
  background-clip: content-box;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, rgba(16, 185, 129, 0.5), rgba(20, 184, 166, 0.5));
  background-clip: content-box;
}

/* 滑动淡入淡出动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
