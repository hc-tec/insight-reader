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

    <!-- 折叠/展开按钮 -->
    <button
      @click="togglePanel"
      class="fixed right-4 bottom-8 z-50 p-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 group"
      :class="{ 'right-[600px]': isExpanded }"
      :title="isExpanded ? '收起AI洞察' : '展开AI洞察'"
    >
      <svg
        class="w-5 h-5 transition-transform duration-200"
        :class="{ 'rotate-180': !isExpanded }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
      </svg>
      <span class="absolute right-full mr-3 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-gray-900 text-white text-sm rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
        {{ isExpanded ? '收起AI洞察' : '展开AI洞察' }}
      </span>
    </button>
  </div>
</template>

<script setup lang="ts">
const isExpanded = ref(true)

const togglePanel = () => {
  isExpanded.value = !isExpanded.value
}
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
