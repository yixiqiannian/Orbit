import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ImapClient:
    """IMAP 邮件接收客户端"""
    
    def __init__(self, server: str, port: int = 993, use_ssl: bool = True):
        self.server = server
        self.port = port
        self.use_ssl = use_ssl
        self.conn: Optional[imaplib.IMAP4_SSL | imaplib.IMAP4] = None
    
    def connect(self, username: str, password: str) -> bool:
        """连接到IMAP服务器"""
        try:
            if self.use_ssl:
                self.conn = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.conn = imaplib.IMAP4(self.server, self.port)
            
            self.conn.login(username, password)
            logger.info(f"Connected to IMAP server {self.server}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            raise
    
    def disconnect(self):
        """断开连接"""
        if self.conn:
            try:
                self.conn.logout()
            except:
                pass
            self.conn = None
    
    def get_folders(self) -> List[str]:
        """获取邮箱文件夹列表"""
        if not self.conn:
            raise ConnectionError("Not connected to IMAP server")
        
        status, folders = self.conn.list()
        result = []
        if status == "OK":
            for folder in folders:
                folder_str = folder.decode()
                # 解析文件夹名称
                parts = folder_str.split('" "') 
                if len(parts) > 1:
                    name = parts[-1].strip('"')
                else:
                    name = folder_str.split()[-1].strip('"')
                result.append(name)
        return result
    
    def get_unread_count(self, folder: str = "INBOX") -> int:
        """获取未读邮件数量"""
        if not self.conn:
            raise ConnectionError("Not connected to IMAP server")
        
        self.conn.select(folder, readonly=True)
        status, messages = self.conn.search(None, "UNSEEN")
        if status == "OK":
            return len(messages[0].split()) if messages[0] else 0
        return 0
    
    def fetch_emails(self, folder: str = "INBOX", limit: int = 50) -> List[Dict]:
        """获取邮件列表"""
        if not self.conn:
            raise ConnectionError("Not connected to IMAP server")
        
        self.conn.select(folder, readonly=True)
        status, messages = self.conn.search(None, "ALL")
        
        if status != "OK":
            return []
        
        email_ids = messages[0].split()
        # 获取最新的 limit 封邮件
        email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
        email_ids.reverse()  # 最新的在前
        
        result = []
        for eid in email_ids:
            try:
                email_data = self._fetch_single_email(eid)
                if email_data:
                    email_data["folder"] = folder
                    result.append(email_data)
            except Exception as e:
                logger.error(f"Failed to fetch email {eid}: {e}")
                continue
        
        return result
    
    def _fetch_single_email(self, email_id: bytes) -> Optional[Dict]:
        """获取单封邮件详情"""
        status, msg_data = self.conn.fetch(email_id, "(RFC822)")
        if status != "OK":
            return None
        
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # 解析主题
        subject = self._decode_header(msg.get("Subject", ""))
        
        # 解析发件人
        sender = self._decode_header(msg.get("From", ""))
        
        # 解析收件人
        recipients_str = msg.get("To", "")
        cc_str = msg.get("Cc", "")
        
        # 解析正文
        body_text, body_html = self._parse_body(msg)
        
        # 检查是否有附件
        has_attachment = self._has_attachment(msg)
        
        # 解析日期
        received_at = self._parse_date(msg.get("Date"))
        
        return {
            "message_id": msg.get("Message-ID", ""),
            "uid": email_id.decode(),
            "subject": subject,
            "sender": sender,
            "recipients": recipients_str,
            "cc": cc_str,
            "body_text": body_text,
            "body_html": body_html,
            "has_attachment": has_attachment,
            "is_read": False,
            "is_starred": False,
            "received_at": received_at
        }
    
    def _decode_header(self, header: str) -> str:
        """解码邮件头部"""
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                charset = charset or "utf-8"
                try:
                    result.append(part.decode(charset))
                except:
                    result.append(part.decode("utf-8", errors="replace"))
            else:
                result.append(part)
        return " ".join(result)
    
    def _parse_body(self, msg: email.message.Message) -> Tuple[Optional[str], Optional[str]]:
        """解析邮件正文"""
        body_text = None
        body_html = None
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body_text = payload.decode(charset, errors="replace")
                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body_html = payload.decode(charset, errors="replace")
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                if content_type == "text/plain":
                    body_text = payload.decode(charset, errors="replace")
                elif content_type == "text/html":
                    body_html = payload.decode(charset, errors="replace")
        
        return body_text, body_html
    
    def _has_attachment(self, msg: email.message.Message) -> bool:
        """检查是否有附件"""
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                if "attachment" in content_disposition:
                    return True
        return False
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析邮件日期"""
        if not date_str:
            return None
        
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return None
    
    def mark_as_read(self, uid: str, folder: str = "INBOX") -> bool:
        """标记邮件为已读"""
        if not self.conn:
            raise ConnectionError("Not connected to IMAP server")
        
        try:
            self.conn.select(folder)
            self.conn.store(uid, "+FLAGS", "\\Seen")
            return True
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
            return False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
