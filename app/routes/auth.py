from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import auth_service
from app.schemas.register_schema import RegisterSchema, LoginSchema, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterSchema, db: AsyncSession = Depends(get_db)):
    token, error = await auth_service.register_user(
        db=db,
        username=data.username,
        email=data.email,
        password=data.password
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"access_token": token}

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginSchema, db: AsyncSession = Depends(get_db)):
    token, error = await auth_service.login_user(
        db=db,
        email=data.email,
        password=data.password
    )
    if error:
        raise HTTPException(status_code=401, detail=error)
    return {"access_token": token}