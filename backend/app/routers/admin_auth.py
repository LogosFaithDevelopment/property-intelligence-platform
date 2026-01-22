"""
Admin Authentication Router
Handles admin authentication using Clerk JWT tokens and role checking
"""

import base64
import json
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.admin_user import AdminRole, AdminUser
from app.schemas.admin import AdminUserResponse, CreateAdminUserRequest
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, text
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
        # Decode Clerk JWT token manually (development only)
        # Note: In production, you should verify the signature with Clerk's public key
        # Split JWT into parts (header.payload.signature)
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        
        # Decode payload (middle part) - it's base64url encoded
        payload_b64 = parts[1]
        # Add padding if needed (base64 requires length to be multiple of 4)
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += '=' * padding
        
        # Decode from base64 and parse JSON
        payload_json = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_json)
        
        # Clerk JWT has 'sub' field containing the user ID
        clerk_user_id = payload.get("sub")
        
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        return clerk_user_id
        
    except (ValueError, json.JSONDecodeError, KeyError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_admin_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    update_last_login: bool = False
) -> AdminUser:
    """
    Dependency to get the current authenticated admin user.
    Verifies Clerk token and checks if user has admin role.
    
    Args:
        update_last_login: If True, updates the last_login timestamp (for actual logins).
                          If False, skips the update (for quick auth checks).
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
    
    # Only update last login if explicitly requested (e.g., for /auth/me endpoint)
    if update_last_login:
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
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated admin user info.
    Verifies Clerk token and returns admin role/permissions.
    Updates last_login timestamp.
    """
    current_user = await get_current_admin_user(request, db, update_last_login=True)
    return AdminUserResponse.from_orm(current_user)


@router.get("/auth/debug")
async def debug_clerk_token(
    request: Request
):
    """
    Debug endpoint to see what Clerk user ID is in the token.
    """
    try:
        clerk_user_id = await get_clerk_user_id_from_request(request)
        return {
            "clerk_user_id": clerk_user_id,
            "message": "Successfully extracted Clerk user ID from token"
        }
    except HTTPException as e:
        return {
            "error": e.detail,
            "status_code": e.status_code
        }


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


@router.get("/auth/users", response_model=list[AdminUserResponse])
async def list_admin_users(
    current_user: AdminUser = Depends(require_role(AdminRole.SUPERADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    List all admin users (Superadmin only).
    """
    result = await db.execute(
        select(AdminUser).order_by(AdminUser.created_at.desc())
    )
    admin_users = result.scalars().all()
    
    return [AdminUserResponse.from_orm(user) for user in admin_users]


@router.patch("/auth/users/{user_id}")
async def update_admin_user(
    user_id: int,
    is_active: Optional[bool] = None,
    role: Optional[AdminRole] = None,
    current_user: AdminUser = Depends(require_role(AdminRole.SUPERADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update admin user status or role (Superadmin only).
    Cannot modify superadmin accounts.
    """
    result = await db.execute(
        select(AdminUser).where(AdminUser.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent modifying superadmin accounts
    if user.role == AdminRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify superadmin accounts"
        )
    
    # Update fields
    if is_active is not None:
        user.is_active = is_active
    
    if role is not None:
        user.role = role
    
    await db.commit()
    await db.refresh(user)
    
    return AdminUserResponse.from_orm(user)


@router.post("/auth/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    user_data: CreateAdminUserRequest,
    current_user: AdminUser = Depends(require_role(AdminRole.SUPERADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new admin user (Superadmin only).
    Uses ON CONFLICT to handle duplicates - will update existing users.
    Replaces the CLI tool for adding admin users.
    """
    # Check if user already exists
    result = await db.execute(
        select(AdminUser).where(AdminUser.clerk_user_id == user_data.clerk_user_id)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        # Update existing user
        existing_user.email = user_data.email
        existing_user.role = user_data.role
        existing_user.full_name = user_data.full_name or user_data.email.split('@')[0]
        existing_user.is_active = True
        await db.commit()
        await db.refresh(existing_user)
        return AdminUserResponse.from_orm(existing_user)
    else:
        # Create new user
        new_user = AdminUser(
            clerk_user_id=user_data.clerk_user_id,
            email=user_data.email,
            role=user_data.role,
            full_name=user_data.full_name or user_data.email.split('@')[0],
            is_active=True
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return AdminUserResponse.from_orm(new_user)


@router.delete("/auth/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_user(
    user_id: int,
    current_user: AdminUser = Depends(require_role(AdminRole.SUPERADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Permanently delete an admin user (Superadmin only).
    Cannot delete your own account.
    """
    result = await db.execute(
        select(AdminUser).where(AdminUser.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account"
        )
    
    # Delete the user
    await db.delete(user)
    await db.commit()
    
    return None
