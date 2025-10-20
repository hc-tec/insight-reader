/**
 * 键盘快捷键 Composable
 */
export const useKeyboard = () => {
  const handlers = ref<Map<string, () => void>>(new Map())

  const handleKeydown = (event: KeyboardEvent) => {
    // Esc 键
    if (event.key === 'Escape') {
      const escHandler = handlers.value.get('escape')
      if (escHandler) {
        escHandler()
        event.preventDefault()
      }
    }

    // Ctrl/Cmd + K - 聚焦到搜索/输入
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
      const searchHandler = handlers.value.get('search')
      if (searchHandler) {
        searchHandler()
        event.preventDefault()
      }
    }

    // Ctrl/Cmd + / - 显示快捷键帮助
    if ((event.ctrlKey || event.metaKey) && event.key === '/') {
      const helpHandler = handlers.value.get('help')
      if (helpHandler) {
        helpHandler()
        event.preventDefault()
      }
    }
  }

  const register = (key: string, handler: () => void) => {
    handlers.value.set(key, handler)
  }

  const unregister = (key: string) => {
    handlers.value.delete(key)
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
  })

  return {
    register,
    unregister
  }
}
