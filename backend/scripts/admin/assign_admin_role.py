#!/usr/bin/env python3
"""
CLI script to assign admin roles to Clerk users
Usage: python assign_admin_role.py <clerk_user_id> <email> <role>
Example: python assign_admin_role.py user_2abc123XYZ adam@logos.com superadmin
"""

import asyncio
import sys

from app.database import AsyncSessionLocal
from app.models.admin_user import AdminRole, AdminUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def assign_admin_role(clerk_user_id: str, email: str, role: str, full_name: str = None):
    """Assign or update admin role for a Clerk user"""
    
    print("=" * 60)
    print("ASSIGN ADMIN ROLE TO CLERK USER")
    print("=" * 60)
    print()
    
    # Validate role
    try:
        admin_role = AdminRole(role.lower())
    except ValueError:
        print(f"❌ Invalid role: {role}")
        print(f"Valid roles: superadmin, admin, viewer")
        return False
    
    print(f"Clerk User ID: {clerk_user_id}")
    print(f"Email:         {email}")
    print(f"Role:          {admin_role.value}")
    print(f"Full Name:     {full_name or 'N/A'}")
    print()
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if user already exists with this clerk_user_id
            result = await db.execute(
                select(AdminUser).where(AdminUser.clerk_user_id == clerk_user_id)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Update existing user
                print(f"📝 Updating existing admin user (ID: {existing_user.id})...")
                existing_user.email = email.lower()
                existing_user.role = admin_role
                if full_name:
                    existing_user.full_name = full_name
                action = "updated"
            else:
                # Check if email exists with different clerk_user_id (update case)
                result = await db.execute(
                    select(AdminUser).where(AdminUser.email == email.lower())
                )
                user_by_email = result.scalar_one_or_none()
                
                if user_by_email:
                    # Update the temporary clerk_user_id with real one
                    print(f"📝 Updating temporary Clerk ID with real ID...")
                    user_by_email.clerk_user_id = clerk_user_id
                    user_by_email.role = admin_role
                    if full_name:
                        user_by_email.full_name = full_name
                    existing_user = user_by_email
                    action = "updated"
                else:
                    # Create new admin user
                    print(f"✨ Creating new admin user...")
                    existing_user = AdminUser(
                        clerk_user_id=clerk_user_id,
                        email=email.lower(),
                        full_name=full_name or email.split('@')[0].title(),
                        role=admin_role,
                        is_active=True
                    )
                    db.add(existing_user)
                    action = "created"
            
            await db.commit()
            await db.refresh(existing_user)
            
            print()
            print("=" * 60)
            print(f"✅ ADMIN USER {action.upper()} SUCCESSFULLY")
            print("=" * 60)
            print(f"ID:            {existing_user.id}")
            print(f"Clerk User ID: {existing_user.clerk_user_id}")
            print(f"Email:         {existing_user.email}")
            print(f"Name:          {existing_user.full_name}")
            print(f"Role:          {existing_user.role.value}")
            print(f"Active:        {existing_user.is_active}")
            print()
            print("🎉 This user can now access the admin portal!")
            print("   Sign in at: http://localhost:3000")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error assigning admin role: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            return False


async def list_admin_users():
    """List all admin users"""
    print("=" * 60)
    print("CURRENT ADMIN USERS")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AdminUser))
        users = result.scalars().all()
        
        if not users:
            print("No admin users found.")
            return
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"  Clerk ID:  {user.clerk_user_id}")
            print(f"  Email:     {user.email}")
            print(f"  Name:      {user.full_name}")
            print(f"  Role:      {user.role.value}")
            print(f"  Active:    {user.is_active}")
            print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Assign role:  python assign_admin_role.py <clerk_user_id> <email> <role> [full_name]")
        print("  List users:   python assign_admin_role.py --list")
        print()
        print("Examples:")
        print("  python assign_admin_role.py user_2abc123XYZ adam@logos.com superadmin 'Adam Silver'")
        print("  python assign_admin_role.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        asyncio.run(list_admin_users())
    elif len(sys.argv) >= 4:
        clerk_id = sys.argv[1]
        email = sys.argv[2]
        role = sys.argv[3]
        full_name = sys.argv[4] if len(sys.argv) > 4 else None
        
        success = asyncio.run(assign_admin_role(clerk_id, email, role, full_name))
        sys.exit(0 if success else 1)
    else:
        print("❌ Invalid arguments")
        print("Usage: python assign_admin_role.py <clerk_user_id> <email> <role> [full_name]")
        sys.exit(1)
