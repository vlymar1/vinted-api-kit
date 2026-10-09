from unittest.mock import AsyncMock, MagicMock

import pytest

from vinted.api.items import ItemsAPI
from vinted.exceptions import VintedDeprecatedError, VintedValidationError


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.base_url = "https://www.vinted.com"
    session.configure_from_url = MagicMock()
    return session


@pytest.mark.asyncio
@pytest.mark.parametrize("raw_data", [False, True])
async def test_items_get_details_raises_deprecated_error(mock_session, raw_data):
    items_api = ItemsAPI(mock_session)
    mock_session.request = AsyncMock()

    with pytest.raises(VintedDeprecatedError):
        await items_api.get_details(
            url="https://www.vinted.com/items/123-test-item", raw_data=raw_data
        )

    mock_session.request.assert_not_called()


def test_extract_product_id():
    items_api = ItemsAPI(MagicMock())

    product_id = items_api._extract_product_id("https://www.vinted.com/items/123-nike-shoes")

    assert product_id == "123"


def test_extract_product_id_complex():
    items_api = ItemsAPI(MagicMock())

    product_id = items_api._extract_product_id(
        "https://www.vinted.fr/items/9876-adidas-sneakers-size-42"
    )

    assert product_id == "9876"


@pytest.mark.parametrize(
    "url",
    [
        "not-a-url",
        "https://www.vinted.com/catalog/123",
        "https://www.vinted.com/items/",
        "https://www.vinted.com/items/not-numeric",
        "/items/123-test-item",
    ],
)
def test_extract_product_id_invalid_url_raises_validation_error(url):
    items_api = ItemsAPI(MagicMock())

    with pytest.raises(VintedValidationError):
        items_api._extract_product_id(url)
