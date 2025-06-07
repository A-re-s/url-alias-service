from datetime import datetime, timedelta, timezone

import pytest

from models.click_stats import ClickStatModel


@pytest.mark.asyncio
async def test_url_click_tracking(async_client, test_user):
    create_response = await async_client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.com",
            "expire_minutes": 60,
        },
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    for _ in range(3):
        response = await async_client.get(f"/{short_code}")
        assert response.status_code == 307
        assert response.headers["location"] == "https://example.com/"

    stats_response = await async_client.get(
        "/api/v1/urls/stats",
        params={"short_code": short_code},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert stats_response.status_code == 200
    stats = stats_response.json()[0]

    assert stats["short_code"] == short_code
    assert stats["original_url"] == "https://example.com/"
    assert stats["clicks_last_hour"] == 3
    assert stats["clicks_last_day"] == 3


@pytest.mark.asyncio
async def test_url_click_limits_stats(async_client, test_user):
    """Test stats for URLs with click limits."""
    create_response = await async_client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.com",
            "expire_minutes": 60,
            "clicks_left": 2,
        },
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    for _ in range(2):
        response = await async_client.get(f"/{short_code}")
        assert response.status_code == 307

    response = await async_client.get(f"/{short_code}")
    assert response.status_code == 410

    stats_response = await async_client.get(
        "/api/v1/urls/stats",
        params={"short_code": short_code},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert stats_response.status_code == 200
    stats = stats_response.json()[0]
    assert stats["clicks_last_hour"] == 2
    assert stats["clicks_last_day"] == 2


@pytest.mark.asyncio
async def test_stats_filtering_and_sorting(async_client, test_user):
    """Test stats filtering and sorting with multiple URLs."""
    urls = [
        ("https://example1.com", "tag1"),
        ("https://example2.com", "tag1"),
        ("https://example3.com", "tag2"),
    ]

    short_codes = []
    for url, tag in urls:
        response = await async_client.post(
            "/api/v1/urls",
            json={"original_url": url, "expire_minutes": 60, "tag": tag},
            headers={"Authorization": f"Bearer {test_user['access_token']}"},
        )
        assert response.status_code == 201
        short_codes.append(response.json()["short_code"])

    for i, code in enumerate(short_codes):
        for _ in range(i + 1):
            response = await async_client.get(f"/{code}")
            assert response.status_code == 307

    stats_response = await async_client.get(
        "/api/v1/urls/stats",
        params={"tag": "tag1"},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert len(stats) == 2
    assert stats[0]["clicks_last_day"] > stats[1]["clicks_last_day"]

    stats_response = await async_client.get(
        "/api/v1/urls/stats",
        params={"page": 1, "page_size": 2},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert stats_response.status_code == 200
    assert len(stats_response.json()) == 2


@pytest.mark.asyncio
async def test_stats_for_expired_urls(async_client, test_user):
    """Test stats for expired URLs."""
    create_response = await async_client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.com",
            "expire_minutes": 1,
        },
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    response = await async_client.get(f"/{short_code}", follow_redirects=True)
    assert response.status_code == 404

    stats_response = await async_client.get(
        "/api/v1/urls/stats",
        params={"short_code": short_code},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert stats_response.status_code == 200
    stats = stats_response.json()[0]
    assert stats["clicks_last_hour"] == 1
    assert stats["clicks_last_day"] == 1


@pytest.mark.asyncio
async def test_stats_for_deactivated_urls(async_client, test_user):
    """Test stats for deactivated URLs."""
    create_response = await async_client.post(
        "/api/v1/urls",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    for _ in range(2):
        response = await async_client.get(f"/{short_code}")
        assert response.status_code == 307

    deactivate_response = await async_client.patch(
        f"/api/v1/urls/{short_code}",
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert deactivate_response.status_code == 200

    response = await async_client.get(f"/{short_code}")
    assert response.status_code == 410

    stats_response = await async_client.get(
        "/api/v1/urls/stats",
        params={"short_code": short_code},
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert stats_response.status_code == 200
    stats = stats_response.json()[0]
    assert stats["clicks_last_hour"] == 2
    assert stats["clicks_last_day"] == 2
