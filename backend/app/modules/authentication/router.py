from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.exceptions import UnauthorizedException
from app.api.deps import get_current_active_user
from app.modules.users.models import User
from app.modules.authentication.schemas import Token, LoginRequest, UserResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user & issue JWT Access Token",
    status_code=status.HTTP_200_OK
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates user with username or email and password.
    Returns Bearer JWT token upon success or HTTP 401 on invalid credentials.
    """
    stmt = select(User).where(
        or_(
            User.username == login_data.username_or_email,
            User.email == login_data.username_or_email
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("Invalid username or password")

    if not verify_password(login_data.password, user.password_hash):
        raise UnauthorizedException("Invalid username or password")

    if not user.is_active:
        raise UnauthorizedException("Account is inactive")

    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get currently authenticated user identity and roles"
)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns current authenticated user details, active status, and assigned roles.
    """
    return current_user


@router.post(
    "/logout",
    summary="Logout user & invalidate session"
)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Confirms client token invalidation.
    """
    return {
        "success": True,
        "message": "Successfully logged out. Please discard local token."
    }
