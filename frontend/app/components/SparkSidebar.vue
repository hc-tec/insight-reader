<template>
  <Sheet v-model:open="isOpen">
    <SheetContent side="right" class="w-[500px] sm:w-[540px] p-0 flex flex-col">
      <SheetHeader class="px-6 py-4 border-b bg-gradient-to-r from-emerald-50 to-teal-50">
        <SheetTitle>句子洞察</SheetTitle>
        <SheetDescription>
          {{ sparkCount }} 个发现
        </SheetDescription>
      </SheetHeader>

      <!-- 选中的句子 -->
      <div v-if="selectedSentence" class="px-6 py-4 bg-gray-50 border-b">
        <div class="flex items-start gap-2">
          <Badge variant="default" class="bg-emerald-500">{{ sentenceIndex }}</Badge>
          <p class="text-sm text-gray-700 leading-relaxed flex-1">{{ selectedSentence }}</p>
        </div>
      </div>

      <!-- 火花列表 -->
      <ScrollArea class="flex-1">
        <div class="p-6 space-y-4">
          <!-- 概念火花 -->
          <Card
            v-for="(spark, index) in conceptSparks"
            :key="`concept-${index}`"
            class="border-emerald-100 hover:shadow-md transition-shadow"
          >
            <CardHeader class="pb-3">
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                    <LightbulbIcon class="w-4 h-4 text-white" />
                  </div>
                  <Badge variant="secondary" class="text-emerald-600">核心概念</Badge>
                </div>
                <Badge variant="outline" class="gap-1">
                  <StarIcon class="w-3 h-3 text-amber-500 fill-amber-500" />
                  {{ spark.importance_score }}/10
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <CardTitle class="text-base mb-2">{{ spark.text }}</CardTitle>
              <CardDescription class="text-sm leading-relaxed">
                {{ spark.explanation_hint }}
              </CardDescription>
            </CardContent>
          </Card>

          <!-- 论证火花 -->
          <Card
            v-for="(spark, index) in argumentSparks"
            :key="`argument-${index}`"
            :class="{
              'border-blue-100': spark.type === 'claim',
              'border-green-100': spark.type === 'evidence',
              'border-amber-100': spark.type === 'transition'
            }"
            class="hover:shadow-md transition-shadow"
          >
            <CardHeader class="pb-3">
              <div class="flex items-center gap-2">
                <div
                  class="w-8 h-8 rounded-lg flex items-center justify-center"
                  :class="{
                    'bg-gradient-to-br from-blue-400 to-blue-600': spark.type === 'claim',
                    'bg-gradient-to-br from-green-400 to-green-600': spark.type === 'evidence',
                    'bg-gradient-to-br from-amber-400 to-amber-600': spark.type === 'transition'
                  }"
                >
                  <CheckCircle2Icon v-if="spark.type === 'claim'" class="w-4 h-4 text-white" />
                  <FileTextIcon v-else-if="spark.type === 'evidence'" class="w-4 h-4 text-white" />
                  <ChevronsRightIcon v-else class="w-4 h-4 text-white" />
                </div>
                <Badge
                  variant="secondary"
                  :class="{
                    'text-blue-600': spark.type === 'claim',
                    'text-green-600': spark.type === 'evidence',
                    'text-amber-600': spark.type === 'transition'
                  }"
                >
                  {{ getTypeLabel(spark.type) }}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <CardDescription class="text-sm leading-relaxed">
                {{ spark.role_description }}
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </ScrollArea>

      <SheetFooter class="px-6 py-4 border-t bg-gray-50">
        <Button @click="isOpen = false" variant="default" class="w-full">
          关闭
        </Button>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>

<script setup lang="ts">
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetFooter
} from '@/components/ui/sheet'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  LightbulbIcon,
  StarIcon,
  CheckCircle2Icon,
  FileTextIcon,
  ChevronsRightIcon
} from 'lucide-vue-next'

interface ConceptSpark {
  text: string
  sentence_index: number
  importance_score: number
  explanation_hint: string
  dom_path: string
}

interface ArgumentSpark {
  type: 'claim' | 'evidence' | 'transition'
  text: string
  sentence_index: number
  role_description: string
  dom_path: string
}

const props = defineProps<{
  show: boolean
  sentenceIndex: number | null
  selectedSentence: string
  conceptSparks: ConceptSpark[]
  argumentSparks: ArgumentSpark[]
}>()

const emit = defineEmits<{
  close: []
}>()

const isOpen = computed({
  get: () => props.show,
  set: (value) => {
    if (!value) emit('close')
  }
})

const sparkCount = computed(() => {
  return props.conceptSparks.length + props.argumentSparks.length
})

const getTypeLabel = (type: string) => {
  const labels = {
    claim: '核心观点',
    evidence: '支撑证据',
    transition: '关键转折'
  }
  return labels[type as keyof typeof labels] || type
}
</script>
