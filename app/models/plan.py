# Plan entity: subscription limits (max documents, max upload size).

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    max_documents: Mapped[int] = mapped_column(Integer, nullable=False)
    max_file_size_mb: Mapped[int] = mapped_column(Integer, nullable=False)
