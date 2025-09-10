from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings
import logging

logger = logging.getLogger(__name__)


def create_engine() -> AsyncEngine:
	return create_async_engine(settings.database_url, pool_pre_ping=True, future=True)


engine: AsyncEngine = create_engine()
async_session_factory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def fetch_sp_statuses() -> dict[str, str]:
	"""
	Execute the configured stored procedures and return the status values.
	Supports multiple expected columns per procedure.
	Returns dict mapping expected column names to their string values.
	"""
	statuses: dict[str, str] = {}
	sp_config = settings.get_sp_config()
	
	if not sp_config:
		logger.warning("No stored procedures configured")
		return {"ERROR": "No stored procedures configured"}
	
	async with async_session_factory() as session:
		for config in sp_config:
			procedure_name = config["procedure"]
			expected_columns = config["columns"]
			
			try:
				query = text(f"EXEC {procedure_name}")
				result = await session.execute(query)
				row = result.first()
				
				if row:
					row_dict = dict(row._mapping)
					
					for expected_column in expected_columns:
						# Direct match first
						if expected_column in row_dict:
							statuses[expected_column] = str(row_dict[expected_column])
							continue
						# Fuzzy match
						matched_key = None
						for key in row_dict.keys():
							if expected_column.lower() in key.lower() or key.lower() in expected_column.lower():
								matched_key = key
								break
						if matched_key is not None:
							statuses[expected_column] = str(row_dict[matched_key])
						else:
							# Last resort: pick first value to avoid missing key
							first_value = next(iter(row_dict.values())) if row_dict else None
							statuses[expected_column] = str(first_value) if first_value is not None else "ERROR: No data returned"
				else:
					for expected_column in expected_columns:
						statuses[expected_column] = f"ERROR: No result from {procedure_name}"
					
			except Exception as e:
				logger.error(f"Error executing {procedure_name}: {e}")
				for expected_column in expected_columns:
					statuses[expected_column] = f"ERROR: {str(e)}"
	
	return statuses


