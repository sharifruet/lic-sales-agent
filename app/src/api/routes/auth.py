"""Authentication API routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()
security = HTTPBearer(auto_error=False)  # Don't auto-raise on missing credentials


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class VerifyResponse(BaseModel):
    valid: bool
    username: Optional[str] = None
    expires_at: Optional[str] = None


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


@router.get("/verify", response_model=VerifyResponse)
async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """
    Verify JWT token.
    
    This endpoint verifies that the provided Bearer token is valid
    and returns token information including username and expiration time.
    
    Headers:
        Authorization: Bearer {token} (optional - if missing, returns valid=false)
    
    Response:
        - valid: true if token is valid, false otherwise
        - username: username from token (if valid)
        - expires_at: expiration timestamp (if valid)
    """
    # Handle missing credentials gracefully
    if not credentials:
        return VerifyResponse(valid=False)
    
    token = credentials.credentials
    
    # Verify token and get username
    username = auth_service.verify_token(token)
    if username is None:
        return VerifyResponse(valid=False)
    
    # Get expiration time
    expires_at = auth_service.get_token_expiration(token)
    expires_at_str = expires_at.isoformat() if expires_at else None
    
    return VerifyResponse(
        valid=True,
        username=username,
        expires_at=expires_at_str
    )

