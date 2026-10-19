from unittest.mock import AsyncMock, MagicMock

import pytest

from vinted.api.seller import SellerAPI
from vinted.exceptions import VintedValidationError
from vinted.models.item import CatalogItem
from vinted.models.seller import Seller


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.base_url = "https://www.vinted.sk"
    session.configure_from_url = MagicMock()
    return session


def json_response(data):
    response = MagicMock()
    response.json.return_value = data
    return response


@pytest.mark.asyncio
async def test_seller_get_info(mock_session):
    seller_api = SellerAPI(mock_session)
    mock_session.request = AsyncMock(
        return_value=json_response({"user": {"id": 123, "login": "seller"}})
    )

    seller = await seller_api.get_info(url="https://www.vinted.sk/member/123-seller")

    assert isinstance(seller, Seller)
    assert seller.id == 123
    assert seller.login == "seller"
    assert mock_session.request.call_args.args[0] == "https://www.vinted.sk/api/v2/users/123"
    mock_session.configure_from_url.assert_called_once_with(
        "https://www.vinted.sk/member/123-seller"
    )


@pytest.mark.asyncio
async def test_seller_get_info_raw_data(mock_session):
    seller_api = SellerAPI(mock_session)
    mock_session.request = AsyncMock(return_value=json_response({"user": {"id": 123}}))

    seller = await seller_api.get_info(url="https://www.vinted.sk/member/123", raw_data=True)

    assert seller == {"id": 123}


@pytest.mark.asyncio
async def test_seller_get_items(mock_session):
    seller_api = SellerAPI(mock_session)
    mock_session.request = AsyncMock(
        return_value=json_response(
            {"items": [{"id": 1, "title": "Item", "url": "https://www.vinted.sk/items/1"}]}
        )
    )

    items = await seller_api.get_items(
        url="https://www.vinted.sk/member/123-seller",
        per_page=96,
        page=2,
        order="price_low_to_high",
    )

    assert len(items) == 1
    assert isinstance(items[0], CatalogItem)
    assert items[0].url == "https://www.vinted.sk/items/1"
    call_args = mock_session.request.call_args
    assert call_args.args[0] == "https://www.vinted.sk/api/v2/wardrobe/123/items"
    assert call_args.kwargs["params"] == {"page": 2, "per_page": 96, "order": "price_low_to_high"}


@pytest.mark.asyncio
async def test_seller_get_items_raw_data(mock_session):
    seller_api = SellerAPI(mock_session)
    mock_session.request = AsyncMock(return_value=json_response({"items": [{"id": 1}]}))

    items = await seller_api.get_items(url="https://www.vinted.sk/member/123", raw_data=True)

    assert items == [{"id": 1}]
    assert "order" not in mock_session.request.call_args.kwargs["params"]


@pytest.mark.parametrize(
    "url",
    [
        "https://www.vinted.sk/member/123",
        "https://www.vinted.sk/member/123/",
        "https://www.vinted.sk/member/123-seller",
        "https://www.vinted.sk/member/123-seller?tab=feedback",
        "https://vinted.sk/member/123",
    ],
)
def test_extract_seller_id(url):
    assert SellerAPI._extract_seller_id(url) == "123"


@pytest.mark.parametrize(
    "url",
    [
        "not-a-url",
        "https://www.vinted.sk",
        "https://www.vinted.sk/catalog",
        "https://www.vinted.sk/member/seller",
        "https://www.vinted.sk/member/general/followers/123",
    ],
)
def test_extract_seller_id_invalid_url(url):
    with pytest.raises(VintedValidationError):
        SellerAPI._extract_seller_id(url)
