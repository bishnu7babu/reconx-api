from app.celery_app import celery_app
from app.database import SyncSessionLocal
from app.models.scan_model import Scan
from app.models.result_model import Result
from app.models.target_model import Target   # ← add this
from app.models.user_model import User
from sqlalchemy import select
from uuid import UUID
import subprocess
import uuid


@celery_app.task
def scan_task(scan_id: str, target_id: str, host: str):

    db = SyncSessionLocal()
    scan = None   # ← initialize as None so except block works safely

    try:
        scan = db.execute(
            select(Scan).where(Scan.id == UUID(scan_id))  # ← UUID conversion
        ).scalar_one_or_none()

        if not scan:
            raise Exception(f"Scan {scan_id} not found in DB")

        scan.status = "running"
        db.commit()

        nmap_output = run_nmap(host)
        save_result(db, scan_id, tool="nmap", raw=nmap_output)

        scan.status = "completed"
        db.commit()

    except Exception as e:
        if scan:
            scan.status = "failed"   # ← scan not Scan
            db.commit()
        raise e

    finally:
        db.close()


def run_nmap(host: str) -> str:
    result = subprocess.run(
        ["nmap", "-sV", "-T4", "--open", host],
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.stdout


def save_result(db, scan_id: str, tool: str, raw: str):
    result = Result(
        id=uuid.uuid4(),
        scan_id=UUID(scan_id),
        tool=tool,
        raw_output=raw,
    )
    db.add(result)
    db.commit()