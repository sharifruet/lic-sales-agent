"""Rate limiting middleware for FastAPI."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
from app.src.services.rate_limiter_service import RateLimiterService
from app.src.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis."""
    
    def __init__(self, app: ASGIApp, rate_limiter: RateLimiterService = None):
        """Initialize rate limiting middleware."""
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiterService()
        # Paths to exclude from rate limiting
        self.excluded_paths = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        }
        # Paths with specific rate limit types
        self.path_limits = {
            "/api/conversation/message": "conversation_message",
            "/api/leads": "lead_creation",
            "/api/auth/login": "auth_login",
        }
    
    def _get_identifier(self, request: Request) -> str:
        """Get identifier for rate limiting (IP address, session_id, or user_id)."""
        # Try to get session_id from query params or headers
        session_id = request.query_params.get("session_id") or request.headers.get("X-Session-ID")
        if session_id:
            return f"session:{session_id}"
        
        # Try to get user_id from JWT token (if authenticated)
        # This would require parsing the Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Extract user from token (simplified - would need JWT decoding)
            # For now, use IP for authenticated users too
            pass
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        # Handle forwarded IPs (if behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in chain
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _get_limit_type(self, request: Request) -> str:
        """Get rate limit type for the request path."""
        path = request.url.path
        
        # Check for specific path limits
        if path in self.path_limits:
            return self.path_limits[path]
        
        # Check for API routes
        if path.startswith("/api/"):
            return "api_call"
        
        # Default to API call limit
        return "api_call"
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Process request through rate limiting middleware."""
        # Skip rate limiting for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Get identifier and limit type
        identifier = self._get_identifier(request)
        limit_type = self._get_limit_type(request)
        
        # Check rate limit
        allowed, remaining, retry_after = await self.rate_limiter.check_limit(
            identifier,
            limit_type
        )
        
        if not allowed:
            # Rate limit exceeded
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.rate_limiter.limits.get(limit_type, (60, 60))[0]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after)
                }
            )
        
        # Request allowed, proceed
        response = await call_next(request)
        
        # Add rate limit headers to response
        limit_info = await self.rate_limiter.get_limit_info(identifier, limit_type)
        response.headers["X-RateLimit-Limit"] = str(limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(limit_info["reset"])
        
        return response

