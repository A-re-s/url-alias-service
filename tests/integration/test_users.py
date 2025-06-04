import pytest


@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post(
        "/api/v1/register",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user(async_client):
    await async_client.post(
        "/api/v1/register",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Логин
    response = await async_client.post(
        "/api/v1/token",
        data={"username": "testuser", "password": "testpass", "grant_type": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_token_refresh(async_client):
    await async_client.post(
        "/api/v1/register",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    login_response = await async_client.post(
        "/api/v1/token",
        data={"username": "testuser", "password": "testpass", "grant_type": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = await async_client.post(
        "/api/v1/token/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_access_protected_route(async_client):
    await async_client.post(
        "/api/v1/register",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    login_response = await async_client.post(
        "/api/v1/token",
        data={"username": "testuser", "password": "testpass", "grant_type": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = login_response.json()["access_token"]

    response = await async_client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_register_existing_user(async_client):
    await async_client.post(
        "/api/v1/register",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    response = await async_client.post(
        "/api/v1/register",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this username already exists"


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client):
    await async_client.post(
        "/api/v1/register",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    response = await async_client.post(
        "/api/v1/token",
        data={
            "username": "testuser",
            "password": "wrongpass",
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_access_protected_route_without_token(async_client):
    response = await async_client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_invalid_refresh_token(async_client):
    response = await async_client.post(
        "/api/v1/token/refresh", json={"refresh_token": "invalid_refresh_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_invalid_access_token(async_client):
    response = await async_client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer invalid_access_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_missing_required_fields_register(async_client):
    response = await async_client.post(
        "/api/v1/register",
        data={"password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422

    response = await async_client.post(
        "/api/v1/register",
        data={"username": "testuser"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_token_format(async_client):
    response = await async_client.get(
        "/api/v1/users/me", headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
