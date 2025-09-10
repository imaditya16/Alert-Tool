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

	# Monitor
	check_interval_seconds: int = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
	alert_cooldown_minutes: int = int(os.getenv("ALERT_COOLDOWN_MINUTES", "10"))
	
	# Stored procedure mode only
	check_mode: str = "stored_procedure"
	
	# Stored procedure configuration - flexible for multiple procedures
	sp_ok_value: str = os.getenv("SP_OK_VALUE", "OK")
	
	# Multiple stored procedures configuration
	# Format: "procedure1:col1|col2,procedure2:colA|colB"
	# Example: "dbo.usp_CheckUpdateStatus:HotelUpdateStatus|ChannelStatsStatus"
	sp_procedures: str = os.getenv(
		"SP_PROCEDURES",
		"dbo.usp_CheckUpdateStatus:HotelUpdateStatus|ChannelStatsStatus",
	)
	
	def get_sp_config(self) -> list[dict[str, list[str]]]:
		"""
		Parse stored procedure configuration into a list of dictionaries.
		Returns: [{"procedure": "dbo.usp_CheckUpdateStatus", "columns": ["HotelUpdateStatus", "ChannelStatsStatus"]}, ...]
		"""
		procedures: list[dict[str, list[str]]] = []
		if not self.sp_procedures.strip():
			return procedures
		
		for item in self.sp_procedures.split(','):
			item = item.strip()
			if not item:
				continue
			if ':' in item:
				procedure, columns_str = item.split(':', 1)
				columns = [c.strip() for c in columns_str.split('|') if c.strip()]
				if not columns:
					# Fallback: derive a single column name from the procedure
					columns = [procedure.strip().split('.')[-1]]
				procedures.append({
					"procedure": procedure.strip(),
					"columns": columns,
				})
			else:
				# Fallback: use procedure name as single column
				procedures.append({
					"procedure": item.strip(),
					"columns": [item.strip().split('.')[-1]],
				})
		
		return procedures


settings = Settings()


