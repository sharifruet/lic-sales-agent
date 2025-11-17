"""Authentication API routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint for admin authentication."""
    if not auth_service.authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = auth_service.create_access_token(request.username)
    return LoginResponse(
        access_token=access_token,
        expires_in=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

