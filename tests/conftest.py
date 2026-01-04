from unittest.mock import AsyncMock, MagicMock

import pytest
from curl_cffi.requests import Response


@pytest.fixture
def sample_catalog_item_data():
    return {
        "id": 123,
        "title": "Nike Air Max",
        "brand_title": "Nike",
        "size_title": "42",
        "price": {"amount": 50.0, "currency_code": "EUR"},
        "photo": {
            "url": "https://example.com/photo.jpg",
            "high_resolution": {"timestamp": 1734796339},
        },
        "url": "https://vinted.com/items/123-nike-air-max",
    }


@pytest.fixture
def sample_detailed_item_data():
    return {
        "id": 456,
        "title": "Adidas Sneakers",
        "description": "Great condition",
        "brand_dto": {"title": "Adidas", "slug": "adidas"},
        "price": {"amount": 75.0, "currency_code": "USD"},
        "total_item_price": {"amount": 80.0, "currency_code": "USD"},
        "photos": [
            {"url": "https://example.com/photo1.jpg", "high_resolution": {"timestamp": 1734796339}}
        ],
        "url": "https://vinted.com/items/456",
        "plugins": [
            {
                "name": "attributes",
                "data": {"attributes": [{"code": "size", "data": {"value": "44"}}]},
            }
        ],
    }


@pytest.fixture
def mock_async_session():
    session = AsyncMock()
    session.cookies = MagicMock()
    session.cookies.get = MagicMock(return_value=None)
    session.headers = {}
    return session


@pytest.fixture
def mock_http_response():
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.json.return_value = {
        "items": [
            {
                "id": 1,
                "title": "Item 1",
                "price": {"amount": 10, "currency_code": "EUR"},
            }
        ]
    }
    return response


@pytest.fixture
def temp_cookies_dir(tmp_path):
    cookies_dir = tmp_path / "cookies"
    cookies_dir.mkdir()
    return cookies_dir
