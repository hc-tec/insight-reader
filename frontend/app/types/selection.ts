/**
 * 选中文本相关类型定义
 */

export interface Selection {
  text: string
  start: number
  end: number
}

export interface SelectionPosition {
  x: number
  y: number
}
