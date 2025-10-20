<template>
  <Card v-if="metaInfo">
    <CardHeader class="pb-4 bg-gradient-to-r from-slate-50 to-gray-50">
      <CardTitle class="text-base flex items-center gap-2">
        <FileTextIcon class="w-4 h-4" />
        文章元信息
      </CardTitle>
    </CardHeader>

    <CardContent class="space-y-4">
      <!-- 作者立场 -->
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
          <UserIcon class="w-5 h-5 text-blue-600" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-xs text-muted-foreground mb-1">作者立场</div>
          <Badge variant="secondary">{{ metaInfo.author_stance }}</Badge>
        </div>
      </div>

      <!-- 写作意图 -->
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
          <PenToolIcon class="w-5 h-5 text-emerald-600" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-xs text-muted-foreground mb-1">写作意图</div>
          <Badge variant="secondary">{{ metaInfo.writing_intent }}</Badge>
        </div>
      </div>

      <!-- 情感基调 -->
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center">
          <SmileIcon class="w-5 h-5 text-purple-600" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-xs text-muted-foreground mb-1">情感基调</div>
          <Badge variant="secondary">{{ metaInfo.emotional_tone }}</Badge>
        </div>
      </div>

      <!-- 目标读者 -->
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
          <UsersIcon class="w-5 h-5 text-amber-600" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-xs text-muted-foreground mb-1">目标读者</div>
          <Badge variant="secondary">{{ metaInfo.target_audience }}</Badge>
        </div>
      </div>

      <!-- 时效性 -->
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-rose-50 flex items-center justify-center">
          <ClockIcon class="w-5 h-5 text-rose-600" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-xs text-muted-foreground mb-1">时效性</div>
          <Badge variant="secondary">{{ metaInfo.timeliness }}</Badge>
        </div>
      </div>
    </CardContent>

    <!-- 标签 -->
    <CardFooter v-if="tags && tags.length > 0" class="flex-col items-start gap-3 bg-gray-50 border-t">
      <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
        <TagIcon class="w-3.5 h-3.5" />
        标签
      </div>
      <div class="flex flex-wrap gap-2">
        <Badge
          v-for="tag in tags"
          :key="tag"
          variant="outline"
          class="gap-1"
        >
          {{ tag }}
        </Badge>
      </div>
    </CardFooter>

    <!-- 摘要 -->
    <div v-if="summary" class="px-6 py-4 border-t">
      <div class="flex items-center gap-1.5 text-xs text-muted-foreground mb-2">
        <FileTextIcon class="w-3.5 h-3.5" />
        核心摘要
      </div>
      <CardDescription class="leading-relaxed">{{ summary }}</CardDescription>
    </div>
  </Card>
</template>

<script setup lang="ts">
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  UserIcon,
  PenToolIcon,
  SmileIcon,
  UsersIcon,
  ClockIcon,
  TagIcon,
  FileTextIcon
} from 'lucide-vue-next'

interface MetaInfo {
  author_stance: string
  writing_intent: string
  emotional_tone: string
  target_audience: string
  timeliness: string
}

defineProps<{
  metaInfo: MetaInfo | null
  tags?: string[]
  summary?: string
}>()
</script>
