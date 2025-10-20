/**
 * 文本选中逻辑 Composable
 */
import type { Intent } from '~/types/insight'
import type { SelectionPosition } from '~/types/selection'
import { extractContext } from '~/utils/textParser'

export const useSelection = () => {
  const selectedText = useState<string>('selected-text', () => '')
  const context = useState<string>('selection-context', () => '')
  const position = useState<SelectionPosition>('selection-position', () => ({ x: 0, y: 0 }))
  const showIntentButtons = useState<boolean>('show-intent-buttons', () => false)

  // 新增：保存选中文本在文章中的位置
  const selectedStart = useState<number | null>('selected-start', () => null)
  const selectedEnd = useState<number | null>('selected-end', () => null)

  // 意图识别（简单规则）
  const suggestedIntent = computed<Intent>(() => {
    const len = selectedText.value.length
    if (len < 5) return 'explain'  // 短文本倾向于解释
    if (len > 50) return 'analyze'  // 长文本倾向于分析
    if (/因为|所以|由于|导致/.test(selectedText.value)) return 'analyze'
    return 'explain'
  })

  /**
   * 计算选中文本在文章纯文本中的位置
   */
  const calculateTextPosition = (selectedText: string): { start: number; end: number } | null => {
    const { content } = useArticle()
    const articleText = content.value

    if (!articleText || !selectedText) return null

    // 在文章中查找选中文本
    const index = articleText.indexOf(selectedText)

    if (index === -1) {
      console.warn('⚠️ 无法在文章中找到选中的文本')
      return null
    }

    return {
      start: index,
      end: index + selectedText.length
    }
  }

  const handleSelection = () => {
    const selection = window.getSelection()
    const text = selection?.toString().trim()

    if (text && text.length > 0) {
      selectedText.value = text

      // 提取上下文
      const { content } = useArticle()
      context.value = extractContext(content.value, text)

      // 计算文本位置
      const positions = calculateTextPosition(text)
      if (positions) {
        selectedStart.value = positions.start
        selectedEnd.value = positions.end
        console.log('📍 选中位置:', positions.start, '-', positions.end)
      }

      // 获取选中位置
      const range = selection?.getRangeAt(0)
      const rect = range?.getBoundingClientRect()

      if (rect) {
        position.value = {
          x: rect.left + rect.width / 2,
          y: rect.bottom + 10
        }
      }

      // 不再自动打开弹窗，由trigger按钮控制
      // showIntentButtons.value = true
    }
  }

  const clear = () => {
    selectedText.value = ''
    context.value = ''
    selectedStart.value = null
    selectedEnd.value = null
    showIntentButtons.value = false
    window.getSelection()?.removeAllRanges()
  }

  return {
    selectedText,
    context,
    position,
    showIntentButtons,
    suggestedIntent,
    selectedStart,  // 新增
    selectedEnd,    // 新增
    handleSelection,
    clear
  }
}
