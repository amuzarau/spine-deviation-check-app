import uuid
from datetime import datetime

from sqlalchemy import Column, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB

from backend.app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, nullable=False)  # ← REQUIRED FIELD!
    role = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Screening(Base):
    __tablename__ = "screenings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.utcnow)

    frontal_risk = Column(Text, nullable=False)
    sagittal_risk = Column(Text, nullable=False)
    overall_risk = Column(Text, nullable=False)

    metrics = Column(JSONB, nullable=False)
    explanation = Column(JSONB, nullable=False)
