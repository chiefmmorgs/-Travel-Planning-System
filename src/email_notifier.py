import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailNotifier:
    """Send email notifications"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email = os.getenv('EMAIL_FROM')
        self.password = os.getenv('EMAIL_PASSWORD')
    
    def send_digest(self, to_email: str, digest: dict):
        """Send weekly digest via email"""
        if not self.email or not self.password:
            print("⚠️  Email not configured. Add EMAIL_FROM and EMAIL_PASSWORD to .env")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to_email
        msg['Subject'] = "Your Weekly Travel Digest"
        
        body = digest['digest']['recommendations']
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            print(f"✅ Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False
