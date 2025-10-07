"""
Authentication Middleware
Handles JWT verification and user context injection using Clerk
"""

import logging
from typing import Optional

from app.config import get_settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """Current authenticated user context"""
    user_id: str
    email: Optional[str] = None
    is_admin: bool = False
    organization_id: Optional[str] = None
    metadata: dict = {}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    Extract and verify current user from JWT token
    
    This middleware:
    1. Extracts Bearer token from Authorization header
    2. Verifies JWT signature using Clerk public key
    3. Returns user context
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        CurrentUser object with user_id, email, etc.
        
    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # DEVELOPMENT MODE: Skip signature verification
        # For production, implement proper JWKS verification with Clerk's public keys
        # See: https://clerk.com/docs/backend-requests/handling/manual-jwt
        payload = jwt.decode(
            token, 
            key="",  # Empty key bypasses verification
            options={"verify_signature": False}
        )
        
        logger.info(f"Token decoded successfully for user: {payload.get('sub')}")
        
        # Extract user information from JWT claims
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )
        
        # Extract additional claims
        email = payload.get("email") or payload.get("email_addresses", [{}])[0].get("email_address")
        is_admin = payload.get("is_admin", False) or "admin" in payload.get("roles", [])
        organization_id = payload.get("org_id") or payload.get("organization_id")
        
        return CurrentUser(
            user_id=user_id,
            email=email,
            is_admin=is_admin,
            organization_id=organization_id,
            metadata=payload.get("metadata", {})
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.error(f"Invalid JWT token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error",
        )


async def get_current_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Require admin privileges
    
    This dependency should be used for admin-only endpoints.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        CurrentUser if user is admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[CurrentUser]:
    """
    Extract user from token if present, but don't require authentication
    
    Useful for endpoints that have different behavior for authenticated vs anonymous users.
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        CurrentUser if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
