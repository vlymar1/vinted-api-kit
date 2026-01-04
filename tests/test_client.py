from unittest.mock import patch

import pytest

from vinted import VintedClient
from vinted.models.item import CatalogItem


@pytest.mark.asyncio
async def test_client_initialization(temp_cookies_dir):
    client = VintedClient(
        cookies_dir=temp_cookies_dir, persist_cookies=True, storage_format="json"
    )

    assert client._session is not None
    assert client._catalog is not None
    assert client._items is not None


@pytest.mark.asyncio
async def test_client_search_items(mock_http_response):
    with patch("vinted.session.HttpSession.request", return_value=mock_http_response):
        async with VintedClient() as client:
            items = await client.search_items(url="https://vinted.com/catalog?search_text=nike")

            assert isinstance(items, list)
            assert len(items) > 0
            assert isinstance(items[0], CatalogItem)


@pytest.mark.asyncio
async def test_client_context_manager():
    async with VintedClient() as client:
        assert client._session is not None


@pytest.mark.asyncio
async def test_client_proxy_configuration():
    client = VintedClient(proxy="user:pass@proxy.com:8080")
    assert client._session.proxy == "user:pass@proxy.com:8080"
