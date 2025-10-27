#!/usr/bin/env python3
"""
Create First Admin User
Bootstraps the first admin user in production database
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import httpx
from app.database import async_engine
from sqlalchemy import text


async def create_admin_user(email: str):
    """Create admin user by email"""
    
    # Get Clerk secret key
    clerk_secret = os.getenv('CLERK_SECRET_KEY')
    if not clerk_secret:
        print("❌ Error: CLERK_SECRET_KEY environment variable not set")
        print("   Run: export CLERK_SECRET_KEY=sk_test_...")
        return False
    
    print(f"🔍 Looking up Clerk user for: {email}")
    
    # Get user from Clerk API
    headers = {
        "Authorization": f"Bearer {clerk_secret}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Search for user by email
            response = await client.get(
                f"https://api.clerk.com/v1/users?email_address={email}",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            users = response.json()
            
            if not users or len(users) == 0:
                print(f"❌ Error: No Clerk user found with email {email}")
                print("   Make sure you've signed up with this email in Clerk")
                return False
            
            user = users[0]
            clerk_user_id = user['id']
            user_email = user['email_addresses'][0]['email_address']
            
            print(f"✅ Found Clerk user:")
            print(f"   ID: {clerk_user_id}")
            print(f"   Email: {user_email}")
            
        except httpx.HTTPError as e:
            print(f"❌ Error fetching from Clerk API: {e}")
            return False
    
    print(f"\n📝 Creating admin user in production database...")
    
    # Insert into database
    async with async_engine.begin() as conn:
        # Check if user already exists
        result = await conn.execute(
            text("SELECT id, is_admin FROM users WHERE clerk_user_id = :clerk_id"),
            {"clerk_id": clerk_user_id}
        )
        existing = result.fetchone()
        
        if existing:
            user_id, is_admin = existing
            if is_admin:
                print(f"✅ User already exists and is an admin (ID: {user_id})")
                return True
            else:
                # Update to admin
                await conn.execute(
                    text("UPDATE users SET is_admin = true, updated_at = NOW() WHERE id = :user_id"),
                    {"user_id": user_id}
                )
                print(f"✅ Updated existing user to admin (ID: {user_id})")
                return True
        
        # Insert new admin user
        await conn.execute(
            text("""
                INSERT INTO users (clerk_user_id, email, is_admin, created_at, updated_at)
                VALUES (:clerk_id, :email, true, NOW(), NOW())
            """),
            {"clerk_id": clerk_user_id, "email": user_email}
        )
        
        print(f"✅ Created admin user in database")
        print(f"\n🎉 Success! {user_email} is now an admin!")
        print(f"   You can now log in to: https://logos.lotspecs.com")
        print(f"   You'll be redirected to: /admin/dashboard")
        return True


async def main():
    email = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not email:
        print("Usage: python create_first_admin.py <email>")
        print("Example: python create_first_admin.py adam@logos.com")
        sys.exit(1)
    
    success = await create_admin_user(email)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
