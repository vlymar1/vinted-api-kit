from unittest.mock import AsyncMock, MagicMock

import pytest

from vinted.api.catalog import CatalogAPI
from vinted.exceptions import VintedValidationError
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
                "photo": {"url": "http://example.com/photo.jpg"},
                "url": "/items/1-test-item",
            }
        ]
    }
    mock_session.request = AsyncMock(return_value=mock_response)

    items = await catalog.search(url="https://www.vinted.com/catalog?search_text=test")

    assert len(items) == 1
    assert isinstance(items[0], CatalogItem)
    assert items[0].id == 1
    assert items[0].url == "https://www.vinted.com/items/1-test-item"
    assert mock_session.request.call_args.args[0] == (
        "https://api.www.vinted.com/svc-catalogue/items"
    )


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "not-a-url",
        "/catalog?search_text=nike",
        "ftp://www.vinted.com/catalog",
        "https://www.vinted.com/items/123-test-item",
        "https://www.vinted.com/api/v2/catalog/items?search_text=nike",
    ],
)
async def test_catalog_search_invalid_url_raises_validation_error(mock_session, url):
    catalog = CatalogAPI(mock_session)

    with pytest.raises(VintedValidationError):
        await catalog.search(url=url)

    mock_session.configure_from_url.assert_not_called()


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
    assert params["attribute_ids[brand]"] == "53"
    assert params["per_page"] == 20
    assert params["page"] == 1


def test_build_params_maps_filters_to_attribute_ids():
    catalog = CatalogAPI(MagicMock())

    params = catalog._build_params(
        url=(
            "https://www.vinted.sk/catalog?catalog[]=5&size_ids[]=206&size_ids[]=207"
            "&brand_ids[]=53&brand_ids[]=7&status_ids[]=6&status_ids[]=1&color_ids[]=1"
            "&patterns_ids[]=119&material_ids[]=122&price_from=5&price_to=550&currency=EUR"
            "&country_ids[]=1&city_ids[]=2&disposal[]=1&order=newest_first"
        ),
        per_page=96,
        page=1,
    )

    assert params == {
        "attribute_ids[catalog]": "5",
        "attribute_ids[size]": "206,207",
        "attribute_ids[brand]": "53,7",
        "attribute_ids[status]": "6,1",
        "attribute_ids[color]": "1",
        "attribute_ids[patterns]": "119",
        "attribute_ids[material]": "122",
        "price_from": "5",
        "price_to": "550",
        "currency": "EUR",
        "order": "newest_first",
        "page": 1,
        "per_page": 96,
    }


def test_build_params_catalog_id_from_path_and_legacy_status():
    catalog = CatalogAPI(MagicMock())

    params = catalog._build_params(
        url="https://www.vinted.de/catalog/1904-women?status[]=2", per_page=20, page=1
    )

    assert params["attribute_ids[catalog]"] == "1904"
    assert params["attribute_ids[status]"] == "2"


@pytest.mark.parametrize(
    ("base_url", "expected"),
    [
        ("https://www.vinted.sk", "https://api.vinted.sk"),
        ("https://www.vinted.co.uk", "https://api.vinted.co.uk"),
        ("https://www.vinted.com", "https://api.www.vinted.com"),
    ],
)
def test_api_gateway_url(mock_session, base_url, expected):
    mock_session.base_url = base_url
    catalog = CatalogAPI(mock_session)

    assert catalog._api_gateway_url() == expected
