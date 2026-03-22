import { useEffect, useState } from 'react'
import { Card, Col, message, Row, Statistic, Table, Typography } from 'antd'
import { api } from '../api/client'
import type { LogItem } from '../types'
import { BRIEFING_TYPE_LABELS } from '../types'

const { Title } = Typography

export default function DashboardPage() {
  const [csLogs, setCsLogs] = useState<LogItem[]>([])
  const [exprLogs, setExprLogs] = useState<LogItem[]>([])
  const [subCount, setSubCount] = useState(0)

  useEffect(() => {
    api.get<{ items: LogItem[] }>('/admin/cs/logs?page=1&page_size=5').then(r => setCsLogs(r.items)).catch(() => message.error('CS 로그 불러오기 실패'))
    api.get<{ items: LogItem[] }>('/admin/expr/logs?page=1&page_size=5').then(r => setExprLogs(r.items)).catch(() => message.error('표현 로그 불러오기 실패'))
    api.get<unknown[]>('/admin/subscriptions').then(r => setSubCount(r.length)).catch(() => {})
  }, [])

  const todayStr = new Date().toISOString().slice(0, 10)
  const todayCs = csLogs.filter(l => l.sent_at.startsWith(todayStr)).length
  const todayExpr = exprLogs.filter(l => l.sent_at.startsWith(todayStr)).length

  const columns = [
    { title: '시간', dataIndex: 'sent_at', key: 'sent_at', render: (v: string) => new Date(v).toLocaleString('ko-KR') },
    { title: '유형', key: 'type', render: (_: unknown, r: LogItem) => r.cs_notes ? BRIEFING_TYPE_LABELS.cs_note : BRIEFING_TYPE_LABELS.expression },
    {
      title: '항목',
      key: 'item',
      render: (_: unknown, r: LogItem) =>
        r.cs_notes?.cs_topics?.title ?? r.expr_notes?.expr_clusters?.base_word ?? '-',
    },
  ]

  const recentLogs = [...csLogs, ...exprLogs]
    .sort((a, b) => b.sent_at.localeCompare(a.sent_at))
    .slice(0, 5)

  return (
    <div>
      <Title level={4}>Dashboard</Title>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic title="오늘 CS 발송" value={todayCs} suffix="건" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="오늘 표현 발송" value={todayExpr} suffix="건" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="활성 구독" value={subCount} suffix="개" />
          </Card>
        </Col>
      </Row>
      <Card title="최근 발송">
        <Table
          dataSource={recentLogs}
          columns={columns}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  )
}
