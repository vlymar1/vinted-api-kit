from datetime import datetime, timedelta, timezone
from typing import Callable

import pytest

from vinted_api_kit.models import CatalogItem


def test_basic_catalog_item_parsing(sample_catalog_item_data: Callable[[int], dict]):
    data = sample_catalog_item_data(1710000000)

    item = CatalogItem(data)

    assert item.id == 77
    assert item.title == "Vintage Jeans"
    assert item.brand_title == "Levis"
    assert item.size_title == "32"
    assert item.currency == "EUR"
    assert item.price == 45
    assert item.photo == "https://cdn.vinted.net/catalog.jpg"
    assert item.url.startswith("https://www.vinted.it/items/")
    assert isinstance(item.created_at_ts, datetime)
    assert item.raw_timestamp == 1710000000


@pytest.mark.parametrize(
    "delta_seconds, expected",
    [
        (30, True),
        (120 * 60, False),
    ],
)
def test_is_new_item_parametrized(
    sample_catalog_item_data: Callable[[int], dict], delta_seconds: int, expected: bool
):
    ts = int((datetime.now(timezone.utc) - timedelta(seconds=delta_seconds)).timestamp())
    data = sample_catalog_item_data(ts)

    item = CatalogItem(data)

    assert item.is_new_item(minutes=1) is expected


def test_equality_and_hash(sample_catalog_item_data: Callable[[int], dict]):
    data1 = sample_catalog_item_data(1710000000)
    data2 = sample_catalog_item_data(1710000000)

    item1 = CatalogItem(data1)
    item2 = CatalogItem(data2)

    assert item1 == item2
    assert hash(item1) == hash(item2)


def test_missing_fields_dont_crash():
    data = {"id": 15, "title": "stub", "brand_title": None, "size_title": None, "url": None}

    item = CatalogItem(data)

    assert item.price is None
    assert item.currency is None
    assert item.photo is None
    assert item.raw_timestamp is None
