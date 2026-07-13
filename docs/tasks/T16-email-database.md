## 目标
设计邮箱模块的数据库表，实现 IMAP 接收邮件和 SMTP 发送邮件的客户端。

## 工作目录
G:\Orbit\backend

## 任务要求

### 1. 创建邮箱配置模型 (models/email_account.py)
创建 EmailAccount 模型，包含：
- 基本信息：name（邮箱名称）、email（邮箱地址）
- IMAP 配置：imap_server、imap_port、imap_ssl
- SMTP 配置：smtp_server、smtp_port、smtp_ssl
- 认证：username、password_encrypted（授权码/密码）
- 状态：is_active

### 2. 创建邮件模型 (models/email_message.py)
创建 EmailMessage 模型，包含：
- 关联：account_id
- 邮件信息：message_id、subject、sender、recipients、cc、body_text、body_html
- 状态：is_read、is_starred、has_attachment
- 时间：received_at

### 3. 实现 IMAP 客户端 (services/imap_client.py)
实现 ImapClient 类：
- connect(username, password) - 连接服务器
- get_folders() - 获取文件夹列表
- get_unread_count(folder) - 获取未读数量
- fetch_emails(folder, limit) - 获取邮件列表
- mark_as_read(uid) - 标记已读

### 4. 实现 SMTP 客户端 (services/smtp_client.py)
实现 SmtpClient 类：
- connect(username, password) - 连接服务器
- send_email(from_addr, to_addrs, subject, body, html, cc, attachments) - 发送邮件

### 5. 更新 requirements.txt
添加 secure-smtplib 依赖

### 6. 更新 models/__init__.py
导出 EmailAccount 和 EmailMessage

## 验收标准
- [ ] 数据库模型创建完成
- [ ] IMAP 客户端可连接、获取邮件、获取未读数
- [ ] SMTP 客户端可连接、发送邮件
- [ ] 模型正确导出
