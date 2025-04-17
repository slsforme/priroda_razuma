from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

import asyncio

from metrics.metrics import update_metrics
from db.db import async_session_maker
from models.models import User, Document, Role, Patient
from config import logger

async def update_metrics_task():
    async with async_session_maker() as session:
        try:
            await update_metrics(session)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Metrics update error: {e}")
            raise

async def scheduled_metrics_update():
    while True:
        try:
            await update_metrics_task()
            logger.info("Metrics updated successfully")
        except Exception as e:
            logger.error(f"Failed to update metrics: {str(e)}")
        await asyncio.sleep(300)

def start_metrics_task():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(scheduled_metrics_update())
    else:
        loop.run_until_complete(scheduled_metrics_update())