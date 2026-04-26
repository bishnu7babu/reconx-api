from fastapi import FastAPI
from app.routes import auth_route, targets_route, scan_route, result_route, ws_route
from app.database import engine
from app.db.base import Base

# import ALL models here so SQLAlchemy knows about them
from app.models import user_model, target_model, scan_model, result_model

app = FastAPI(title="reconX", version="1.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_route.router)
app.include_router(targets_route.router)
app.include_router(scan_route.router)
app.include_router(result_route.router)
app.include_router(ws_route.router)