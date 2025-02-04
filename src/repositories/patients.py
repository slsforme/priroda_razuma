from models.models import Patient
from .base import BaseRepository


class PatientRepository(BaseRepository):
    def __init__(self):
        super().__init__(Patient)
