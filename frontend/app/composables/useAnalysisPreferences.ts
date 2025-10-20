import { ref } from 'vue'

export interface AnalysisPreferences {
  auto_basic_analysis: boolean
  auto_meta_analysis: boolean
  auto_argument_lens: boolean
  auto_stance_lens: boolean
}

const preferences = ref<AnalysisPreferences>({
  auto_basic_analysis: true,
  auto_meta_analysis: false,
  auto_argument_lens: false,
  auto_stance_lens: false
})

const isLoading = ref(false)
const error = ref<string | null>(null)

export function useAnalysisPreferences() {
  /**
   * 获取用户的分析偏好设置
   */
  async function fetchPreferences(userId: number) {
    isLoading.value = true
    error.value = null

    try {
      const config = useRuntimeConfig()
      const data = await $fetch(`${config.public.apiBase}/api/v1/preferences/analysis/${userId}`)

      preferences.value = data as AnalysisPreferences

      return data as AnalysisPreferences
    } catch (err) {
      error.value = err instanceof Error ? err.message : '未知错误'
      console.error('获取分析偏好设置失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新用户的分析偏好设置
   */
  async function updatePreferences(userId: number, updates: Partial<AnalysisPreferences>) {
    isLoading.value = true
    error.value = null

    try {
      const config = useRuntimeConfig()
      const data = await $fetch(`${config.public.apiBase}/api/v1/preferences/analysis/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: updates
      })

      preferences.value = data as AnalysisPreferences

      return data as AnalysisPreferences
    } catch (err) {
      error.value = err instanceof Error ? err.message : '未知错误'
      console.error('更新分析偏好设置失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 切换特定分析功能的开关
   */
  async function togglePreference(
    userId: number,
    key: keyof AnalysisPreferences
  ) {
    const newValue = !preferences.value[key]
    await updatePreferences(userId, { [key]: newValue })
  }

  return {
    preferences,
    isLoading,
    error,
    fetchPreferences,
    updatePreferences,
    togglePreference
  }
}
