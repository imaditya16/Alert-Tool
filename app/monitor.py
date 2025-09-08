from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from dateutil import parser as date_parser

from .config import settings
from .db import fetch_latest_timestamp
from .emailer import send_alert_email
from .teams_notifier import send_teams_notification

logger = logging.getLogger(__name__)


class ActivityMonitor:
	def __init__(self) -> None:
		self._last_alert_at_utc: Optional[datetime] = None

	async def check_and_alert(self) -> dict:
		"""Check the latest row timestamp and send an alert if inactive too long."""
		try:
			has_row, latest_iso = await fetch_latest_timestamp()
			now = datetime.now(timezone.utc)

			if not has_row:
				logger.info("No rows found in activity table")
				return {"status": "no_rows", "now": now.isoformat()}

			latest_dt = self._to_utc(latest_iso)
			inactive_for = now - latest_dt
			threshold = settings.inactivity_timedelta()

			logger.debug(f"Last activity: {latest_dt}, Inactive for: {inactive_for}, Threshold: {threshold}")

			if inactive_for >= threshold:
				if not self._is_in_cooldown(now):
					logger.warning(f"Database inactive for {inactive_for}, sending alert")
					await self._send_inactivity_alert(latest_dt, inactive_for, threshold)
					self._last_alert_at_utc = now
					return {
						"status": "alert_sent",
						"inactive_for_seconds": int(inactive_for.total_seconds()),
					}
				logger.info(f"Alert in cooldown until {self._cooldown_until()}")
				return {"status": "cooldown", "cooldown_until": self._cooldown_until().isoformat()}

			return {"status": "ok", "inactive_for_seconds": int(inactive_for.total_seconds())}
		except Exception as e:
			logger.error(f"Error during database check: {e}", exc_info=True)
			return {"status": "error", "error": str(e)}

	def _to_utc(self, ts: str) -> datetime:
		parsed = date_parser.parse(ts)
		if parsed.tzinfo is None:
			parsed = parsed.replace(tzinfo=timezone.utc)
		return parsed.astimezone(timezone.utc)

	def _is_in_cooldown(self, now: datetime) -> bool:
		if self._last_alert_at_utc is None:
			return False
		return now < self._cooldown_until()

	def _cooldown_until(self) -> datetime:
		assert self._last_alert_at_utc is not None
		return self._last_alert_at_utc + settings.alert_cooldown_timedelta()

	async def _send_inactivity_alert(self, last_update: datetime, inactive_for, threshold) -> None:
		title = f"⚠️ Database Inactivity Alert - {int(threshold.total_seconds()//60)} minutes"
		message = (
			f"Database activity monitor detected inactivity.\n\n"
			f"**Activity table:** {settings.activity_table}\n"
			f"**Timestamp column:** {settings.activity_timestamp_column}\n"
			f"**Last update (UTC):** {last_update.isoformat()}\n"
			f"**Inactive for:** {inactive_for}\n"
			f"**Threshold:** {threshold}\n\n"
			f"Please check the database for any issues."
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
			subject = f"DB inactivity alert: no updates in {int(threshold.total_seconds()//60)} min"
			body = (
				"Database activity monitor detected inactivity.\n\n"
				f"Activity table: {settings.activity_table}\n"
				f"Timestamp column: {settings.activity_timestamp_column}\n"
				f"Last update (UTC): {last_update.isoformat()}\n"
				f"Inactive for: {inactive_for}\n"
				f"Threshold: {threshold}\n"
			)
			try:
				await send_alert_email(subject, body)
				logger.info("Alert email sent successfully")
			except Exception as e:
				logger.error(f"Failed to send alert email: {e}", exc_info=True)
		else:
			logger.warning("Both Teams and email notifications are disabled")


