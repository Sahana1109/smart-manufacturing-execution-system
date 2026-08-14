from typing import Callable, List, Optional
import uuid
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.modules.users.models import User

# OAuth2 Password Bearer scheme
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(reusable_oauth2)
) -> User:
    """
    FastAPI dependency that extracts Bearer token, decodes JWT, and returns authenticated User.
    Raises HTTP 401 Unauthorized if missing, invalid, or user not found.
    """
    if not token:
        # Fallback to Authorization header manual parse if present
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise UnauthorizedException("Authentication token is missing")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException("Invalid or expired authentication token")

    user_id_str = payload["sub"]
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise UnauthorizedException("Invalid user ID in token claim")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("User associated with token no longer exists")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensures user account is active.
    """
    if not current_user.is_active:
        raise UnauthorizedException("User account is disabled")
    return current_user


def require_roles(*allowed_roles: str) -> Callable:
    """
    FastAPI dependency factory enforcing Role-Based Access Control (RBAC).
    Raises HTTP 403 Forbidden if user does not possess at least one of the allowed roles.
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_role_names = [role.name for role in current_user.roles]
        
        # Superuser / ADMIN check or role match check
        has_permission = any(role in allowed_roles for role in user_role_names)
        if not has_permission:
            raise ForbiddenException(
                f"Action requires one of the following roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker
