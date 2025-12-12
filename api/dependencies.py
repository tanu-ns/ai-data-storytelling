from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from .database import get_db
from .models import User, Tenant

# Mocking Auth for Initial Dev (until Keycloak is fully wired)
# In production, this would verify the Bearer token against Keycloak's public key.

async def get_current_user(
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    db: Session = Depends(get_db)
):
    """
    Simulates getting the current user. 
    For MVP Local dev without full Keycloak UI flow yet, we can pass user email in header.
    In real flow, we decode JWT.
    """
    if not x_user_email:
        # Default mock user for convenience if no header
        # In real prod, raise 401
        return None 
        
    user = db.query(User).filter(User.email == x_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_tenant(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resolves the tenant for the current request.
    """
    if not user:
         # Fallback for dev: return first tenant or raise
         # For now, let's just return None to force header usage in tests
         return None

    return user.tenant
