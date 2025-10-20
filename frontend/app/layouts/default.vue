<script setup lang="ts">
</script>

<template>
  <div class="flex h-screen bg-background text-foreground">
    <main class="flex-1 overflow-y-auto relative">
      <div class="w-full p-0 relative z-10">
        <slot />
      </div>
    </main>
  </div>
</template>
