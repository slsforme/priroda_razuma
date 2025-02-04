from repositories.roles import PatientRepository
from .base import Service


class RoleService(Service):
    def __init__(self, repository: PatientRepository):
        super().__init__(repository)
