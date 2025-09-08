import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv


# Ensure values from config.env override any existing environment variables
# Explicitly load config.env from project root to avoid using a stale .env/system env
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / "config.env", override=True)


def get_env(name: str, default: str | None = None) -> str:
	value = os.getenv(name, default)
	if value is None:
		raise RuntimeError(f"Missing required environment variable: {name}")
	return value


class Settings:
	"""Runtime configuration loaded from environment variables."""

	# FastAPI
	app_name: str = os.getenv("APP_NAME", "db-activity-monitor")

	# Database
	database_url: str = get_env("DATABASE_URL")
	activity_table: str = get_env("ACTIVITY_TABLE")
	activity_timestamp_column: str = os.getenv("ACTIVITY_TIMESTAMP_COLUMN", "updated_at")

	# Monitor
	check_interval_seconds: int = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
	inactivity_threshold_minutes: int = int(os.getenv("INACTIVITY_THRESHOLD_MINUTES", "10"))
	alert_cooldown_minutes: int = int(os.getenv("ALERT_COOLDOWN_MINUTES", "30"))

	# Email (SMTP) - Optional
	smtp_host: str = os.getenv("SMTP_HOST", "")
	smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
	smtp_user: str = os.getenv("SMTP_USER", "")
	smtp_password: str = os.getenv("SMTP_PASSWORD", "")
	smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
	smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes", "on"}
	mail_sender: str = os.getenv("MAIL_SENDER", "")
	mail_recipients: list[str] = [r.strip() for r in os.getenv("MAIL_RECIPIENTS", "").split(",") if r.strip()]
	
	# Teams - Primary notification method
	teams_webhook_url: str = os.getenv("TEAMS_WEBHOOK_URL", "")
	enable_teams_notifications: bool = os.getenv("ENABLE_TEAMS_NOTIFICATIONS", "true").lower() in {"1", "true", "yes", "on"}
	enable_email_notifications: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() in {"1", "true", "yes", "on"}

	def inactivity_timedelta(self) -> timedelta:
		return timedelta(minutes=self.inactivity_threshold_minutes)

	def alert_cooldown_timedelta(self) -> timedelta:
		return timedelta(minutes=self.alert_cooldown_minutes)


settings = Settings()


