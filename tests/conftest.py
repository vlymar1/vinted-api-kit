from pathlib import Path
from typing import Any, Callable, Generator

import pytest

from vinted_api_kit import VintedApi
from vinted_api_kit.client.vinted_http_client import VintedHttpClient
from vinted_api_kit.services.item_service import ItemService


@pytest.fixture
def vinted_http_client(tmp_path: Path) -> Generator[VintedHttpClient, Any, None]:
    client = VintedHttpClient(
        locale="fr",
        proxies={"http": "http://127.0.0.1:8888"},
        client_ip="123.123.123.123",
        cookies_dir=tmp_path,
        persist_cookies=False,
    )
    yield client
    import asyncio

    asyncio.run(client.close())


@pytest.fixture
def item_service(vinted_http_client: VintedHttpClient):
    return ItemService(client=vinted_http_client)


@pytest.fixture
async def vinted_api():
    async with VintedApi() as api:
        yield api


@pytest.fixture
def sample_catalog_item_data() -> Callable[[int], dict[str, Any]]:
    def factory(ts: int = 1710000000) -> dict[str, Any]:
        return {
            "id": 77,
            "title": "Vintage Jeans",
            "brand_title": "Levis",
            "size_title": "32",
            "price": {"currency_code": "EUR", "amount": 45},
            "photo": {
                "url": "https://cdn.vinted.net/catalog.jpg",
                "high_resolution": {"timestamp": ts},
            },
            "photos": [{"high_resolution": {"timestamp": ts}}],
            "url": "https://www.vinted.it/items/77-vintage-jeans",
        }

    return factory


@pytest.fixture
def sample_detailed_item_data() -> dict[str, Any]:
    return {
        "id": 42,
        "title": "Test Product",
        "description": "Very rare Vinted item",
        "brand_dto": {"title": "Nike", "slug": "nike"},
        "price": {"currency_code": "EUR", "amount": 19.99},
        "total_item_price": {"amount": 22.49},
        "photos": [
            {
                "url": "https://cdn.vinted.net/images.jpg",
                "high_resolution": {"timestamp": 1710000000},
            }
        ],
        "url": "https://www.vinted.it/items/42-test-product",
        "plugins": [
            {
                "name": "attributes",
                "data": {"attributes": [{"code": "size", "data": {"value": "M"}}]},
            }
        ],
    }
