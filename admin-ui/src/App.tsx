import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  FileTextOutlined,
  HistoryOutlined,
  MessageOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { getToken } from './api/client'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import CSPage from './pages/CSPage'
import ExpressionPage from './pages/ExpressionPage'
import LogsPage from './pages/LogsPage'
import SubscriptionsPage from './pages/SubscriptionsPage'

const { Sider, Content } = Layout

const NAV_ITEMS = [
  { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/cs', icon: <FileTextOutlined />, label: 'CS 커리큘럼' },
  { key: '/expression', icon: <MessageOutlined />, label: '한글 표현' },
  { key: '/logs', icon: <HistoryOutlined />, label: '발송 로그' },
  { key: '/subscriptions', icon: <SettingOutlined />, label: '봇-채팅방' },
]

function AdminLayout() {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '16px 24px', fontWeight: 700, fontSize: 15 }}>세상만사</div>
        <Menu
          mode="inline"
          selectedKeys={[pathname]}
          items={NAV_ITEMS}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Content style={{ padding: 24, background: '#fff' }}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/cs" element={<CSPage />} />
            <Route path="/expression" element={<ExpressionPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/subscriptions" element={<SubscriptionsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  if (!getToken()) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={<RequireAuth><AdminLayout /></RequireAuth>} />
      </Routes>
    </BrowserRouter>
  )
}
