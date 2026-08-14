from datetime import timedelta
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.modules.users.models import User
from app.modules.roles.models import Role


@pytest.mark.asyncio
async def test_01_successful_login(async_client: AsyncClient, sample_admin: User):
    """Scenario 1: Valid credentials return access token."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin_user", "password": "AdminPass123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_02_invalid_username_email(async_client: AsyncClient, sample_admin: User):
    """Scenario 2: Reject non-existent username/email."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "non_existent_user", "password": "AdminPass123!"}
    )
    assert response.status_code == 401
    payload = response.json()
    assert payload["success"] is False


@pytest.mark.asyncio
async def test_03_invalid_password(async_client: AsyncClient, sample_admin: User):
    """Scenario 3: Reject incorrect password."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin_user", "password": "WrongPassword123!"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_04_password_is_hashed(sample_admin: User):
    """Scenario 4: Verify passwords are stored strictly as bcrypt hashes."""
    assert sample_admin.password_hash != "AdminPass123!"
    assert sample_admin.password_hash.startswith("$2b$") or sample_admin.password_hash.startswith("$2a$")
    assert verify_password("AdminPass123!", sample_admin.password_hash) is True


@pytest.mark.asyncio
async def test_05_access_token_generation(sample_admin: User):
    """Scenario 5: Verify JWT token generation and decoding."""
    token = create_access_token(subject=sample_admin.id)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == str(sample_admin.id)


@pytest.mark.asyncio
async def test_06_valid_token_authentication(async_client: AsyncClient, admin_token_headers: dict):
    """Scenario 6: Valid Bearer token grants access to protected /auth/me."""
    response = await async_client.get("/api/v1/auth/me", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin_user"


@pytest.mark.asyncio
async def test_07_invalid_token(async_client: AsyncClient):
    """Scenario 7: Malformed token header returns HTTP 401."""
    headers = {"Authorization": "Bearer invalid_malformed_jwt_token_string"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_08_expired_token(async_client: AsyncClient, sample_admin: User):
    """Scenario 8: Expired token returns HTTP 401."""
    expired_token = create_access_token(
        subject=sample_admin.id,
        expires_delta=timedelta(seconds=-10)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_09_missing_authentication(async_client: AsyncClient):
    """Scenario 9: Missing Authorization header returns HTTP 401."""
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_10_role_based_authorization_success(async_client: AsyncClient, admin_token_headers: dict):
    """Scenario 10: User with ADMIN role can list all users."""
    response = await async_client.get("/api/v1/users", headers=admin_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_11_unauthorized_role_rejection(async_client: AsyncClient, operator_token_headers: dict):
    """Scenario 11: User with OPERATOR role attempting ADMIN endpoint receives HTTP 403 Forbidden."""
    new_user_data = {
        "email": "newuser@test.com",
        "username": "newuser",
        "password": "Password123!",
        "role_ids": [1]
    }
    response = await async_client.post("/api/v1/users", json=new_user_data, headers=operator_token_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_12_inactive_user_rejection(async_client: AsyncClient, db_session: AsyncSession):
    """Scenario 12: Inactive user account is rejected upon login attempt."""
    inactive_user = User(
        email="inactive@test.com",
        username="inactive_user",
        password_hash=get_password_hash("Pass123!"),
        is_active=False
    )
    db_session.add(inactive_user)
    await db_session.commit()

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "inactive_user", "password": "Pass123!"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_13_auth_me_endpoint(async_client: AsyncClient, admin_token_headers: dict):
    """Scenario 13: /auth/me returns identity and role definitions."""
    response = await async_client.get("/api/v1/auth/me", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "roles" in data
    assert len(data["roles"]) > 0
    assert data["roles"][0]["name"] == "ADMIN"


@pytest.mark.asyncio
async def test_14_logout_behavior(async_client: AsyncClient, admin_token_headers: dict):
    """Scenario 14: Logout endpoint confirms session exit."""
    response = await async_client.post("/api/v1/auth/logout", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_15_user_uniqueness(async_client: AsyncClient, admin_token_headers: dict, sample_admin: User):
    """Scenario 15: Duplicate email/username registration returns HTTP 409 Conflict."""
    duplicate_data = {
        "email": sample_admin.email,
        "username": "unique_username",
        "password": "Password123!",
        "role_ids": []
    }
    response = await async_client.post("/api/v1/users", json=duplicate_data, headers=admin_token_headers)
    assert response.status_code == 409
