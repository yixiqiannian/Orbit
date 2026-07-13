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
  body_html?: string
  is_read: boolean
  is_starred: boolean
  has_attachment: boolean
  received_at?: string
  created_at: string
}

export interface SendMessageParams {
  to: string[]
  subject: string
  body: string
  html?: boolean
}

export const emailApi = {
  listAccounts() {
    return api.get<any, EmailAccount[]>('/api/email/accounts')
  },
  createAccount(data: {
    name: string
    email: string
    password: string
    imap_server: string
    imap_port: number
    smtp_server: string
    smtp_port: number
    use_ssl?: boolean
  }) {
    return api.post<any, EmailAccount>('/api/email/accounts', data)
  },
  deleteAccount(id: number) {
    return api.delete(`/api/email/accounts/${id}`)
  },
  getUnreadCount(accountId: number) {
    return api.get<any, { account_id: number; folder: string; unread_count: number }>(`/api/email/accounts/${accountId}/unread`)
  },
  listMessages(accountId: number, folder?: string) {
    return api.get<any, { total: number; items: EmailMessage[] }>(`/api/email/accounts/${accountId}/messages`, { params: { folder } })
  },
  getMessage(messageId: number) {
    return api.get<any, EmailMessage>(`/api/email/messages/${messageId}`)
  },
  sendMessage(accountId: number, data: SendMessageParams) {
    return api.post(`/api/email/accounts/${accountId}/send`, data)
  },
  markAsRead(messageId: number) {
    return api.put(`/api/email/messages/${messageId}/read`)
  },
  toggleStar(messageId: number) {
    return api.put(`/api/email/messages/${messageId}/star`)
  },
  syncEmails(accountId: number) {
    return api.post(`/api/email/accounts/${accountId}/sync`)
  }
}
