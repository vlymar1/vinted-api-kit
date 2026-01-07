from datetime import datetime, timezone

import pytest

from vinted.models.item import CatalogItem


def test_catalog_item_creation(sample_catalog_item_data):
    item = CatalogItem(raw_data=sample_catalog_item_data)

    assert item.id == 123
    assert item.title == "Nike Air Max"
    assert item.brand_title == "Nike"
    assert item.size_title == "42"
    assert item.currency == "EUR"
    assert item.price == 50.0
    assert item.photo == "https://example.com/photo.jpg"
    assert item.url == "https://vinted.com/items/123-nike-air-max"
    assert isinstance(item.created_at_ts, datetime)
    assert item.raw_timestamp == 1734796339


def test_catalog_item_equality(sample_catalog_item_data):
    item1 = CatalogItem(raw_data=sample_catalog_item_data)
    item2 = CatalogItem(raw_data=sample_catalog_item_data)
    item3 = CatalogItem(raw_data={**sample_catalog_item_data, "id": 999})

    assert item1 == item2
    assert item1 != item3


def test_catalog_item_hash(sample_catalog_item_data):
    item1 = CatalogItem(raw_data=sample_catalog_item_data)
    item2 = CatalogItem(raw_data=sample_catalog_item_data)

    assert hash(item1) == hash(item2)
    assert len({item1, item2}) == 1


def test_catalog_item_is_new(sample_catalog_item_data):
    data = {**sample_catalog_item_data}
    data["photo"]["high_resolution"]["timestamp"] = int(datetime.now(timezone.utc).timestamp())

    item = CatalogItem(raw_data=data)
    assert item.is_new_item(minutes=1) is True


@pytest.mark.parametrize("missing_field", ["price", "photo", "url"])
def test_catalog_item_with_missing_fields(sample_catalog_item_data, missing_field):
    data = {**sample_catalog_item_data}
    del data[missing_field]

    item = CatalogItem(raw_data=data)
    assert item.id == 123
