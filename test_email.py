#!/usr/bin/env python3
"""
Test email configuration for database monitoring
"""

import asyncio
from app.emailer import send_alert_email

async def test_email():
    try:
        print("🧪 Testing email configuration...")
        print("📧 Sending test email to: aditya.kumar@rategain.com")
        
        await send_alert_email(
            "Test Alert - Database Monitor", 
            "This is a test email to verify the email configuration is working correctly.\n\nIf you receive this, email alerts are properly configured!\n\nTest sent at: " + str(asyncio.get_event_loop().time())
        )
        print("✅ Email test completed successfully!")
        print("📬 Check your email inbox (including spam folder)")
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        print("\n🔧 Common fixes:")
        print("1. Check Gmail app password in config.env")
        print("2. Enable 2-Factor Authentication on Gmail")
        print("3. Verify SMTP settings")

if __name__ == "__main__":
    asyncio.run(test_email())
