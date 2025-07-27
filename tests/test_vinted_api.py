import pytest

from vinted_api_kit import VintedApi


@pytest.mark.asyncio
async def tes_context_manager_calls_close(vinted_api: VintedApi, mocker):
    mocker.patch.object(vinted_api._client, "close", return_value=pytest.raises(None))

    async with vinted_api:
        pass

    vinted_api._client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_items_calls_service_search_items(
    vinted_api: VintedApi, mocker, sample_catalog_item_data
):
    mock_search = mocker.patch.object(
        vinted_api._items_service, "search_items", return_value=sample_catalog_item_data
    )

    result = await vinted_api.search_items("https://vinted.example.com/catalog")

    mock_search.assert_awaited_once_with(
        "https://vinted.example.com/catalog", 20, 1, None, False, None
    )
    assert result == sample_catalog_item_data


@pytest.mark.asyncio
async def test_get_item_details_calls_service_get(
    vinted_api: VintedApi, mocker, sample_detailed_item_data
):
    mock_get = mocker.patch.object(
        vinted_api._items_service, "get_item_details", return_value=sample_detailed_item_data
    )

    result = await vinted_api.get_item_details("https://vinted.example.com/item/123")

    mock_get.assert_awaited_once_with("https://vinted.example.com/item/123", False)
    assert result == sample_detailed_item_data
