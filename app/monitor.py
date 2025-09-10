from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from .config import settings
from .db import fetch_sp_statuses
from .emailer import send_alert_email
from .teams_notifier import send_teams_notification

logger = logging.getLogger(__name__)


class ActivityMonitor:
	def __init__(self) -> None:
		self._last_alert_at_utc: Optional[datetime] = None

	async def check_and_alert(self) -> dict:
		"""Check stored procedure status and send an alert if needed."""
		try:
			return await self._check_stored_procedure()
		except Exception as e:
			logger.error(f"Error during database check: {e}", exc_info=True)
			return {"status": "error", "error": str(e)}

	async def _check_stored_procedure(self) -> dict:
		"""Check stored procedure status and send an alert if any status is not OK."""
		now = datetime.now(timezone.utc)
		statuses = await fetch_sp_statuses()
		
		logger.debug(f"Stored procedure statuses: {statuses}")
		
		# Check if all statuses are OK
		all_ok = all(status == settings.sp_ok_value for status in statuses.values())
		
		if all_ok:
			return {"status": "ok", "statuses": statuses}
		
		# Some status is not OK, check if we should send alert
		if not self._is_in_cooldown(now):
			logger.warning(f"Stored procedure check failed: {statuses}, sending alert")
			await self._send_sp_alert(statuses)
			self._last_alert_at_utc = now
			return {
				"status": "alert_sent",
				"statuses": statuses,
			}
		
		logger.info(f"Alert in cooldown until {self._cooldown_until()}")
		return {"status": "cooldown", "cooldown_until": self._cooldown_until().isoformat(), "statuses": statuses}

	def _is_in_cooldown(self, now: datetime) -> bool:
		if self._last_alert_at_utc is None:
			return False
		return now < self._cooldown_until()

	def _cooldown_until(self) -> datetime:
		assert self._last_alert_at_utc is not None
		return self._last_alert_at_utc + settings.alert_cooldown_timedelta()

	async def _send_sp_alert(self, statuses: dict[str, str]) -> None:
		"""Send alert for stored procedure check failure."""
		title = "⚠️ Database Update Health Check Failed"
		
		# Build status details
		status_details = []
		for key, value in statuses.items():
			status_icon = "✅" if value == settings.sp_ok_value else "❌"
			status_details.append(f"**{key}:** {status_icon} {value}")
		
		# Get procedure names from configuration
		sp_config = settings.get_sp_config()
		procedure_names = [config["procedure"] for config in sp_config]
		procedures_text = ", ".join(procedure_names) if procedure_names else "No procedures configured"
		
		message = (
			f"Database update health check failed.\n\n"
			f"**Stored Procedures:** {procedures_text}\n"
			f"**Expected OK Value:** {settings.sp_ok_value}\n\n"
			f"**Status Results:**\n" + "\n".join(status_details) + "\n\n"
			f"Please check the database update processes for any issues."
		)
		
		# Try Teams notification first (primary method)
		if settings.enable_teams_notifications and settings.teams_webhook_url:
			try:
				await send_teams_notification(title, message)
				logger.info("Teams notification sent successfully")
				return
			except Exception as e:
				logger.error(f"Failed to send Teams notification: {e}", exc_info=True)
		
		# Fallback to email if Teams fails or is disabled
		if settings.enable_email_notifications:
			subject = "Database Update Health Check Failed"
			# Get procedure names from configuration
			sp_config = settings.get_sp_config()
			procedure_names = [config["procedure"] for config in sp_config]
			procedures_text = ", ".join(procedure_names) if procedure_names else "No procedures configured"
			
			body = (
				"Database update health check failed.\n\n"
				f"Stored Procedures: {procedures_text}\n"
				f"Expected OK Value: {settings.sp_ok_value}\n\n"
				"Status Results:\n" + "\n".join([f"{key}: {value}" for key, value in statuses.items()]) + "\n"
			)
			try:
				await send_alert_email(subject, body)
				logger.info("Alert email sent successfully")
			except Exception as e:
				logger.error(f"Failed to send alert email: {e}", exc_info=True)
		else:
			logger.warning("Both Teams and email notifications are disabled")


