/**
 * 文章相关类型定义
 */

export interface Sentence {
  id: number
  text: string
  start: number
  end: number
}

export interface Article {
  content: string
  title: string
  sentences: Sentence[]
}
