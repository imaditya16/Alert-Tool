#!/usr/bin/env python3
"""
Debug email configuration
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from app.config import settings

async def debug_email():
    print("🔍 Debugging email configuration...")
    print(f"📧 SMTP Host: {settings.smtp_host}")
    print(f"📧 SMTP Port: {settings.smtp_port}")
    print(f"📧 SMTP User: {settings.smtp_user}")
    print(f"📧 SMTP Password: {'*' * len(settings.smtp_password) if settings.smtp_password else 'NOT SET'}")
    print(f"📧 Mail Sender: {settings.mail_sender}")
    print(f"📧 Mail Recipients: {settings.mail_recipients}")
    print(f"📧 Use TLS: {settings.smtp_use_tls}")
    print(f"📧 Use SSL: {settings.smtp_use_ssl}")
    print(f"📧 Email Enabled: {settings.enable_email_notifications}")
    
    print("\n🧪 Testing SMTP connection...")
    
    try:
        if settings.smtp_use_ssl:
            print("Using SSL connection...")
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as smtp:
                print("SSL connection established")
                smtp.login(settings.smtp_user, settings.smtp_password)
                print("✅ Authentication successful")
                
                # Create test message
                msg = MIMEText("Test email from database monitor", _charset="utf-8")
                msg["Subject"] = "Test Alert - Database Monitor"
                msg["From"] = settings.mail_sender
                msg["To"] = ", ".join(settings.mail_recipients)
                msg["Date"] = formatdate(localtime=True)
                
                smtp.sendmail(settings.mail_sender, settings.mail_recipients, msg.as_string())
                print("✅ Email sent successfully!")
                
        else:
            print("Using TLS connection...")
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
                print("SMTP connection established")
                if settings.smtp_use_tls:
                    smtp.starttls()
                    print("TLS started")
                smtp.login(settings.smtp_user, settings.smtp_password)
                print("✅ Authentication successful")
                
                # Create test message
                msg = MIMEText("Test email from database monitor", _charset="utf-8")
                msg["Subject"] = "Test Alert - Database Monitor"
                msg["From"] = settings.mail_sender
                msg["To"] = ", ".join(settings.mail_recipients)
                msg["Date"] = formatdate(localtime=True)
                
                smtp.sendmail(settings.mail_sender, settings.mail_recipients, msg.as_string())
                print("✅ Email sent successfully!")
                
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n🔧 Gmail Authentication Fix:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Generate a new app password for 'Mail'")
        print("3. Update SMTP_PASSWORD in config.env")
        print("4. Make sure 2-Step Verification is enabled")
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_email())
