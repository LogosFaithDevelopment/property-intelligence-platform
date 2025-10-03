"""
Authentication Router
Handles Clerk webhook integration and user session management
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import httpx
import json
import hmac
import hashlib
import logging

from app.database import get_db
from app.config import get_settings
from app.models.church import Church
from app.schemas.base import SuccessResponse, ErrorResponse

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer(auto_error=False)

router = APIRouter()


class ClerkWebhookHandler:
    """Handle Clerk webhook events"""
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verify Clerk webhook signature"""
        try:
            # Clerk uses HMAC-SHA256
            expected_signature = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Clerk sends signature as "v1,<signature>"
            if signature.startswith("v1,"):
                signature = signature[3:]
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
    
    @staticmethod
    async def handle_user_created(data: dict, db: AsyncSession):
        """Handle user.created webhook"""
        user_id = data.get("id")
        email = data.get("email_addresses", [{}])[0].get("email_address")
        
        if not user_id or not email:
            logger.warning("Incomplete user data in webhook")
            return
        
        # Check if this is a church registration
        # (In a real implementation, you might have a temporary registration table)
        logger.info(f"New user created: {user_id} ({email})")
    
    @staticmethod
    async def handle_user_updated(data: dict, db: AsyncSession):
        """Handle user.updated webhook"""
        user_id = data.get("id")
        logger.info(f"User updated: {user_id}")
    
    @staticmethod
    async def handle_user_deleted(data: dict, db: AsyncSession):
        """Handle user.deleted webhook"""
        user_id = data.get("id")
        logger.info(f"User deleted: {user_id}")


@router.post("/webhooks/clerk", response_model=SuccessResponse)
async def clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Clerk webhooks for user events
    """
    if not settings.clerk_webhook_secret:
        raise HTTPException(
            status_code=501,
            detail="Webhook secret not configured"
        )
    
    # Get the signature from headers
    signature = request.headers.get("svix-signature")
    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing webhook signature"
        )
    
    # Read the payload
    payload = await request.body()
    
    # Verify the webhook signature
    if not ClerkWebhookHandler.verify_webhook_signature(
        payload, signature, settings.clerk_webhook_secret
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )
    
    try:
        # Parse the webhook payload
        webhook_data = json.loads(payload)
        event_type = webhook_data.get("type")
        data = webhook_data.get("data", {})
        
        # Handle different event types
        handler = ClerkWebhookHandler()
        
        if event_type == "user.created":
            await handler.handle_user_created(data, db)
        elif event_type == "user.updated":
            await handler.handle_user_updated(data, db)
        elif event_type == "user.deleted":
            await handler.handle_user_deleted(data, db)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
        
        return SuccessResponse(message="Webhook processed successfully")
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed"
        )


@router.get("/verify-token")
async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Verify JWT token from Clerk (for debugging)
    In production, use Clerk's SDK for proper token verification
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="No authorization token provided"
        )
    
    token = credentials.credentials
    
    # In a real implementation, verify the JWT token with Clerk
    # For now, just return basic info
    return {
        "message": "Token verification endpoint",
        "token_length": len(token),
        "note": "Implement proper JWT verification with Clerk SDK"
    }


@router.get("/user-info")
async def get_user_info(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    # In a real implementation:
    # 1. Verify JWT token with Clerk
    # 2. Extract user ID from token
    # 3. Look up associated church/user data
    
    return {
        "message": "User info endpoint",
        "note": "Implement with Clerk SDK integration"
    }


@router.post("/session/refresh")
async def refresh_session():
    """
    Refresh user session
    """
    return {
        "message": "Session refresh endpoint",
        "note": "Implement session refresh logic"
    }


@router.post("/logout")
async def logout():
    """
    Handle user logout
    """
    return SuccessResponse(message="Logout successful")


# Health check for auth system
@router.get("/health")
async def auth_health():
    """Health check for authentication system"""
    
    status_info = {
        "status": "healthy",
        "clerk_configured": bool(settings.clerk_secret_key),
        "webhook_configured": bool(settings.clerk_webhook_secret),
    }
    
    # Test Clerk API connectivity (optional)
    try:
        if settings.clerk_secret_key:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {settings.clerk_secret_key}"}
                response = await client.get(
                    "https://api.clerk.com/v1/users",
                    headers=headers,
                    params={"limit": 1},
                    timeout=5.0
                )
                status_info["clerk_api_status"] = "connected" if response.status_code == 200 else "error"
        else:
            status_info["clerk_api_status"] = "not_configured"
    except Exception as e:
        status_info["clerk_api_status"] = f"error: {str(e)}"
    
    return status_info
