from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings


def create_engine() -> AsyncEngine:
	return create_async_engine(settings.database_url, pool_pre_ping=True, future=True)


engine: AsyncEngine = create_engine()
async_session_factory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def fetch_latest_timestamp() -> tuple[bool, str | None]:
	"""
	Return (has_row, iso_timestamp_str or None)
	"""
	query = text(
		f"""
		SELECT {settings.activity_timestamp_column}
		FROM {settings.activity_table}
		ORDER BY {settings.activity_timestamp_column} DESC
		LIMIT 1
		"""
	)
	async with async_session_factory() as session:
		result = await session.execute(query)
		row = result.first()
		if not row:
			return False, None
		ts = row[0]
		# Support both datetime and string timestamps
		return True, (ts.isoformat() if hasattr(ts, "isoformat") else str(ts))


