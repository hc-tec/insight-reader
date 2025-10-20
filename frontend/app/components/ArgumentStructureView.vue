<template>
  <div class="space-y-4">
    <!-- ∫¡êXÅ -->
    <Card>
      <CardHeader class="pb-3">
        <CardTitle class="text-sm flex items-center gap-2">
          <FileTextIcon class="w-4 h-4" />
          ∫¡êXÅ
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-sm text-gray-700 leading-relaxed">{{ annotations.summary }}</p>

        <!-- s.ﬂ -->
        <div v-if="annotations.key_insights && annotations.key_insights.length > 0" class="mt-4 space-y-2">
          <h4 class="text-xs font-semibold text-gray-600">s.—∞</h4>
          <ul class="space-y-1">
            <li
              v-for="(insight, index) in annotations.key_insights"
              :key="index"
              class="text-xs text-gray-600 flex items-start gap-2"
            >
              <CheckCircle2Icon class="w-3 h-3 text-emerald-600 mt-0.5 flex-shrink-0" />
              <span>{{ insight }}</span>
            </li>
          </ul>
        </div>

        <!-- ﬂ°·o -->
        <div v-if="annotations.statistics" class="mt-4 grid grid-cols-3 gap-3">
          <div class="text-center p-3 bg-blue-50 rounded-lg">
            <div class="text-xl font-bold text-blue-700">{{ annotations.statistics.claim_count || 0 }}</div>
            <div class="text-xs text-gray-600">8√; </div>
          </div>
          <div class="text-center p-3 bg-green-50 rounded-lg">
            <div class="text-xl font-bold text-green-700">{{ annotations.statistics.evidence_count || 0 }}</div>
            <div class="text-xs text-gray-600">/ë¡n</div>
          </div>
          <div class="text-center p-3 bg-amber-50 rounded-lg">
            <div class="text-xl font-bold text-amber-700">{{ formatRatio(annotations.statistics.claim_to_evidence_ratio) }}</div>
            <div class="text-xs text-gray-600">¡n‘ã</div>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- ∫¡A˛ -->
    <Card>
      <CardHeader class="pb-3">
        <CardTitle class="text-sm flex items-center gap-2">
          <NetworkIcon class="w-4 h-4" />
          ∫¡A
        </CardTitle>
        <CardDescription class="text-xs">π˚Ô(á‡-öM</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea class="h-[400px] pr-4">
          <div class="space-y-4">
            <!-- 	zè>:; å¡n -->
            <div
              v-for="(item, index) in sortedHighlights"
              :key="index"
              class="group"
            >
              <!-- ; aG -->
              <div
                v-if="item.category === 'claim'"
                class="relative pl-6 pb-4"
              >
                <!-- ﬁ•ø -->
                <div class="absolute left-3 top-0 bottom-0 w-px bg-blue-200"></div>
                <div class="absolute left-[0.6875rem] top-3 w-2.5 h-2.5 rounded-full bg-blue-500 border-2 border-white"></div>

                <!-- ÖπaG -->
                <div
                  @click="scrollToHighlight(item)"
                  class="ml-4 p-3 bg-blue-50 border border-blue-200 rounded-lg cursor-pointer hover:bg-blue-100 hover:shadow-md transition-all"
                >
                  <div class="flex items-start gap-2 mb-2">
                    <Badge variant="default" class="bg-blue-600 text-xs">;  {{ getClaimNumber(index) }}</Badge>
                  </div>
                  <p class="text-sm text-gray-800 leading-relaxed">{{ item.text }}</p>
                  <p class="text-xs text-gray-500 mt-2">{{ item.tooltip }}</p>
                </div>
              </div>

              <!-- ¡naG -->
              <div
                v-else-if="item.category === 'evidence'"
                class="relative pl-6 pb-4"
              >
                <!-- ﬁ•ø -->
                <div class="absolute left-3 top-0 bottom-0 w-px bg-green-200"></div>
                <div class="absolute left-[0.6875rem] top-3 w-2.5 h-2.5 rounded-full bg-green-500 border-2 border-white"></div>

                <!-- ÖπaG -->
                <div
                  @click="scrollToHighlight(item)"
                  class="ml-4 p-3 bg-green-50 border border-green-200 rounded-lg cursor-pointer hover:bg-green-100 hover:shadow-md transition-all"
                >
                  <div class="flex items-start gap-2 mb-2">
                    <Badge variant="default" class="bg-green-600 text-xs">¡n</Badge>
                  </div>
                  <p class="text-sm text-gray-800 leading-relaxed">{{ item.text }}</p>
                  <p class="text-xs text-gray-500 mt-2">{{ item.tooltip }}</p>
                </div>
              </div>
            </div>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { CheckCircle2Icon, FileTextIcon, NetworkIcon } from 'lucide-vue-next'
import type { Highlight, LensAnnotations } from '@/composables/useThinkingLens'

const props = defineProps<{
  highlights: Highlight[]
  annotations: LensAnnotations
}>()

// 	MníèÿÆ
const sortedHighlights = computed(() => {
  return [...props.highlights].sort((a, b) => a.start - b.start)
})

// <‘ã
const formatRatio = (ratio: number | undefined): string => {
  if (!ratio) return '0'
  return ratio.toFixed(1)
}

// ∑÷; ˜
const getClaimNumber = (index: number): number => {
  let claimCount = 0
  for (let i = 0; i <= index; i++) {
    if (sortedHighlights.value[i]?.category === 'claim') {
      claimCount++
    }
  }
  return claimCount
}

// ⁄®0ÿÆMn
const scrollToHighlight = (item: Highlight) => {
  // (á‡-Â~˘îÑÿÆC 
  const containerEl = document.getElementById('article-content-container')
  if (!containerEl) return

  // Â~@	+Âá,ÑÿÆC 
  const highlights = containerEl.querySelectorAll('.meta-view-highlight')
  for (const el of highlights) {
    if (el.textContent?.trim() === item.text.trim()) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })

      // ˚†4ˆÍ¡Hú
      el.classList.add('highlight-flash')
      setTimeout(() => {
        el.classList.remove('highlight-flash')
      }, 2000)

      break
    }
  }
}
</script>

<style scoped>
:global(.highlight-flash) {
  animation: flash 2s ease-in-out;
}

@keyframes flash {
  0%, 100% {
    box-shadow: none;
  }
  50% {
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.4);
  }
}
</style>
