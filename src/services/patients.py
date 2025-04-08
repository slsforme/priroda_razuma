from repositories.patients import PatientRepository
from .base import BaseService


class PatientService(BaseService):
    def __init__(self, repository: PatientRepository):
        super().__init__(repository)
