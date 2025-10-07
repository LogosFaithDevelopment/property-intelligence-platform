"""
Admin User Model
Manages role-based access control for the admin portal
Uses Clerk for authentication - this model only stores roles
"""

from datetime import datetime
from enum import Enum as PyEnum

from app.models.base import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String


class AdminRole(str, PyEnum):
    """Admin user roles with hierarchical permissions"""
    SUPERADMIN = "superadmin"  # Full access: manage users, delete data, all settings
    ADMIN = "admin"            # Standard access: view/edit submissions, export reports
    VIEWER = "viewer"          # Read-only: view submissions only


class AdminUser(BaseModel):
    """
    Admin user role assignment model
    Links Clerk user_id to admin roles for portal access
    
    Attributes:
        clerk_user_id: Clerk user ID (from Clerk authentication)
        email: User's email (synced from Clerk)
        role: Admin role (superadmin, admin, viewer)
        full_name: Admin's full name (synced from Clerk)
        is_active: Whether account is active
        last_login: Timestamp of last successful login
        created_by_id: ID of superadmin who created this role assignment
    """
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    clerk_user_id = Column(String(255), unique=True, nullable=False, index=True)  # Clerk user ID
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(Enum(AdminRole), nullable=False, default=AdminRole.ADMIN)
    
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_by_id = Column(Integer, nullable=True)  # ID of admin who created this user
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AdminUser(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    def has_permission(self, required_role: AdminRole) -> bool:
        """Check if user has required permission level"""
        role_hierarchy = {
            AdminRole.VIEWER: 1,
            AdminRole.ADMIN: 2,
            AdminRole.SUPERADMIN: 3
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
