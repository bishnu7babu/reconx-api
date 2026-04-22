from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import target_service
from app.schemas.target_schema import TargetSchema
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/targets")
async def add_target(
    data: TargetSchema,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)   # ← gets real user_id from JWT
):
    target = await target_service.create_target(
        db=db,
        user_id=user_id,    # ← real user_id now
        host=data.host,
        label=data.label
    )
    return target