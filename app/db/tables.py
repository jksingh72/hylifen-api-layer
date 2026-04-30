import uuid
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ExampleRecord(Base):
    """
    Example ORM table — copy this pattern for each new module.
    Run `uv run alembic revision --autogenerate -m "add example_records"` after adding a table.
    """
    __tablename__ = "example_records"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
