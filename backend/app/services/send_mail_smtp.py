# backend/app/services/send_email.py
# Thay thế Resend bằng SMTP

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.settings import settings

async def send_password_reset_email(
    to_email: str,
    username: str,
    frontend_url: str,
    reset_token: str
) -> bool:
    """
    Gửi email reset password qua SMTP (Gmail/Outlook)
    """
    try:
        # Nếu không có SMTP config, chỉ log (development)
        if not settings.SMTP_ENABLED or not settings.SMTP_USERNAME:
            print(f"[DEV MODE] Password reset email would be sent to {to_email}")
            print(f"[DEV MODE] Reset URL: {frontend_url}/reset-password?token={reset_token}")
            return True
        
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; 
                          color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Reset Your Password</h2>
                <p>Hello {username},</p>
                <p>You requested to reset your password. Click the button below to reset it:</p>
                <a href="{reset_url}" class="button">Reset Password</a>
                <p>Or copy this link:</p>
                <p style="word-break: break-all; color: #007bff;">{reset_url}</p>
                <p>This link will expire in 15 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <div class="footer">
                    <p>Best regards,<br>Tervie Pal Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Tạo email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Reset Your Password - Tervie Pal"
        msg["From"] = settings.SMTP_USERNAME
        msg["To"] = to_email
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, "html"))
        
        # Gửi email qua SMTP
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()  # Enable encryption
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False