<template>
  <div class="email-page">
    <!-- 左侧：邮箱账户列表 -->
    <div class="email-sidebar">
      <div class="sidebar-header">
        <h3>邮箱账户</h3>
        <el-button type="primary" size="small" @click="showAddAccount = true">
          <el-icon><Plus /></el-icon>
          添加
        </el-button>
      </div>

      <div v-loading="loadingAccounts" class="account-list">
        <div
          v-for="account in accounts"
          :key="account.id"
          :class="['account-item', { active: selectedAccount?.id === account.id }]"
          @click="selectAccount(account)"
        >
          <div class="account-info">
            <el-icon class="account-icon"><Message /></el-icon>
            <div class="account-detail">
              <div class="account-name">{{ account.name }}</div>
              <div class="account-email">{{ account.email }}</div>
            </div>
          </div>
          <el-badge
            v-if="unreadCounts[account.id]"
            :value="unreadCounts[account.id]"
            :max="99"
            class="unread-badge"
          />
          <el-dropdown @command="(cmd: string) => handleAccountAction(cmd, account)" trigger="click">
            <el-icon class="more-btn"><MoreFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="sync">
                  <el-icon><Refresh /></el-icon>同步邮件
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <el-icon><Delete /></el-icon>删除账户
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <el-empty v-if="!loadingAccounts && accounts.length === 0" description="暂无邮箱账户" :image-size="60" />
      </div>
    </div>

    <!-- 右侧：邮件列表和详情 -->
    <div class="email-main">
      <template v-if="selectedAccount">
        <!-- 工具栏 -->
        <div class="email-toolbar">
          <div class="toolbar-left">
            <h3>{{ selectedAccount.name }}</h3>
            <el-tag size="small" type="info">{{ selectedAccount.email }}</el-tag>
          </div>
          <div class="toolbar-right">
            <el-button :icon="Refresh" @click="syncEmails" :loading="syncing">同步</el-button>
            <el-button type="primary" :icon="Edit" @click="showCompose = true">写邮件</el-button>
          </div>
        </div>

        <!-- 邮件列表 -->
        <div v-loading="loadingMessages" class="message-list">
          <div
            v-for="msg in messages"
            :key="msg.id"
            :class="['message-item', { unread: !msg.is_read, selected: selectedMessage?.id === msg.id }]"
            @click="selectMessage(msg)"
          >
            <div class="msg-left">
              <el-icon
                :class="['star-icon', { starred: msg.is_starred }]"
                @click.stop="toggleStar(msg)"
              >
                <StarFilled v-if="msg.is_starred" />
                <Star v-else />
              </el-icon>
              <div class="msg-info">
                <div class="msg-sender">{{ msg.sender }}</div>
                <div class="msg-subject">{{ msg.subject || '(无主题)' }}</div>
              </div>
            </div>
            <div class="msg-right">
              <span v-if="msg.has_attachment" class="attachment-icon">
                <el-icon><Paperclip /></el-icon>
              </span>
              <span class="msg-time">{{ formatTime(msg.received_at || msg.created_at) }}</span>
            </div>
          </div>

          <el-empty v-if="!loadingMessages && messages.length === 0" description="暂无邮件" />
        </div>

        <!-- 邮件详情 -->
        <el-drawer
          v-model="showDetail"
          :title="selectedMessage?.subject || '(无主题)'"
          size="50%"
          direction="rtl"
        >
          <template v-if="selectedMessage">
            <div class="detail-header">
              <div class="detail-from">
                <strong>发件人：</strong>{{ selectedMessage.sender }}
              </div>
              <div class="detail-to">
                <strong>收件人：</strong>{{ selectedMessage.recipients }}
              </div>
              <div class="detail-time">
                <strong>时间：</strong>{{ formatTime(selectedMessage.received_at || selectedMessage.created_at) }}
              </div>
            </div>
            <el-divider />
            <div class="detail-body" v-html="selectedMessage.body_html || selectedMessage.body_text || '(无内容)'"></div>
          </template>
        </el-drawer>
      </template>

      <!-- 未选择账户时的空状态 -->
      <el-empty v-else description="请选择一个邮箱账户" class="empty-state" />
    </div>

    <!-- 添加邮箱账户对话框 -->
    <el-dialog v-model="showAddAccount" title="添加邮箱账户" width="500px">
      <el-form :model="accountForm" :rules="accountRules" ref="accountFormRef" label-width="100px">
        <el-form-item label="账户名称" prop="name">
          <el-input v-model="accountForm.name" placeholder="如：工作邮箱" />
        </el-form-item>
        <el-form-item label="邮箱地址" prop="email">
          <el-input v-model="accountForm.email" placeholder="example@email.com" />
        </el-form-item>
        <el-form-item label="密码/授权码" prop="password">
          <el-input v-model="accountForm.password" type="password" show-password placeholder="邮箱密码或授权码" />
        </el-form-item>
        <el-form-item label="IMAP服务器" prop="imap_server">
          <el-input v-model="accountForm.imap_server" placeholder="imap.example.com" />
        </el-form-item>
        <el-form-item label="IMAP端口" prop="imap_port">
          <el-input-number v-model="accountForm.imap_port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="SMTP服务器" prop="smtp_server">
          <el-input v-model="accountForm.smtp_server" placeholder="smtp.example.com" />
        </el-form-item>
        <el-form-item label="SMTP端口" prop="smtp_port">
          <el-input-number v-model="accountForm.smtp_port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="使用SSL">
          <el-switch v-model="accountForm.use_ssl" />
        </el-form-item>
      </el-form>

      <!-- 快速配置 -->
      <el-divider>快速配置</el-divider>
      <div class="quick-config">
        <el-button @click="fillPreset('163')">163邮箱</el-button>
        <el-button @click="fillPreset('qq')">QQ邮箱</el-button>
        <el-button @click="fillPreset('gmail')">Gmail</el-button>
      </div>

      <template #footer>
        <el-button @click="showAddAccount = false">取消</el-button>
        <el-button type="primary" @click="handleAddAccount" :loading="addingAccount">确定</el-button>
      </template>
    </el-dialog>

    <!-- 写邮件对话框 -->
    <el-dialog v-model="showCompose" title="写邮件" width="600px">
      <el-form :model="composeForm" :rules="composeRules" ref="composeFormRef" label-width="80px">
        <el-form-item label="收件人" prop="to">
          <el-select
            v-model="composeForm.to"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入邮箱地址后回车"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="主题" prop="subject">
          <el-input v-model="composeForm.subject" placeholder="邮件主题" />
        </el-form-item>
        <el-form-item label="内容" prop="body">
          <el-input
            v-model="composeForm.body"
            type="textarea"
            :rows="10"
            placeholder="邮件内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCompose = false">取消</el-button>
        <el-button type="primary" @click="handleSend" :loading="sending">发送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { emailApi, type EmailAccount, type EmailMessage } from '../api/email'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus, Message, MoreFilled, Refresh, Delete, Edit,
  Star, StarFilled, Paperclip
} from '@element-plus/icons-vue'

