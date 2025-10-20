/**
 * 阅读设置 Composable
 *
 * 管理字体、字号等阅读偏好设置
 */

export interface ReadingSettings {
  fontFamily: string
  fontSize: string
  lineHeight: string
}

const FONT_FAMILIES = {
  serif: 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif',
  sansSerif: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  songti: '"Songti SC", "SimSun", "宋体", serif',
  heiti: '"Heiti SC", "SimHei", "黑体", sans-serif',
  kaiti: '"Kaiti SC", "KaiTi", "楷体", serif',
  cangErJinKai: '"仓耳今楷01 W03", "仓耳今楷", "Cang Er Jin Kai", "KaiTi", "楷体", serif',
}

const FONT_SIZES = {
  small: '16px',
  medium: '22px',
  large: '28px',
  xlarge: '36px',
}

const LINE_HEIGHTS = {
  small: '1.8',
  medium: '2.0',
  large: '2.1',
  xlarge: '2.0',
}

const STORAGE_KEY = 'reading-settings'

export const useReadingSettings = () => {
  // 默认设置
  const defaultSettings: ReadingSettings = {
    fontFamily: FONT_FAMILIES.cangErJinKai,
    fontSize: FONT_SIZES.medium,
    lineHeight: LINE_HEIGHTS.medium,
  }

  // 从 localStorage 加载设置
  const loadSettings = (): ReadingSettings => {
    if (process.client) {
      try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) {
          return { ...defaultSettings, ...JSON.parse(saved) }
        }
      } catch (e) {
        console.error('加载阅读设置失败:', e)
      }
    }
    return defaultSettings
  }

  // 保存设置到 localStorage
  const saveSettings = (settings: ReadingSettings) => {
    if (process.client) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
      } catch (e) {
        console.error('保存阅读设置失败:', e)
      }
    }
  }

  // 响应式设置
  const settings = useState<ReadingSettings>('reading-settings', () => loadSettings())

  // 设置字体
  const setFontFamily = (fontKey: keyof typeof FONT_FAMILIES) => {
    settings.value.fontFamily = FONT_FAMILIES[fontKey]
    saveSettings(settings.value)
  }

  // 设置字号
  const setFontSize = (sizeKey: keyof typeof FONT_SIZES) => {
    settings.value.fontSize = FONT_SIZES[sizeKey]
    settings.value.lineHeight = LINE_HEIGHTS[sizeKey]
    saveSettings(settings.value)
  }

  // 重置为默认
  const resetSettings = () => {
    settings.value = { ...defaultSettings }
    saveSettings(settings.value)
  }

  // 获取字体列表
  const getFontOptions = () => [
    { key: 'cangErJinKai', label: '仓耳今楷', family: FONT_FAMILIES.cangErJinKai },
    { key: 'songti', label: '宋体', family: FONT_FAMILIES.songti },
    { key: 'heiti', label: '黑体', family: FONT_FAMILIES.heiti },
    { key: 'kaiti', label: '楷体', family: FONT_FAMILIES.kaiti },
    { key: 'serif', label: '衬线体', family: FONT_FAMILIES.serif },
    { key: 'sansSerif', label: '无衬线', family: FONT_FAMILIES.sansSerif },
  ]

  // 获取字号列表
  const getFontSizeOptions = () => [
    { key: 'small', label: '小', size: FONT_SIZES.small },
    { key: 'medium', label: '中', size: FONT_SIZES.medium },
    { key: 'large', label: '大', size: FONT_SIZES.large },
    { key: 'xlarge', label: '特大', size: FONT_SIZES.xlarge },
  ]

  // 获取当前选中的字体 key
  const getCurrentFontKey = () => {
    const entry = Object.entries(FONT_FAMILIES).find(
      ([_, value]) => value === settings.value.fontFamily
    )
    return entry ? entry[0] : 'cangErJinKai'
  }

  // 获取当前选中的字号 key
  const getCurrentSizeKey = () => {
    const entry = Object.entries(FONT_SIZES).find(
      ([_, value]) => value === settings.value.fontSize
    )
    return entry ? entry[0] : 'medium'
  }

  return {
    settings: readonly(settings),
    setFontFamily,
    setFontSize,
    resetSettings,
    getFontOptions,
    getFontSizeOptions,
    getCurrentFontKey,
    getCurrentSizeKey,
  }
}
