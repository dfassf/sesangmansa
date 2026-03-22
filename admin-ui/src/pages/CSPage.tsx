import { useEffect, useState } from 'react'
import { Badge, Descriptions, Drawer, Select, Space, Table, Tag, Typography, message } from 'antd'
import { api } from '../api/client'
import type { CSNote, CSTopic } from '../types'

const { Title, Paragraph } = Typography

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner: 'green',
  intermediate: 'blue',
  advanced: 'red',
}

export default function CSPage() {
  const [topics, setTopics] = useState<CSTopic[]>([])
  const [category, setCategory] = useState<string>()
  const [difficulty, setDifficulty] = useState<string>()
  const [selected, setSelected] = useState<CSTopic | null>(null)
  const [note, setNote] = useState<CSNote | null>(null)
  const [noteLoading, setNoteLoading] = useState(false)

  useEffect(() => {
    const params = new URLSearchParams()
    if (category) params.set('category', category)
    if (difficulty) params.set('difficulty', difficulty)
    api.get<CSTopic[]>(`/admin/cs/topics?${params}`).then(setTopics).catch(() => message.error('토픽 불러오기 실패'))
  }, [category, difficulty])

  async function onRowClick(topic: CSTopic) {
    setSelected(topic)
    setNote(null)
    setNoteLoading(true)
    try {
      const n = await api.get<CSNote>(`/admin/cs/topics/${topic.id}/note`)
      setNote(n)
    } catch {
      setNote(null)
    } finally {
      setNoteLoading(false)
    }
  }

  const categories = [...new Set(topics.map(t => t.category))]

  const columns = [
    { title: '카테고리', dataIndex: 'category', key: 'category' },
    { title: '제목', dataIndex: 'title', key: 'title' },
    {
      title: '난이도',
      dataIndex: 'difficulty',
      key: 'difficulty',
      render: (v: string) => <Tag color={DIFFICULTY_COLOR[v]}>{v}</Tag>,
    },
    {
      title: '노트',
      key: 'note',
      render: () => <Badge status="default" text="클릭하여 조회" />,
    },
  ]

  return (
    <div>
      <Title level={4}>CS 커리큘럼</Title>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="카테고리"
          allowClear
          style={{ width: 160 }}
          onChange={setCategory}
          options={categories.map(c => ({ label: c, value: c }))}
        />
        <Select
          placeholder="난이도"
          allowClear
          style={{ width: 140 }}
          onChange={setDifficulty}
          options={[
            { label: 'beginner', value: 'beginner' },
            { label: 'intermediate', value: 'intermediate' },
            { label: 'advanced', value: 'advanced' },
          ]}
        />
      </Space>
      <Table
        dataSource={topics}
        columns={columns}
        rowKey="id"
        size="small"
        onRow={record => ({ onClick: () => onRowClick(record), style: { cursor: 'pointer' } })}
      />
      <Drawer
        title={selected?.title}
        open={!!selected}
        onClose={() => setSelected(null)}
        width={520}
        loading={noteLoading}
      >
        {note ? (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="요약">
              <Paragraph style={{ marginBottom: 0 }}>{note.summary}</Paragraph>
            </Descriptions.Item>
            <Descriptions.Item label="핵심 포인트">
              <ul style={{ paddingLeft: 16, margin: 0 }}>
                {note.key_points.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </Descriptions.Item>
            {note.analogy && (
              <Descriptions.Item label="비유">{note.analogy}</Descriptions.Item>
            )}
            {note.quiz && (
              <Descriptions.Item label="퀴즈">
                <div>{note.quiz.question}</div>
                <ol style={{ paddingLeft: 16, margin: '8px 0 0' }}>
                  {note.quiz.options.map((o, i) => <li key={i}>{o}</li>)}
                </ol>
              </Descriptions.Item>
            )}
            <Descriptions.Item label="생성일">
              {new Date(note.created_at).toLocaleString('ko-KR')}
            </Descriptions.Item>
          </Descriptions>
        ) : (
          <Paragraph type="secondary">노트가 아직 생성되지 않았습니다.</Paragraph>
        )}
      </Drawer>
    </div>
  )
}
