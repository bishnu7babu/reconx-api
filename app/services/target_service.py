from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.target_model import Target
import uuid

# CREATE — insert new target
async def create_target(db: AsyncSession, user_id: str, host: str, label: str):
    target = Target(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id),
        host=host,
        label=label
    )
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return target

# GET ALL — fetch all targets for a user
async def get_targets(db: AsyncSession, user_id: str):
    result = await db.execute(
        select(Target).where(Target.user_id == user_id)
    )
    return result.scalars().all()

# GET ONE — fetch single target by id
async def get_target_by_id(db: AsyncSession, target_id: str):
    result = await db.execute(
        select(Target).where(Target.id == target_id)
    )
    return result.scalar_one_or_none()

# DELETE — remove target
async def delete_target(db: AsyncSession, target_id: str):
    await db.execute(
        delete(Target).where(Target.id == target_id)
    )
    await db.commit()