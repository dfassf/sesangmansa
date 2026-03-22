import { useEffect, useState } from 'react'
import { Button, message, Modal, Table, Tabs, Typography } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import { api } from '../api/client'
import type { LogItem } from '../types'

const { Title } = Typography

function LogTable({ endpoint }: { endpoint: string }) {
  const [items, setItems] = useState<LogItem[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [resending, setResending] = useState<number | null>(null)
  const PAGE_SIZE = 50

  useEffect(() => {
    api
      .get<{ items: LogItem[]; page: number }>(`${endpoint}?page=${page}&page_size=${PAGE_SIZE}`)
      .then(r => {
        setItems(r.items)
        setTotal(r.items.length < PAGE_SIZE ? (page - 1) * PAGE_SIZE + r.items.length : page * PAGE_SIZE + 1)
      })
  }, [endpoint, page])

  function handleResend(id: number) {
    Modal.confirm({
      title: '재발송하시겠습니까?',
      content: '현재 활성 구독자에게 다시 전송됩니다.',
      okText: '재발송',
      cancelText: '취소',
      onOk: async () => {
        setResending(id)
        try {
          const r = await api.post<{ recipients: number }>(`${endpoint}/${id}/resend`, {})
          message.success(`재발송 완료 (${r.recipients}명)`)
        } catch (e: unknown) {
          message.error(e instanceof Error ? e.message : '재발송 실패')
        } finally {
          setResending(null)
        }
      },
    })
  }

  const columns = [
    {
      title: '발송 시간',
      dataIndex: 'sent_at',
      key: 'sent_at',
      render: (v: string) => new Date(v).toLocaleString('ko-KR'),
    },
    {
      title: '항목',
      key: 'item',
      render: (_: unknown, r: LogItem) =>
        r.cs_notes?.cs_topics?.title ??
        r.expr_notes?.expr_clusters?.base_word ??
        `note_id: ${r.note_id}`,
    },
    {
      title: '카테고리',
      key: 'category',
      render: (_: unknown, r: LogItem) =>
        r.cs_notes?.cs_topics?.category ??
        r.expr_notes?.expr_clusters?.category ??
        '-',
    },
    {
      title: '',
      key: 'resend',
      render: (_: unknown, r: LogItem) => (
        <Button
          icon={<SendOutlined />}
          size="small"
          loading={resending === r.id}
          onClick={() => handleResend(r.id)}
        >
          재발송
        </Button>
      ),
    },
  ]

  return (
    <Table
      dataSource={items}
      columns={columns}
      rowKey="id"
      size="small"
      pagination={{
        current: page,
        pageSize: PAGE_SIZE,
        total,
        onChange: setPage,
        showSizeChanger: false,
      }}
    />
  )
}

export default function LogsPage() {
  return (
    <div>
      <Title level={4}>발송 로그</Title>
      <Tabs
        items={[
          { key: 'cs', label: 'CS 노트', children: <LogTable endpoint="/admin/cs/logs" /> },
          { key: 'expr', label: '한글 표현', children: <LogTable endpoint="/admin/expr/logs" /> },
        ]}
      />
    </div>
  )
}
