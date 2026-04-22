import uuid
from sqlalchemy import Column, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    target_id = Column(UUID(as_uuid=True), ForeignKey("targets.id", ondelete="CASCADE"), nullable=False)

    status = Column(
        Enum("queued", "running", "completed", "failed", name="scan_status_enum"),
        nullable=False,
        default="queued"
    )

    tools_used = Column(JSONB)

    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))