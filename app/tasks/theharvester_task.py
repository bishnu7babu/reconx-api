from app.celery_app import celery_app
from app.database import SyncSessionLocal
from app.models.scan_model import Scan
from sqlalchemy import select
from app.models.target_model import Target
from app.models.user_model import User
from uuid import UUID
import subprocess

from app.tasks.nmap_task import save_result


@celery_app.task()
def theharvester_task(scan_id: str, target_id: str, host: str):
    db = SyncSessionLocal()
    scan = None

    try:
        scan = db.execute(
            select(Scan).where(Scan.id == UUID(scan_id))
        ).scalar_one_or_none()

        if not scan:
            raise Exception(f"Scan {scan_id} not found in DB")

        scan.status = "running"
        db.commit()
        theharvester_output = run_theharvester(host)
        save_result(db, scan_id=scan_id, tool="theharvester",raw=theharvester_output)

        scan.status = "completed"
        db.commit()

    except Exception as e:
        if scan:
            scan.status = "failed"
            db.commit()
        raise e

    finally:
        db.close()


def run_theharvester(host: str) -> str:
    result = subprocess.run(
        ["theharvester", "-d", host, "-b", "crtsh,duckduckgo,otx,rapiddns"],
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.stdout