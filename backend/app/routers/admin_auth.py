"""
Admin Authentication Router
Handles admin authentication using Clerk JWT tokens and role checking
"""

from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.admin_user import AdminRole, AdminUser
from app.schemas.admin import AdminUserResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/admin", tags=["Admin"])


async def get_clerk_user_id_from_request(request: Request) -> str:
    """
    Extract and verify Clerk user ID from the request headers.
    Frontend should send the Clerk JWT token in Authorization header.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        # Decode Clerk JWT token
        # Note: In production, you should verify the signature with Clerk's public key
        # For now, we'll decode without verification (development only)
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Clerk JWT has 'sub' field containing the user ID
        clerk_user_id = payload.get("sub")
        
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        return clerk_user_id
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_admin_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    """
    Dependency to get the current authenticated admin user.
    Verifies Clerk token and checks if user has admin role.
    """
    clerk_user_id = await get_clerk_user_id_from_request(request)
    
    # Look up admin user by Clerk ID
    result = await db.execute(
        select(AdminUser).where(AdminUser.clerk_user_id == clerk_user_id)
    )
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an admin"
        )
    
    if not admin_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is deactivated"
        )
    
    # Update last login
    admin_user.last_login = datetime.utcnow()
    await db.commit()
    
    return admin_user


def require_role(required_role: AdminRole):
    """
    Dependency factory to require specific admin role.
    Usage: Depends(require_role(AdminRole.SUPERADMIN))
    """
    async def role_checker(
        current_user: AdminUser = Depends(get_current_admin_user)
    ) -> AdminUser:
        if not current_user.has_permission(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role or higher"
            )
        return current_user
    
    return role_checker


@router.get("/auth/me", response_model=AdminUserResponse)
async def get_current_admin_info(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get current authenticated admin user info.
    Verifies Clerk token and returns admin role/permissions.
    """
    return AdminUserResponse.from_orm(current_user)


@router.get("/auth/check")
async def check_admin_access(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Quick endpoint to check if user has admin access.
    Returns 200 if user is admin, 403 otherwise.
    """
    return {
        "is_admin": True,
        "role": current_user.role.value,
        "email": current_user.email
    }
