from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.engine import Base


class JobSite(Base):
    __tablename__ = 'job_sites'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255 * 5))
