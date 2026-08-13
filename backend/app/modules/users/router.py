import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.exceptions import ResourceNotFoundException, SmartMESException
from app.api.deps import get_current_active_user, require_roles
from app.modules.users.models import User
from app.modules.roles.models import Role, UserRole
from app.modules.authentication.schemas import UserResponse, UserCreate, UserRoleUpdate

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account (Admin Only)",
    dependencies=[Depends(require_roles("ADMIN"))]
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new user account with hashed password and role associations.
    Requires ADMIN role.
    """
    # Check duplicate email or username
    stmt = select(User).where(
        or_(User.email == user_in.email, User.username == user_in.username)
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists"
        )

    # Hash password
    hashed_pwd = get_password_hash(user_in.password)

    new_user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=hashed_pwd,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=True,
    )
    db.add(new_user)
    await db.flush()

    # Assign roles if provided
    if user_in.role_ids:
        role_stmt = select(Role).where(Role.id.in_(user_in.role_ids))
        roles_res = await db.execute(role_stmt)
        assigned_roles = roles_res.scalars().all()
        new_user.roles = list(assigned_roles)

    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List all registered user accounts (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def list_users(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns list of all user accounts.
    """
    stmt = select(User).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user profile by ID"
)
async def get_user_by_id(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetches user account details by ID.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise ResourceNotFoundException(f"User with ID '{user_id}' not found")
    return user


@router.put(
    "/{user_id}/roles",
    response_model=UserResponse,
    summary="Update assigned roles for a user (Admin Only)",
    dependencies=[Depends(require_roles("ADMIN"))]
)
async def update_user_roles(
    user_id: uuid.UUID,
    role_update: UserRoleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Replaces user's current role assignments with the specified role IDs.
    Requires ADMIN role.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise ResourceNotFoundException(f"User with ID '{user_id}' not found")

    role_stmt = select(Role).where(Role.id.in_(role_update.role_ids))
    roles_res = await db.execute(role_stmt)
    new_roles = roles_res.scalars().all()

    user.roles = list(new_roles)
    await db.commit()
    await db.refresh(user)
    return user
