## 目标
实现邮箱管理的前端页面，包括邮箱配置、收件箱、发送邮件等功能。

## 前置任务
依赖 T17 完成（需要邮箱 API）

## 工作目录
G:\Orbit\frontend

## 任务要求

### 1. 创建邮箱 API (api/email.ts)
```typescript
import api from './index'

export interface EmailAccount {
  id: number
  name: string
  email: string
  imap_server: string
  smtp_server: string
  is_active: boolean
  created_at: string
}

export interface EmailMessage {
  id: number
  account_id: number
  subject: string
  sender: string
  recipients: string
  body_text?: string
  is_read: boolean
  is_starred: boolean
  has_attachment: boolean
  received_at?: string
}

export const emailApi = {
  listAccounts() {
    return api.get<any, EmailAccount[]>('/api/email/accounts')
  },
  createAccount(data: any) {
    return api.post<any, EmailAccount>('/api/email/accounts', data)
  },
  deleteAccount(id: number) {
    return api.delete(`/api/email/accounts/${id}`)
  },
  getUnreadCount(accountId: number) {
    return api.get<any, { count: number }>(`/api/email/accounts/${accountId}/unread`)
  },
  listMessages(accountId: number, folder?: string) {
    return api.get<any, EmailMessage[]>(`/api/email/accounts/${accountId}/messages`, { params: { folder } })
  },
  sendMessage(accountId: number, data: { to: string[], subject: string, body: string, html?: boolean }) {
    return api.post(`/api/email/accounts/${accountId}/send`, data)
  },
  markAsRead(messageId: number) {
    return api.put(`/api/email/messages/${messageId}/read`)
  },
  syncEmails(accountId: number) {
    return api.post(`/api/email/accounts/${accountId}/sync`)
  }
}
```

### 2. 创建邮箱页面 (views/Email.vue)
设计要求：
- 左侧显示邮箱账户列表，每个账户显示未读数量
- 右侧显示选中账户的收件箱
- 支持添加邮箱账户的对话框
- 支持发送邮件的对话框
- 邮件列表显示发件人、主题、时间、是否已读
- 点击邮件可查看详情

### 3. 添加路由
在 router/index.ts 中添加邮箱路由：
```typescript
{
  path: '/email',
  name: 'Email',
  component: () => import('../views/Email.vue')
}
```

### 4. 添加侧边栏菜单
在 Sidebar.vue 中添加邮箱菜单项：
```typescript
{
  path: '/email',
  title: '邮箱',
  icon: 'Message'
}
```

## 预置邮箱配置
用户已提供以下邮箱：

### 163邮箱
- IMAP: imap.163.com:993 (SSL)
- SMTP: smtp.163.com:465 (SSL)
- 授权码: JReFz38AGyjbCMXG

### QQ邮箱
- IMAP: imap.qq.com:993 (SSL)
- SMTP: smtp.qq.com:465 (SSL)
- 服务码: ascndheebkvjbaih

### Gmail
- IMAP: imap.gmail.com:993 (SSL)
- SMTP: smtp.gmail.com:465 (SSL) 或 587 (TLS)
- 应用专用密码: zitd joak dsdd wsqa

## 验收标准
- [ ] 邮箱账户列表正常显示
- [ ] 添加邮箱账户功能正常
- [ ] 未读邮件数量显示正常
- [ ] 邮件列表正常显示
- [ ] 发送邮件功能正常
- [ ] 路由和菜单配置正确
