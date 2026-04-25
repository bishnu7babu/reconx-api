from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.result_model import Result
from app.services.ai_service import generate_ai_summery
from uuid import UUID

router = APIRouter()

@router.get("/results/{scan_id}")
async def get_results(scan_id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):

    # fetch all results for this scan
    result = await db.execute(
        select(Result).where(Result.scan_id == scan_id)
    )
    results = result.scalars().all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found for this scan")

    return {"scan_id": scan_id, "results": results}


@router.get("/results/{scan_id}/ai-summary")
async def get_ai_summary(scan_id: UUID, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):

    # fetch all results for this scan
    result = await db.execute(
        select(Result).where(Result.scan_id == scan_id)
    )
    results = result.scalars().all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found for this scan")

    # extract raw output per tool
    nmap_output = next((r.raw_output for r in results if r.tool == "nmap"), "")
    harvester_output = next((r.raw_output for r in results if r.tool == "theharvester"), "")
    subfinder_output = next((r.raw_output for r in results if r.tool == "subfinder"), "")

    # call OpenAI
    ai_result = generate_ai_summery(
        nmap_output=nmap_output,
        harvester_output=harvester_output,
        subfinder_output=subfinder_output
    )

    return {
        "scan_id": scan_id,
        "ai_summary": ai_result
    }