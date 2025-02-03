from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, select, delete

from db.db import connection
from models.models import Patient
from .base import BaseRepository


class PatientRepository(BaseRepository):
    def __init__(self):
        super().__init__(Patient)
