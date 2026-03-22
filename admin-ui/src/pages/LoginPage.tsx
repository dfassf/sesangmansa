import { useState } from 'react'
import { Button, Card, Form, Input, Typography } from 'antd'
import { setToken } from '../api/client'

const { Title } = Typography

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function onFinish({ token }: { token: string }) {
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/admin/subscriptions', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.status === 401) {
        setError('토큰이 올바르지 않습니다.')
        return
      }
      setToken(token)
      window.location.href = '/'
    } catch {
      setError('서버에 연결할 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f5f5f5' }}>
      <Card style={{ width: 360 }}>
        <Title level={4} style={{ marginBottom: 24 }}>세상만사 백오피스</Title>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item name="token" label="Admin Token" rules={[{ required: true }]}>
            <Input.Password placeholder="ADMIN_TOKEN" />
          </Form.Item>
          {error && <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>}
          <Button type="primary" htmlType="submit" loading={loading} block>
            로그인
          </Button>
        </Form>
      </Card>
    </div>
  )
}
