from typing import Optional, List
from sqlalchemy import ForeignKey, LargeBinary, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from db.db import Base


class User(Base):
    fio: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    login: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(64), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)


class Role(Base):
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    users: Mapped[List[User]] = relationship(
        "User", backref="role", cascade="all, delete-orphan"
    )


class Document(Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary)


class Patient(Base):
    fio: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
