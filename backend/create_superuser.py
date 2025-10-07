#!/usr/bin/env python3
"""
CLI script to create the first superuser admin account
Usage: python create_superuser.py
"""

import asyncio
import sys
from getpass import getpass

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.admin_user import AdminRole, AdminUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_superuser():
    """Interactive script to create a superuser account"""
    
    print("=" * 60)
    print("CREATE SUPERUSER ADMIN ACCOUNT")
    print("=" * 60)
    print()
    
    # Get user input
    full_name = input("Full Name: ").strip()
    if not full_name:
        print("❌ Full name is required")
        return
    
    email = input("Email: ").strip().lower()
    if not email or "@" not in email:
        print("❌ Valid email is required")
        return
    
    password = getpass("Password: ")
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        return
    
    password_confirm = getpass("Confirm Password: ")
    if password != password_confirm:
        print("❌ Passwords do not match")
        return
    
    print()
    print("Creating superuser account...")
    
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
                return
            
            # Hash password
            password_hash = pwd_context.hash(password)
            
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
            
        except Exception as e:
            print(f"❌ Error creating superuser: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(create_superuser())
