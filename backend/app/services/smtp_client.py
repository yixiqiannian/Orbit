import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SmtpClient:
    """SMTP 邮件发送客户端"""
    
    def __init__(self, server: str, port: int = 465, use_ssl: bool = True):
        self.server = server
        self.port = port
        self.use_ssl = use_ssl
        self.conn: Optional[smtplib.SMTP_SSL | smtplib.SMTP] = None
    
    def connect(self, username: str, password: str) -> bool:
        """连接到SMTP服务器"""
        try:
            if self.use_ssl:
                context = ssl.create_default_context()
                self.conn = smtplib.SMTP_SSL(self.server, self.port, context=context)
            else:
                self.conn = smtplib.SMTP(self.server, self.port)
                self.conn.starttls()
            
            self.conn.login(username, password)
            logger.info(f"Connected to SMTP server {self.server}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            raise
    
    def disconnect(self):
        """断开连接"""
        if self.conn:
            try:
                self.conn.quit()
            except:
                pass
            self.conn = None
    
    def send_email(
        self,
        from_addr: str,
        to_addrs: List[str],
        subject: str,
        body: Optional[str] = None,
        html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict:
        """发送邮件
        
        Args:
            from_addr: 发件人地址
            to_addrs: 收件人地址列表
            subject: 邮件主题
            body: 纯文本正文
            html: HTML正文
            cc: 抄送地址列表
            attachments: 附件文件路径列表
        
        Returns:
            包含发送结果的字典
        """
        if not self.conn:
            raise ConnectionError("Not connected to SMTP server")
        
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["From"] = from_addr
        msg["To"] = ", ".join(to_addrs)
        msg["Subject"] = subject
        
        if cc:
            msg["Cc"] = ", ".join(cc)
        
        # 添加正文
        if body:
            msg.attach(MIMEText(body, "plain", "utf-8"))
        if html:
            msg.attach(MIMEText(html, "html", "utf-8"))
        
        # 添加附件
        if attachments:
            msg = self._attach_files(msg, attachments)
        
        # 收件人列表（包含抄送）
        all_recipients = to_addrs + (cc or [])
        
        try:
            self.conn.sendmail(from_addr, all_recipients, msg.as_string())
            logger.info(f"Email sent to {to_addrs}")
            return {
                "success": True,
                "message": "Email sent successfully",
                "recipients": all_recipients
            }
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "message": str(e),
                "recipients": all_recipients
            }
    
    def _attach_files(self, msg: MIMEMultipart, attachments: List[str]) -> MIMEMultipart:
        """添加附件"""
        for file_path in attachments:
            try:
                path = Path(file_path)
                if not path.exists():
                    logger.warning(f"Attachment not found: {file_path}")
                    continue
                
                with open(path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={path.name}"
                )
                msg.attach(part)
            except Exception as e:
                logger.error(f"Failed to attach file {file_path}: {e}")
        
        return msg
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
