import { useEffect, useState } from 'react'
import { Button, Checkbox, Form, Input, Modal, Space, Switch, Table, Tag, Typography, message } from 'antd'
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import { api } from '../api/client'
import type { Subscription } from '../types'
import { BRIEFING_TYPE_LABELS } from '../types'

const { Title } = Typography

const ALL_TYPES = Object.keys(BRIEFING_TYPE_LABELS)

export default function SubscriptionsPage() {
  const [subs, setSubs] = useState<Subscription[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Subscription | null>(null)
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)

  async function load() {
    const data = await api.get<Subscription[]>('/admin/subscriptions')
    setSubs(data)
  }

  useEffect(() => { load() }, [])

  function openCreate() {
    setEditing(null)
    form.resetFields()
    setModalOpen(true)
  }

  function openEdit(sub: Subscription) {
    setEditing(sub)
    form.setFieldsValue({
      label: sub.label ?? '',
      chat_id: String(sub.chat_id),
      bot_token: sub.bot_token,
      briefing_types: sub.briefing_types,
    })
    setModalOpen(true)
  }

  async function onSubmit(values: { label: string; chat_id: string; bot_token: string; briefing_types: string[] }) {
    setSubmitting(true)
    try {
      if (editing) {
        await api.patch(`/admin/subscriptions/${editing.id}`, {
          label: values.label || null,
          briefing_types: values.briefing_types,
        })
      } else {
        await api.post('/admin/subscriptions', {
          label: values.label || null,
          chat_id: Number(values.chat_id),
          bot_token: values.bot_token,
          briefing_types: values.briefing_types,
          active: true,
        })
      }
      setModalOpen(false)
      await load()
    } catch (e: unknown) {
      message.error(e instanceof Error ? e.message : '오류가 발생했습니다.')
    } finally {
      setSubmitting(false)
    }
  }

  async function toggleActive(sub: Subscription) {
    await api.patch(`/admin/subscriptions/${sub.id}`, { active: !sub.active })
    await load()
  }

  async function deleteSub(id: number) {
    await api.delete(`/admin/subscriptions/${id}`)
    await load()
  }

  const columns = [
    { title: '이름', dataIndex: 'label', key: 'label', render: (v: string | null) => v ?? '-' },
    { title: 'Chat ID', dataIndex: 'chat_id', key: 'chat_id' },
    {
      title: 'Bot Token',
      dataIndex: 'bot_token',
      key: 'bot_token',
      render: (v: string) => `...${v.slice(-8)}`,
    },
    {
      title: '발송 유형',
      dataIndex: 'briefing_types',
      key: 'briefing_types',
      render: (types: string[]) => types.map(t => <Tag key={t}>{BRIEFING_TYPE_LABELS[t] ?? t}</Tag>),
    },
    {
      title: '활성',
      key: 'active',
      render: (_: unknown, r: Subscription) => (
        <Switch checked={r.active} onChange={() => toggleActive(r)} size="small" />
      ),
    },
    {
      title: '',
      key: 'actions',
      render: (_: unknown, r: Subscription) => (
        <Space>
          <Button icon={<EditOutlined />} size="small" onClick={() => openEdit(r)} />
          <Button
            icon={<DeleteOutlined />}
            size="small"
            danger
            onClick={() => Modal.confirm({
              title: '삭제하시겠습니까?',
              onOk: () => deleteSub(r.id),
            })}
          />
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>봇-채팅방 구독</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>추가</Button>
      </Space>
      <Table dataSource={subs} columns={columns} rowKey="id" size="small" />

      <Modal
        title={editing ? '구독 수정' : '구독 추가'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={submitting}
      >
        <Form form={form} layout="vertical" onFinish={onSubmit} style={{ marginTop: 16 }}>
          <Form.Item name="label" label="이름 (선택)">
            <Input placeholder="예: 메인 채팅방" />
          </Form.Item>
          {!editing && (
            <>
              <Form.Item name="chat_id" label="Chat ID" rules={[{ required: true }]}>
                <Input placeholder="-1001234567890" />
              </Form.Item>
              <Form.Item name="bot_token" label="Bot Token" rules={[{ required: true }]}>
                <Input.Password placeholder="1234567890:ABC..." />
              </Form.Item>
            </>
          )}
          <Form.Item name="briefing_types" label="발송 유형" rules={[{ required: true }]}>
            <Checkbox.Group>
              <Space direction="vertical">
                {ALL_TYPES.map(t => (
                  <Checkbox key={t} value={t}>{BRIEFING_TYPE_LABELS[t]}</Checkbox>
                ))}
              </Space>
            </Checkbox.Group>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