// 状态
const accounts = ref<EmailAccount[]>([])
const messages = ref<EmailMessage[]>([])
const selectedAccount = ref<EmailAccount | null>(null)
const selectedMessage = ref<EmailMessage | null>(null)
const unreadCounts = ref<Record<number, number>>({})
const loadingAccounts = ref(false)
const loadingMessages = ref(false)
const syncing = ref(false)
const addingAccount = ref(false)
const sending = ref(false)
const showAddAccount = ref(false)
const showCompose = ref(false)
const showDetail = ref(false)

// 表单引用
const accountFormRef = ref<FormInstance>()
const composeFormRef = ref<FormInstance>()

// 添加账户表单
const accountForm = reactive({
  name: '',
  email: '',
  password: '',
  imap_server: '',
  imap_port: 993,
  smtp_server: '',
  smtp_port: 465,
  use_ssl: true
})

const accountRules: FormRules = {
  name: [{ required: true, message: '请输入账户名称', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码或授权码', trigger: 'blur' }],
  imap_server: [{ required: true, message: '请输入IMAP服务器', trigger: 'blur' }],
  imap_port: [{ required: true, message: '请输入IMAP端口', trigger: 'blur' }],
  smtp_server: [{ required: true, message: '请输入SMTP服务器', trigger: 'blur' }],
  smtp_port: [{ required: true, message: '请输入SMTP端口', trigger: 'blur' }]
}

// 写邮件表单
const composeForm = reactive({
  to: [] as string[],
  subject: '',
  body: ''
})

const composeRules: FormRules = {
  to: [{ required: true, message: '请输入收件人', trigger: 'change', type: 'array' }],
  subject: [{ required: true, message: '请输入主题', trigger: 'blur' }],
  body: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

// 预设配置
const presets: Record<string, Partial<typeof accountForm>> = {
  '163': {
    name: '163邮箱',
    imap_server: 'imap.163.com',
    imap_port: 993,
    smtp_server: 'smtp.163.com',
    smtp_port: 465,
    use_ssl: true
  },
  'qq': {
    name: 'QQ邮箱',
    imap_server: 'imap.qq.com',
    imap_port: 993,
    smtp_server: 'smtp.qq.com',
    smtp_port: 465,
    use_ssl: true
  },
  'gmail': {
    name: 'Gmail',
    imap_server: 'imap.gmail.com',
    imap_port: 993,
    smtp_server: 'smtp.gmail.com',
    smtp_port: 465,
    use_ssl: true
  }
}

function fillPreset(type: string) {
  const preset = presets[type]
  if (preset) {
    Object.assign(accountForm, preset)
  }
}

// 加载账户列表
async function loadAccounts() {
  loadingAccounts.value = true
  try {
    accounts.value = await emailApi.listAccounts()
    // 加载每个账户的未读数
    for (const account of accounts.value) {
      try {
        const res = await emailApi.getUnreadCount(account.id)
        unreadCounts.value[account.id] = res.count
      } catch {
        // 忽略单个账户的错误
      }
    }
  } catch {
    ElMessage.error('加载邮箱账户失败')
  } finally {
    loadingAccounts.value = false
  }
}

// 选择账户
async function selectAccount(account: EmailAccount) {
  selectedAccount.value = account
  selectedMessage.value = null
  showDetail.value = false
  await loadMessages()
}

// 加载邮件列表
async function loadMessages() {
  if (!selectedAccount.value) return
  loadingMessages.value = true
  try {
    messages.value = await emailApi.listMessages(selectedAccount.value.id)
  } catch {
    ElMessage.error('加载邮件失败')
  } finally {
    loadingMessages.value = false
  }
}

// 选择邮件
async function selectMessage(msg: EmailMessage) {
  selectedMessage.value = msg
  showDetail.value = true
  // 标记为已读
  if (!msg.is_read) {
    try {
      await emailApi.markAsRead(msg.id)
      msg.is_read = true
      // 更新未读数
      if (selectedAccount.value) {
        unreadCounts.value[selectedAccount.value.id] = Math.max(0, (unreadCounts.value[selectedAccount.value.id] || 0) - 1)
      }
    } catch {
      // 忽略标记错误
    }
  }
}

// 切换星标
async function toggleStar(msg: EmailMessage) {
  try {
    await emailApi.toggleStar(msg.id)
    msg.is_starred = !msg.is_starred
  } catch {
    ElMessage.error('操作失败')
  }
}

// 同步邮件
async function syncEmails() {
  if (!selectedAccount.value) return
  syncing.value = true
  try {
    await emailApi.syncEmails(selectedAccount.value.id)
    ElMessage.success('同步成功')
    await loadMessages()
    // 更新未读数
    const res = await emailApi.getUnreadCount(selectedAccount.value.id)
    unreadCounts.value[selectedAccount.value.id] = res.count
  } catch {
    ElMessage.error('同步失败')
  } finally {
    syncing.value = false
  }
}

// 添加账户
async function handleAddAccount() {
  const valid = await accountFormRef.value?.validate().catch(() => false)
  if (!valid) return

  addingAccount.value = true
  try {
    await emailApi.createAccount(accountForm)
    ElMessage.success('添加成功')
    showAddAccount.value = false
    // 重置表单
    Object.assign(accountForm, {
      name: '', email: '', password: '',
      imap_server: '', imap_port: 993,
      smtp_server: '', smtp_port: 465,
      use_ssl: true
    })
    await loadAccounts()
  } catch {
    ElMessage.error('添加失败')
  } finally {
    addingAccount.value = false
  }
}

// 删除账户
async function handleDeleteAccount(account: EmailAccount) {
  try {
    await ElMessageBox.confirm(`确定删除账户 "${account.name}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await emailApi.deleteAccount(account.id)
    ElMessage.success('删除成功')
    if (selectedAccount.value?.id === account.id) {
      selectedAccount.value = null
      messages.value = []
    }
    await loadAccounts()
  } catch {
    // 用户取消或删除失败
  }
}

// 账户操作
function handleAccountAction(cmd: string, account: EmailAccount) {
  if (cmd === 'sync') {
    syncEmails()
  } else if (cmd === 'delete') {
    handleDeleteAccount(account)
  }
}

// 发送邮件
async function handleSend() {
  const valid = await composeFormRef.value?.validate().catch(() => false)
  if (!valid || !selectedAccount.value) return

  sending.value = true
  try {
    await emailApi.sendMessage(selectedAccount.value.id, {
      to: composeForm.to,
      subject: composeForm.subject,
      body: composeForm.body
    })
    ElMessage.success('发送成功')
    showCompose.value = false
    // 重置表单
    composeForm.to = []
    composeForm.subject = ''
    composeForm.body = ''
  } catch {
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

// 格式化时间
function formatTime(timeStr: string) {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 今天内显示时间
  if (diff < 86400000 && date.getDate() === now.getDate()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  // 今年内显示月日
  if (date.getFullYear() === now.getFullYear()) {
    return `${date.getMonth() + 1}月${date.getDate()}日`
  }
  // 其他显示完整日期
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => loadAccounts())
</script>

<style scoped>
.email-page {
  display: flex;
  height: calc(100vh - 60px);
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.email-sidebar {
  width: 280px;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
}

.account-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.account-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.account-item:hover {
  background: #f5f7fa;
}

.account-item.active {
  background: #ecf5ff;
}

.account-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.account-icon {
  font-size: 24px;
  color: #409eff;
}

.account-detail {
  flex: 1;
  min-width: 0;
}

.account-name {
  font-weight: 500;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-email {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-btn {
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
}

.account-item:hover .more-btn {
  opacity: 1;
}

.email-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.email-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-left h3 {
  margin: 0;
  font-size: 16px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
}

.message-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.message-item:hover {
  background: #f5f7fa;
}

.message-item.unread {
  background: #fafafa;
}

.message-item.unread .msg-sender,
.message-item.unread .msg-subject {
  font-weight: 600;
}

.message-item.selected {
  background: #ecf5ff;
}

.msg-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.star-icon {
  font-size: 18px;
  color: #c0c4cc;
  cursor: pointer;
  transition: color 0.2s;
}

.star-icon:hover {
  color: #e6a23c;
}

.star-icon.starred {
  color: #e6a23c;
}

.msg-info {
  flex: 1;
  min-width: 0;
}

.msg-sender {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.msg-subject {
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.msg-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.attachment-icon {
  color: #909399;
}

.msg-time {
  font-size: 12px;
  color: #909399;
}

.detail-header {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.detail-header > div {
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-header > div:last-child {
  margin-bottom: 0;
}

.detail-body {
  padding: 16px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.empty-state {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.quick-config {
  display: flex;
  gap: 8px;
  justify-content: center;
}
</style>