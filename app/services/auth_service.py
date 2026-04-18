from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.config import settings
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import uuid

# bcrypt context — handles hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hash a plain password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# verify plain password against stored hash
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# create JWT token containing user_id
def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,       # sub = subject = who this token belongs to
        "exp": expire         # exp = expiry time
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

# decode JWT token and return user_id
def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")   # returns user_id
    except JWTError:
        return None

# REGISTER — create new user
async def register_user(db: AsyncSession, username: str, email: str, password: str):
    # check if email already exists
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        return None, "email already exists"

    # check if username already exists
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        return None, "username already exists"

    # create new user with hashed password
    user = User(
        id=uuid.uuid4(),
        username=username,
        email=email,
        password=hash_password(password)   # NEVER store plain password
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # generate JWT token
    token = create_access_token(str(user.id))
    return token, None

# LOGIN — verify credentials and return token
async def login_user(db: AsyncSession, email: str, password: str):
    # find user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # user not found OR wrong password
    if not user or not verify_password(password, user.password):
        return None, "invalid email or password"

    # generate JWT token
    token = create_access_token(str(user.id))
    return token, None