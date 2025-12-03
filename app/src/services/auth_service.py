"""Authentication service for admin endpoints."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.src.config import settings


class AuthService:
    """Service for JWT-based authentication."""
    
    SECRET_KEY = settings.jwt_secret_key
    ALGORITHM = settings.jwt_algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_expire_minutes
    
    def create_access_token(self, username: str) -> str:
        """Create JWT token."""
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": username,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return username."""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
    
    def get_token_payload(self, token: str) -> Optional[dict]:
        """Get token payload without verification (for expiration check)."""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """Get token expiration time."""
        payload = self.get_token_payload(token)
        if payload is None:
            return None
        
        exp = payload.get("exp")
        if exp is None:
            return None
        
        # Convert Unix timestamp to datetime
        return datetime.utcfromtimestamp(exp)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials (simple version - extend for production)."""
        # Simple hardcoded admin for Phase 1
        # TODO: Replace with proper user database/auth in production
        admin_username = "admin"
        admin_password = "admin"  # Should be hashed in production
        
        return username == admin_username and password == admin_password

