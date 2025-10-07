#!/usr/bin/env python3
"""
Simple CLI script to create the first superuser admin account
Usage: python create_superuser_simple.py
"""

import asyncio
import sys

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.admin_user import AdminRole, AdminUser


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Ensure password is bytes and truncate to 72 bytes if needed
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


async def create_superuser(email: str, password: str, full_name: str):
    """Create a superuser account with provided credentials"""
    
    print("=" * 60)
    print("CREATE SUPERUSER ADMIN ACCOUNT")
    print("=" * 60)
    print()
    
    # Validate inputs
    if not full_name:
        print("❌ Full name is required")
        return False
    
    if not email or "@" not in email:
        print("❌ Valid email is required")
        return False
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        return False
    
    print(f"Creating superuser: {full_name} ({email})...")
    
    # Create database session
    async with AsyncSessionLocal() as db:
        try:
            # Check if user already exists
            result = await db.execute(
                select(AdminUser).where(AdminUser.email == email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ User with email '{email}' already exists")
                return False
            
            # Hash password
            password_hash = hash_password(password)
            
            # Create superuser
            superuser = AdminUser(
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                role=AdminRole.SUPERADMIN,
                is_active=True
            )
            
            db.add(superuser)
            await db.commit()
            await db.refresh(superuser)
            
            print()
            print("=" * 60)
            print("✅ SUPERUSER CREATED SUCCESSFULLY")
            print("=" * 60)
            print(f"ID:        {superuser.id}")
            print(f"Email:     {superuser.email}")
            print(f"Name:      {superuser.full_name}")
            print(f"Role:      {superuser.role.value}")
            print(f"Active:    {superuser.is_active}")
            print()
            print("You can now sign in to the admin portal at:")
            print("👉 http://localhost:3000/admin/signin")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating superuser: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            return False


if __name__ == "__main__":
    # Default credentials - change these!
    EMAIL = "adam@logos.com"
    PASSWORD = "admin123"  # Change this to something secure
    FULL_NAME = "Adam Silver"
    
    # You can also pass arguments
    if len(sys.argv) == 4:
        EMAIL = sys.argv[1]
        PASSWORD = sys.argv[2]
        FULL_NAME = sys.argv[3]
    
    success = asyncio.run(create_superuser(EMAIL, PASSWORD, FULL_NAME))
    sys.exit(0 if success else 1)
