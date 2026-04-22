from sqlalchemy.ext.asyncio import AsyncSession
from app.models.scan_model import Scan
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

async def create_scan_record(db: AsyncSession, target_id: str, status: str, tools_used: list, started_at: datetime):
    scan = Scan(
        id=uuid.uuid4(),
        target_id=target_id,
        status=status,
        tools_used=tools_used,
        started_at=started_at
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    return scan