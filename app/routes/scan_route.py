from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.dependencies import get_current_user
from app.services.scan_service import create_scan_record
from datetime import datetime
from app.tasks.nmap_task import nmap_task
from app.services.target_service import get_target_by_id
from app.tasks.theharvester_task import theharvester_task

router = APIRouter()

@router.post("/scan/{target_id}")
async def create_scan(target_id: UUID, db: AsyncSession = Depends(get_db), user_id = Depends(get_current_user)):

    target = await get_target_by_id(db=db, target_id=str(target_id))
    if not target:
        raise HTTPException(status_code=404, detail="target not found")

    started_at = datetime.now()
    scan = await create_scan_record(db=db, target_id=str(target_id), status="queued", tools_used=[], started_at=started_at)
    nmap_task.delay(str(scan.id), str(target_id), target.host)

    theharvester_task.delay(str(scan.id), str(target_id), target.host)

    return {
        "scan_id": scan.id,
        "target_id": target_id,
        "host": target.host,
        "status": "queued"
    }