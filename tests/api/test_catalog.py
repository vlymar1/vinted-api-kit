from unittest.mock import AsyncMock, MagicMock

import pytest

from vinted.api.catalog import CatalogAPI
from vinted.models.item import CatalogItem


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.base_url = "https://www.vinted.com"
    session.configure_from_url = MagicMock()
    return session


@pytest.mark.asyncio
async def test_catalog_search_basic(mock_session):
    catalog = CatalogAPI(mock_session)

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "items": [
            {
                "id": 1,
                "title": "Test Item",
                "price": {"amount": 10, "currency_code": "EUR"},
                "photo": {
                    "url": "http://example.com/photo.jpg",
                    "high_resolution": {"timestamp": 1734796339},
                },
                "url": "http://example.com/item/1",
            }
        ]
    }
    mock_session.request = AsyncMock(return_value=mock_response)

    items = await catalog.search(url="https://www.vinted.com/catalog?search_text=test")

    assert len(items) == 1
    assert isinstance(items[0], CatalogItem)
    assert items[0].id == 1


@pytest.mark.asyncio
async def test_catalog_search_raw_data(mock_session):
    catalog = CatalogAPI(mock_session)

    mock_response = MagicMock()
    mock_response.json.return_value = {"items": [{"id": 1, "title": "Test"}]}
    mock_session.request = AsyncMock(return_value=mock_response)

    items = await catalog.search(url="https://www.vinted.com/catalog", raw_data=True)

    assert isinstance(items, list)
    assert isinstance(items[0], dict)


@pytest.mark.asyncio
async def test_catalog_search_with_order(mock_session):
    catalog = CatalogAPI(mock_session)

    mock_response = MagicMock()
    mock_response.json.return_value = {"items": []}

    mock_session.request = AsyncMock(return_value=mock_response)

    await catalog.search(url="https://www.vinted.com/catalog", order="newest_first")

    call_args = mock_session.request.call_args
    assert "order" in call_args.kwargs["params"]


def test_extract_catalog_id_from_path():
    catalog = CatalogAPI(MagicMock())

    catalog_id = catalog._extract_catalog_id("/catalog/123-women-clothes")
    assert catalog_id == 123


def test_extract_catalog_id_no_catalog():
    catalog = CatalogAPI(MagicMock())

    catalog_id = catalog._extract_catalog_id("/search")
    assert catalog_id is None


def test_build_params():
    catalog = CatalogAPI(MagicMock())

    params = catalog._build_params(
        url="https://www.vinted.com/catalog?search_text=nike&brand_ids[]=53", per_page=20, page=1
    )

    assert params["search_text"] == "nike"
    assert params["brand_ids"] == "53"
    assert params["per_page"] == 20
    assert params["page"] == 1
