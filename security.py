"""
Security utilities and middleware for the Data Extraction API.
Provides input sanitization, security headers, and rate limiting utilities.
"""

import re
import html
from typing import Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import time
from collections import defaultdict, deque

# Security configuration
MAX_TEXT_LENGTH = int(os.getenv("MAX_REQUEST_SIZE", 1048576))  # 1MB default
ALLOWED_EXTRACTION_TYPES = {"email_phone", "dates", "numbers", "urls", "all"}

# Simple in-memory rate limiter (for production, use Redis or similar)
class SimpleRateLimiter:
    """Simple in-memory rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] < now - self.window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) >= self.max_requests:
            return False
        
        # Add current request
        client_requests.append(now)
        return True

# Global rate limiter instance
rate_limiter = SimpleRateLimiter(
    max_requests=int(os.getenv("RATE_LIMIT_REQUESTS", 100)),
    window_seconds=int(os.getenv("RATE_LIMIT_WINDOW", 3600))
)

def sanitize_input_text(text: str) -> str:
    """
    Sanitize input text to prevent injection attacks and normalize content.
    
    Args:
        text: Raw input text
        
    Returns:
        Sanitized text
        
    Raises:
        HTTPException: If text is too long or contains suspicious content
    """
    if not text or not isinstance(text, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text input is required and must be a string"
        )
    
    # Check length limits
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Text input too large. Maximum {MAX_TEXT_LENGTH} characters allowed."
        )
    
    # HTML escape to prevent XSS
    sanitized = html.escape(text)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'data:text/html',  # Data URLs with HTML
        r'vbscript:',  # VBScript URLs
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized

def validate_extraction_type(extraction_type: str) -> str:
    """
    Validate and normalize extraction type.
    
    Args:
        extraction_type: The extraction type to validate
        
    Returns:
        Validated extraction type
        
    Raises:
        HTTPException: If extraction type is invalid
    """
    if not extraction_type or not isinstance(extraction_type, str):
        return "email_phone"  # Default
    
    extraction_type = extraction_type.lower().strip()
    
    if extraction_type not in ALLOWED_EXTRACTION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid extraction type. Allowed types: {', '.join(ALLOWED_EXTRACTION_TYPES)}"
        )
    
    return extraction_type

def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request, considering proxies.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for forwarded headers (common in production deployments)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"

def check_rate_limit(request: Request) -> None:
    """
    Check rate limit for the current request.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    client_ip = get_client_ip(request)
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "3600"}
        )

def get_security_headers() -> Dict[str, str]:
    """
    Get security headers to add to responses.
    
    Returns:
        Dictionary of security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }

class SecureHTTPBearer(HTTPBearer):
    """Enhanced HTTP Bearer authentication with additional security checks."""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        """
        Authenticate request with additional security checks.
        
        Args:
            request: FastAPI request object
            
        Returns:
            HTTP authorization credentials
            
        Raises:
            HTTPException: If authentication fails or security checks fail
        """
        # Check rate limit first
        check_rate_limit(request)
        
        # Perform standard bearer token authentication
        credentials = await super().__call__(request)
        
        # Additional security checks can be added here
        # For example: token blacklist, token expiration, etc.
        
        return credentials

# Enhanced security instance
security = SecureHTTPBearer()

def create_secure_response_headers() -> Dict[str, str]:
    """
    Create a complete set of security headers for API responses.
    
    Returns:
        Dictionary of security headers
    """
    headers = get_security_headers()
    
    # Add API-specific headers
    headers.update({
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })
    
    return headers

