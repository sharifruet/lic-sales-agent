"""Authentication middleware for protected endpoints."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.src.services.auth_service import AuthService

security = HTTPBearer()
auth_service = AuthService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Dependency to get current authenticated user from JWT token."""
    token = credentials.credentials
    username = auth_service.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username

