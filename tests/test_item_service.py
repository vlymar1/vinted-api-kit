from unittest.mock import AsyncMock, MagicMock

import pytest

from vinted_api_kit.models import CatalogItem, DetailedItem
from vinted_api_kit.services.item_service import ItemService


@pytest.mark.asyncio
async def test_search_items_returns_catalog_items(mocker, item_service: ItemService):
    raw_response = {
        "items": [
            {
                "id": 1,
                "title": "Test item",
                "brand_title": "Brand",
                "size_title": "L",
                "price": {"currency_code": "EUR", "amount": 10},
                "photo": {"url": "http://image.url", "high_resolution": {"timestamp": 123}},
                "photos": [{"high_resolution": {"timestamp": 123}}],
                "url": "http://example.com/item/1",
            }
        ]
    }
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=raw_response)
    mocker.patch.object(item_service.client, "request", return_value=mock_response)

    result = await item_service.search_items("https://www.vinted.fr/catalog/1")

    assert isinstance(result, list)
    assert len(result) > 0
    first = result[0]
    assert isinstance(first, CatalogItem)
    assert first.id == 1


@pytest.mark.asyncio
async def test_item_details_returns_detailed_item(mocker, item_service: ItemService):
    raw_response = {
        "item": {
            "id": 1,
            "title": "Test detailed item",
            "description": "Description",
            "brand_dto": {"title": "Brand", "slug": "brand-slug"},
            "price": {"currency_code": "EUR", "amount": 10},
            "total_item_price": {"amount": 12},
            "photos": [{"url": "http://image.url", "high_resolution": {"timestamp": 123}}],
            "url": "http://www.vinted.fr/item/1",
            "plugins": [
                {
                    "name": "attributes",
                    "data": {"attributes": [{"code": "size", "data": {"value": "L"}}]},
                }
            ],
        }
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=raw_response)
    mocker.patch.object(item_service.client, "request", return_value=mock_response)

    result = await item_service.item_details("https://www.vinted.fr/item/1")

    assert isinstance(result, DetailedItem)
    assert result.id == 1
    assert result.brand_title == "Brand"


@pytest.mark.asyncio
async def test_no_valid_order(item_service: ItemService):
    with pytest.raises(ValueError) as exc_info:
        await item_service.search_items("https://www.vinted.fr/catalog/1", order="no_valid")

    assert "Invalid order" in str(exc_info.value)
