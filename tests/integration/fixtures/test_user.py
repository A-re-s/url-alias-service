import pytest_asyncio


@pytest_asyncio.fixture(scope="function")
async def test_user(async_client):
    response = await async_client.post(
        "/api/v1/register",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response = await async_client.post(
        "/api/v1/token",
        data={"username": "testuser", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    data = response.json()
    return data
