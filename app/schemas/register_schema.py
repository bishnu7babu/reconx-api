from pydantic import BaseModel, EmailStr

class RegisterSchema(BaseModel):
    username: str
    email: EmailStr        # auto validates email format
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"