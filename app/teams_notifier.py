from __future__ import annotations

import aiohttp
import json
from datetime import datetime
from typing import Optional

from .config import settings


async def send_teams_notification(
    title: str, 
    message: str, 
    webhook_url: Optional[str] = None
) -> None:
    """
    Send a notification to Microsoft Teams via webhook
    """
    # Use webhook URL from config or parameter
    webhook_url = webhook_url or settings.teams_webhook_url
    
    if not webhook_url:
        raise ValueError("Teams webhook URL not configured. Please set TEAMS_WEBHOOK_URL in your .env file")
    
    # Create Teams message card
    teams_message = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": title,
        "sections": [
            {
                "activityTitle": title,
                "activitySubtitle": f"Database Activity Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "activityImage": "https://img.icons8.com/color/96/000000/database.png",
                "text": message,
                "facts": [
                    {
                        "name": "Status",
                        "value": "⚠️ Database Inactivity Alert"
                    },
                    {
                        "name": "Time",
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    },
                    {
                        "name": "Threshold",
                        "value": f"{settings.inactivity_threshold_minutes} minutes"
                    }
                ]
            }
        ],
        "potentialAction": [
            {
                "@type": "OpenUri",
                "name": "Check Database",
                "targets": [
                    {
                        "os": "default",
                        "uri": "http://localhost:8000/check-now"
                    }
                ]
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=teams_message,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    print(f"✅ Teams notification sent successfully")
                else:
                    error_text = await response.text()
                    raise Exception(f"Teams webhook failed with status {response.status}: {error_text}")
                    
    except aiohttp.ClientError as e:
        error_msg = f"❌ Teams notification failed (network error): {e}"
        print(error_msg)
        raise Exception(error_msg)
        
    except Exception as e:
        error_msg = f"❌ Teams notification failed: {e}"
        print(error_msg)
        raise Exception(error_msg)


async def send_teams_activity_resumed_notification() -> None:
    """
    Send notification when database activity resumes
    """
    title = "🟢 Database Activity Resumed"
    message = "Database activity has been detected. The system is now active and monitoring continues."
    
    await send_teams_notification(title, message)


