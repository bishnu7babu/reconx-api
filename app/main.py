from fastapi import FastAPI
from app.routes import auth, targets
from app.database import engine
from app.db.base import Base

# import ALL models here so SQLAlchemy knows about them
from app.models import user, target, scan, result

app = FastAPI(title="reconX", version="1.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router)
app.include_router(targets.router)