from repositories.users import UserRepository
from repositories.roles import RoleRepository
from repositories.patients import PatientRepository
from repositories.documents import DocumentRepository

from services.users import UserService
from services.roles import RoleService
from services.patients import PatientService
from services.documents import DocumentService


user_repository = UserRepository()
role_repository = RoleRepository()
patient_repository = PatientRepository()
document_repository = DocumentRepository()

user_service = UserService(user_repository)
role_service = RoleService(role_repository)
patient_service = PatientService(patient_repository)
document_service = DocumentService(document_repository)


def get_user_service() -> UserService:
    return user_service

def get_role_service() -> RoleService:
    return role_service

def get_patient_service() -> PatientService:
    return patient_service

def get_document_service() -> DocumentService:
    return document_service


