from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.engine import Base


class JobSite(Base):
    __tablename__ = 'job_sites'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(String(255 * 5))
    link: Mapped[str] = mapped_column(String(255))


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    google_subject_id: Mapped[int] = mapped_column(unique=True)
