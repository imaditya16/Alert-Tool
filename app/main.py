from __future__ import annotations

import logging
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import settings
from .monitor import ActivityMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title=settings.app_name)
monitor = ActivityMonitor()
scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup_event() -> None:
	# Schedule the periodic job
	trigger = IntervalTrigger(seconds=settings.check_interval_seconds)
	scheduler.add_job(monitor.check_and_alert, trigger, name="db-activity-check")
	scheduler.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
	if scheduler.running:
		scheduler.shutdown(wait=False)


@app.get("/health")
async def health() -> dict:
	return {"status": "ok"}


@app.get("/check-now")
async def manual_check() -> dict:
	return await monitor.check_and_alert()


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		"app.main:app",
		host="0.0.0.0",
		port=8000,
		reload=True,
		log_level="info"
	)


