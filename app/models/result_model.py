import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)

    tool = Column(String(100), nullable=False)

    raw_output = Column(Text)
    parsed_data = Column(JSONB)

    ai_summary = Column(Text)
    risk_score = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())