from datetime import datetime, timedelta, timezone

import pytest

from models.click_stats import ClickStat


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
    assert create_response.status_code == 200
    short_code = create_response.json()["short_code"]

    for _ in range(3):
        response = await async_client.get(f"/{short_code}")
        assert response.status_code == 307  # Temporary redirect
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
async def test_url_click_limits(async_client, test_user):
    # Create a short URL with click limit
    create_response = await async_client.post(
        "/api/v1/urls",
        json={
            "original_url": "https://example.com",
            "expire_minutes": 60,
            "clicks_left": 2,
        },
        headers={"Authorization": f"Bearer {test_user['access_token']}"},
    )
    assert create_response.status_code == 200
    short_code = create_response.json()["short_code"]

    response = await async_client.get(f"/{short_code}")
    assert response.status_code == 307


@pytest.mark.asyncio
async def test_stats_filtering_and_sorting(async_client, test_user):
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
        assert response.status_code == 200
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
