from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any

from db.db import get_async_session
from models.models import Document

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)

@router.get("/documents/weekly", response_model=List[Dict[str, Any]])
async def get_documents_weekly_stats(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получение статистики созданных документов за последние 7 дней
    """
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)  
    
    query = (
        select(
            func.date(Document.created_at).label("date"),
            func.count().label("count")
        )
        .where(func.date(Document.created_at) >= seven_days_ago)
        .group_by(func.date(Document.created_at))
        .order_by(func.date(Document.created_at))
    )
    
    result = await session.execute(query)
    data = result.all()
    
    stats = {}
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        stats[date.isoformat()] = 0
    
    for row in data:
        date_str = row.date.isoformat()
        stats[date_str] = row.count
    
    formatted_stats = [
        {"date": date, "count": count} 
        for date, count in stats.items()
    ]
    
    return formatted_stats

@router.get("/documents/weekly/user/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_documents_weekly_stats(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    query = (
        select(
            func.date(Document.created_at).label("date"),
            func.count().label("count")
        )
        .where(
            (func.date(Document.created_at) >= seven_days_ago) &
            (Document.author_id == user_id)  
        )
        .group_by(func.date(Document.created_at))
        .order_by(func.date(Document.created_at))
    )
    
    result = await session.execute(query)
    data = result.all()
    
    stats = {}
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        stats[date.isoformat()] = 0
    
    for row in data:
        date_str = row.date.isoformat()
        stats[date_str] = row.count
    
    return [{"date": k, "count": v} for k, v in stats.items()]