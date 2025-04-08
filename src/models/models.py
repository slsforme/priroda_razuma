from typing import Optional, List
from enum import Enum
from sqlalchemy import ForeignKey, LargeBinary, String, Integer, Boolean, Enum as SQLAlchemyEnum, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import Base


class SubDirectories(str, Enum):
    DIAGNOSTICS = "Диагностика"
    ANAMNESIS = "Анамнез"
    WORK_PLAN = "План работы"
    COMMENTS = "Комментарии специалистов" 
    PHOTOS_AND_VIDEOS = "Фотографии и Видео"


class User(Base):
    fio: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    login: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)  
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="author", cascade="all, delete-orphan"
    )


class Role(Base):
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    users: Mapped[List["User"]] = relationship(
        "User", backref="role", cascade="all, delete-orphan"
    )


class Document(Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary)
    
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    patient: Mapped["Patient"] = relationship(
        "Patient", back_populates="documents"
    )
    
    subdirectory_type: Mapped[SubDirectories] = mapped_column(
        SQLAlchemyEnum(SubDirectories), nullable=False
    )
    
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    author: Mapped[Optional["User"]] = relationship(
        "User", back_populates="documents"
    )
    
    @classmethod
    async def create_document(
        cls, 
        session: AsyncSession, 
        name: str, 
        data: bytes, 
        patient_id: int, 
        subdirectory_type: SubDirectories, 
        author_id: int
    ) -> "Document":
        document = cls(
            name=name,
            data=data,
            patient_id=patient_id,
            subdirectory_type=subdirectory_type,
            author_id=author_id
        )
        session.add(document)
        await session.flush()
        return document


class Patient(Base):
    fio: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="patient", cascade="all, delete-orphan"
    )
    
    async def get_documents_by_directory(self, session: AsyncSession, directory_type: SubDirectories) -> List[Document]:
        from sqlalchemy import select
        
        query = select(Document).where(
            Document.patient_id == self.id,
            Document.subdirectory_type == directory_type
        ).order_by(Document.created_at.desc())
        
        result = await session.execute(query)
        return result.scalars().all()


@event.listens_for(Patient, 'after_insert')
def create_default_subdirectories(mapper, connection, target):
    pass

async def ensure_patient_subdirectories(session: AsyncSession):
    from sqlalchemy import select
    
    result = await session.execute(select(Patient))
    patients = result.scalars().all()
    
    for patient in patients:
        for subdir_type in SubDirectories:
            docs = await patient.get_documents_by_directory(session, subdir_type)
            if not docs:
                pass