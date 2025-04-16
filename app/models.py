import uuid

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {"schema": "geo_app"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    status: Mapped[str] = mapped_column(String, default="running")  # 'done' | 'faild'
    distances: Mapped[dict] = mapped_column(JSON, nullable=True)

    locations: Mapped[list["Location"]] = relationship(
        "Location", back_populates="task", cascade="all, delete-orphan"
    )


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = {"schema": "geo_app"}

    id: Mapped[int] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("geo_app.tasks.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    task: Mapped["Task"] = relationship("Task", back_populates="locations")
