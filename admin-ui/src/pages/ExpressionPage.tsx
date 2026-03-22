import { useEffect, useState } from 'react'
import { Descriptions, Drawer, Select, Space, Table, Tag, Typography } from 'antd'
import { api } from '../api/client'
import type { ExprCluster, ExprNote } from '../types'

const { Title, Paragraph } = Typography

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner: 'green',
  intermediate: 'blue',
  advanced: 'red',
}

export default function ExpressionPage() {
  const [clusters, setClusters] = useState<ExprCluster[]>([])
  const [category, setCategory] = useState<string>()
  const [selected, setSelected] = useState<ExprCluster | null>(null)
  const [note, setNote] = useState<ExprNote | null>(null)
  const [noteLoading, setNoteLoading] = useState(false)

  useEffect(() => {
    const params = new URLSearchParams()
    if (category) params.set('category', category)
    api.get<ExprCluster[]>(`/admin/expr/clusters?${params}`).then(setClusters)
  }, [category])

  async function onRowClick(cluster: ExprCluster) {
    setSelected(cluster)
    setNote(null)
    setNoteLoading(true)
    try {
      const n = await api.get<ExprNote>(`/admin/expr/clusters/${cluster.id}/note`)
      setNote(n)
    } catch {
      setNote(null)
    } finally {
      setNoteLoading(false)
    }
  }

  const categories = [...new Set(clusters.map(c => c.category))]

  const columns = [
    { title: '카테고리', dataIndex: 'category', key: 'category' },
    { title: '기준 표현', dataIndex: 'base_word', key: 'base_word' },
    {
      title: '표현 목록',
      dataIndex: 'expressions',
      key: 'expressions',
      render: (v: string[]) => v.map(e => <Tag key={e}>{e}</Tag>),
    },
    {
      title: '난이도',
      dataIndex: 'difficulty',
      key: 'difficulty',
      render: (v: string | null) => v ? <Tag color={DIFFICULTY_COLOR[v]}>{v}</Tag> : '-',
    },
  ]

  return (
    <div>
      <Title level={4}>한글 표현</Title>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="카테고리"
          allowClear
          style={{ width: 180 }}
          onChange={setCategory}
          options={categories.map(c => ({ label: c, value: c }))}
        />
      </Space>
      <Table
        dataSource={clusters}
        columns={columns}
        rowKey="id"
        size="small"
        onRow={record => ({ onClick: () => onRowClick(record), style: { cursor: 'pointer' } })}
      />
      <Drawer
        title={selected?.base_word}
        open={!!selected}
        onClose={() => setSelected(null)}
        width={540}
        loading={noteLoading}
      >
        {note ? (
          <div>
            <Paragraph>{note.intro}</Paragraph>
            {note.expressions.map((e, i) => (
              <Descriptions key={i} column={1} bordered size="small" style={{ marginBottom: 12 }} title={e.word}>
                <Descriptions.Item label="의미">{e.meaning}</Descriptions.Item>
                <Descriptions.Item label="예문">{e.example}</Descriptions.Item>
                <Descriptions.Item label="뉘앙스">{e.nuance}</Descriptions.Item>
              </Descriptions>
            ))}
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="비교">{note.comparison}</Descriptions.Item>
              {note.usage_tip && (
                <Descriptions.Item label="사용 팁">{note.usage_tip}</Descriptions.Item>
              )}
            </Descriptions>
          </div>
        ) : (
          <Paragraph type="secondary">노트가 아직 생성되지 않았습니다.</Paragraph>
        )}
      </Drawer>
    </div>
  )
}
