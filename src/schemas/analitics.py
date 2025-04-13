from pydantic import BaseModel
from datetime import date

class DailyReportCountResponse(BaseModel):
    date: date
    count: int