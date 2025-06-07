import pytest


@pytest.mark.asyncio
async def test_create_and_redirect_short_url(async_client, test_user):
    """Test basic URL creation and redirection flow."""
    create_response = await async_client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.com/path",
            "expire_minutes": 60,
            "desired_short_code": "custom123",
        },
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 201
    assert create_response.json()["short_code"] == "custom123"

    redirect_response = await async_client.get("/custom123")
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/path"


@pytest.mark.asyncio
async def test_url_expiration(async_client, test_user):
    """Test URL expiration behavior."""
    create_response = await async_client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.com",
            "expire_minutes": -1,
        },
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    response = await async_client.get(f"/{short_code}", follow_redirects=True)
    assert response.status_code == 410
    assert response.json()["detail"] == "URL has expired"


@pytest.mark.asyncio
async def test_click_limit_behavior(async_client, test_user):
    """Test URL click limit behavior."""
    create_response = await async_client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.com",
            "clicks_left": 2,
        },
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    response = await async_client.get(f"/{short_code}")
    assert response.status_code == 307

    response = await async_client.get(f"/{short_code}")
    assert response.status_code == 307

    response = await async_client.get(f"/{short_code}")
    assert response.status_code == 410
    assert response.json()["detail"] == "Click limit reached"


@pytest.mark.asyncio
async def test_url_deactivation(async_client, test_user):
    """Test URL deactivation functionality."""
    # Create URL
    create_response = await async_client.post(
        "/api/v1/urls",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    response = await async_client.get(f"/{short_code}")
    assert response.status_code == 307

    deactivate_response = await async_client.patch(
        f"/api/v1/urls/{short_code}",
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert deactivate_response.status_code == 200

    response = await async_client.get(f"/{short_code}")
    assert response.status_code == 410
    assert response.json()["detail"] == "URL is no longer active"


@pytest.mark.asyncio
async def test_url_listing_and_filtering(async_client, test_user):
    """Test URL listing with various filters."""
    urls = [
        ("https://example1.com", "promo"),
        ("https://example2.com", "promo"),
        ("https://example3.com", "docs"),
    ]

    for url, tag in urls:
        response = await async_client.post(
            "/api/v1/urls",
            json={"original_url": url, "tag": tag},
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
        )

        assert response.status_code == 201

    response = await async_client.get(
        "/api/v1/urls",
        params={"tag": "promo"},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await async_client.get(
        "/api/v1/urls",
        params={"is_active": True},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.asyncio
async def test_error_cases(async_client, test_user):
    """Test various error cases."""
    create_response = await async_client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.com",
            "desired_short_code": "unique123",
        },
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 201

    duplicate_response = await async_client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.com",
            "desired_short_code": "unique123",
        },
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert duplicate_response.status_code == 400
    assert "already in use" in duplicate_response.json()["detail"]

    response = await async_client.get("/nonexistent")
    assert response.status_code == 404

    response = await async_client.patch(
        "/api/v1/urls/nonexistent",
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert response.status_code == 404
