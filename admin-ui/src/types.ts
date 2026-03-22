export interface CSTopic {
  id: number
  category: string
  subcategory: string
  title: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  sort_order: number
  created_at: string
}

export interface CSNote {
  id: number
  topic_id: number
  summary: string
  key_points: string[]
  analogy: string | null
  quiz: { question: string; options: string[] } | null
  reading_time_min: number
  created_at: string
}

export interface ExprCluster {
  id: number
  category: string
  base_word: string
  expressions: string[]
  difficulty: 'beginner' | 'intermediate' | 'advanced' | null
  sort_order: number
  created_at: string
}

export interface ExprNote {
  id: number
  cluster_id: number
  intro: string
  expressions: { word: string; meaning: string; example: string; nuance: string }[]
  comparison: string
  usage_tip: string | null
  created_at: string
}

export interface LogItem {
  id: number
  note_id: number
  sent_at: string
  cs_notes?: { topic_id: number; cs_topics?: { title: string; category: string } }
  expr_notes?: { cluster_id: number; expr_clusters?: { base_word: string; category: string } }
}

export interface Subscription {
  id: number
  label: string | null
  chat_id: number
  bot_token: string
  briefing_types: string[]
  active: boolean
  created_at: string
}

export const BRIEFING_TYPE_LABELS: Record<string, string> = {
  news: '뉴스',
  stock_morning: '주식(아침)',
  stock_evening: '주식(저녁)',
  cs_note: 'CS 노트',
  expression: '한글 표현',
}
