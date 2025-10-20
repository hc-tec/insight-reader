/**
 * 导出功能 Composable
 */
import type { StashItem, ExportFormat } from '~/types/stash'
import type { Intent } from '~/types/insight'

export const useExport = () => {
  // 导出格式配置
  const exportFormats: ExportFormat[] = [
    {
      type: 'md',
      label: 'Markdown (.md)',
      mimeType: 'text/markdown;charset=utf-8',
      extension: 'md'
    },
    {
      type: 'txt',
      label: '纯文本 (.txt)',
      mimeType: 'text/plain;charset=utf-8',
      extension: 'txt'
    }
  ]

  // 获取意图标签
  const getIntentLabel = (intent: Intent): string => {
    const labels: Record<Intent, string> = {
      explain: '解释',
      analyze: '分析',
      counter: '反驳'
    }
    return labels[intent] || intent
  }

  // 格式化时间
  const formatTime = (timestamp: number): string => {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 导出为 Markdown
  const exportAsMarkdown = (items: StashItem[]): string => {
    if (items.length === 0) return ''

    // 获取文章信息（使用第一个洞察的文章信息）
    const firstItem = items[0]
    const articleTitle = firstItem.articleTitle || '我的阅读笔记'
    const articleContent = firstItem.articleContent

    let markdown = `# ${articleTitle}\n\n`
    markdown += `📅 生成时间：${new Date().toLocaleString('zh-CN')}\n`
    markdown += `📝 共 ${items.length} 个洞察\n\n`
    markdown += `---\n\n`

    // 添加原文内容（重要！）
    if (articleContent && articleContent.trim()) {
      markdown += `## 📖 原文内容\n\n`
      markdown += `${articleContent}\n\n`
      markdown += `---\n\n`
    }

    // 添加洞察卡片
    markdown += `## 💡 我的洞察\n\n`

    items.forEach((item, idx) => {
      markdown += `### ${idx + 1}. "${item.selectedText}"\n\n`

      // 元数据
      markdown += `- **意图**：${getIntentLabel(item.intent)}\n`
      markdown += `- **时间**：${formatTime(item.timestamp)}\n`
      if (item.modelUsed) {
        markdown += `- **模型**：${item.modelUsed}\n`
      }
      if (item.customQuestion) {
        markdown += `- **自定义问题**：${item.customQuestion}\n`
      }
      markdown += `\n`

      // 上下文（引用格式）
      if (item.context && item.context.trim()) {
        markdown += `**上下文**：\n\n`
        markdown += `> ${item.context.replace(/\n/g, '\n> ')}\n\n`
      }

      // 推理内容（如果有）
      if (item.reasoning && item.reasoning.trim()) {
        markdown += `#### 🧠 思维链\n\n`
        markdown += `${item.reasoning}\n\n`
      }

      // 洞察内容
      markdown += `#### 💬 洞察内容\n\n`
      markdown += `${item.insight}\n\n`

      // 对话历史（追问记录）
      if (item.conversationHistory && item.conversationHistory.length > 0) {
        markdown += `#### 🔄 对话记录（${item.conversationHistory.length / 2} 轮追问）\n\n`
        item.conversationHistory.forEach((msg) => {
          const prefix = msg.role === 'user' ? '**你**' : '**AI**'
          markdown += `${prefix}：${msg.content}\n\n`
        })
      }

      markdown += `---\n\n`
    })

    // 添加页脚
    markdown += `\n> 🤖 由 InsightReader 生成 | [https://insightreader.ai](https://insightreader.ai)\n`

    return markdown
  }

  // 导出为纯文本
  const exportAsText = (items: StashItem[]): string => {
    if (items.length === 0) return ''

    const firstItem = items[0]
    const articleTitle = firstItem.articleTitle || '我的阅读笔记'
    const articleContent = firstItem.articleContent

    let text = `${articleTitle}\n`
    text += `${'='.repeat(articleTitle.length)}\n\n`
    text += `生成时间：${new Date().toLocaleString('zh-CN')}\n`
    text += `共 ${items.length} 个洞察\n\n`
    text += `${'-'.repeat(60)}\n\n`

    // 原文内容
    if (articleContent && articleContent.trim()) {
      text += `原文内容\n\n`
      text += `${articleContent}\n\n`
      text += `${'-'.repeat(60)}\n\n`
    }

    // 洞察卡片
    text += `我的洞察\n\n`

    items.forEach((item, idx) => {
      text += `${idx + 1}. "${item.selectedText}"\n\n`
      text += `意图：${getIntentLabel(item.intent)}\n`
      text += `时间：${formatTime(item.timestamp)}\n`
      if (item.customQuestion) {
        text += `问题：${item.customQuestion}\n`
      }
      text += `\n`

      // 上下文
      if (item.context && item.context.trim()) {
        text += `上下文：\n${item.context}\n\n`
      }

      // 推理内容
      if (item.reasoning && item.reasoning.trim()) {
        text += `思维链：\n${item.reasoning}\n\n`
      }

      // 洞察内容
      text += `洞察内容：\n${item.insight}\n\n`

      // 对话历史
      if (item.conversationHistory && item.conversationHistory.length > 0) {
        text += `对话记录（${item.conversationHistory.length / 2} 轮追问）：\n`
        item.conversationHistory.forEach((msg) => {
          const prefix = msg.role === 'user' ? '你' : 'AI'
          text += `${prefix}：${msg.content}\n`
        })
        text += `\n`
      }

      text += `${'-'.repeat(60)}\n\n`
    })

    text += `\n由 InsightReader 生成\n`

    return text
  }

  // 触发文件下载
  const downloadFile = (content: string, filename: string, mimeType: string) => {
    if (!process.client) return

    try {
      // 添加 BOM 以确保中文正确显示
      const BOM = '\uFEFF'
      const blob = new Blob([BOM + content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      console.log('📥 文件下载成功:', filename)
    } catch (error) {
      console.error('文件下载失败:', error)
      throw error
    }
  }

  // 导出洞察笔记
  const exportInsights = (
    items: StashItem[],
    format: 'md' | 'txt' = 'md',
    customFilename?: string
  ) => {
    if (items.length === 0) {
      throw new Error('没有可导出的内容')
    }

    // 生成文件名
    const timestamp = new Date().toISOString().split('T')[0]
    const articleTitle = items[0].articleTitle || '我的阅读笔记'
    const safeTitle = articleTitle.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '_').substring(0, 30)
    const defaultFilename = `${safeTitle}_${timestamp}`

    let content: string
    let mimeType: string
    let extension: string

    switch (format) {
      case 'md':
        content = exportAsMarkdown(items)
        mimeType = 'text/markdown;charset=utf-8'
        extension = 'md'
        break
      case 'txt':
        content = exportAsText(items)
        mimeType = 'text/plain;charset=utf-8'
        extension = 'txt'
        break
      default:
        throw new Error('不支持的导出格式')
    }

    const filename = customFilename
      ? `${customFilename}.${extension}`
      : `${defaultFilename}.${extension}`

    downloadFile(content, filename, mimeType)
  }

  // 复制到剪贴板
  const copyToClipboard = async (items: StashItem[], format: 'md' | 'txt' = 'md') => {
    if (!process.client) return

    try {
      const content = format === 'md' ? exportAsMarkdown(items) : exportAsText(items)
      await navigator.clipboard.writeText(content)
      console.log('📋 已复制到剪贴板')
      return true
    } catch (error) {
      console.error('复制失败:', error)
      return false
    }
  }

  return {
    exportFormats,
    exportInsights,
    exportAsMarkdown,
    exportAsText,
    copyToClipboard,
    getIntentLabel,
    formatTime
  }
}
