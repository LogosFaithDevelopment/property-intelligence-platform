"""
Admin Authentication Schemas
Pydantic models for admin login/signup requests and responses
"""

from datetime import datetime
from typing import Optional

from app.models.admin_user import AdminRole
from pydantic import BaseModel, EmailStr


class AdminSignInRequest(BaseModel):
    """Admin sign-in request"""
    email: EmailStr
    password: str


class AdminUserResponse(BaseModel):
    """Admin user data for responses"""
    id: int
    email: str
    full_name: str
    role: AdminRole
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminSignInResponse(BaseModel):
    """Admin sign-in response with JWT token"""
    access_token: str
    token_type: str = "bearer"
    user: AdminUserResponse


class AdminUserCreate(BaseModel):
    """Schema for creating new admin users"""
    email: EmailStr
    password: str
    full_name: str
    role: AdminRole = AdminRole.ADMIN


class AdminUserUpdate(BaseModel):
    """Schema for updating admin users"""
    full_name: Optional[str] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None


class CreateAdminUserRequest(BaseModel):
    """Schema for creating admin users via API (replaces CLI tool)"""
    clerk_user_id: str
    email: EmailStr
    role: AdminRole
    full_name: Optional[str] = None
