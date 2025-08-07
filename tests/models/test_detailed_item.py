from datetime import datetime

from vinted_api_kit.models import DetailedItem


def test_detailed_item_parsing(sample_detailed_item_data):
    data = sample_detailed_item_data

    item = DetailedItem(data)

    assert item.id == 42
    assert item.title == "Test Product"
    assert item.description == "Very rare Vinted item"
    assert item.brand_title == "Nike"
    assert item.brand_slug == "nike"
    assert item.currency == "EUR"
    assert item.price == 19.99
    assert item.total_item_price == 22.49
    assert item.photo == "https://cdn.vinted.net/images.jpg"
    assert item.url == "https://www.vinted.it/items/42-test-product"
    assert item.size_title == "M"
    assert isinstance(item.created_at_ts, datetime)
    assert item.raw_timestamp == 1710000000


def test_detailed_item_missing_optional_fields():
    data = {"id": 100, "title": "Minimal", "description": None}

    item = DetailedItem(data)

    assert item.id == 100


def test_equality_and_hash(sample_detailed_item_data):
    data1 = sample_detailed_item_data
    data2 = sample_detailed_item_data

    item1 = DetailedItem(data1)
    item2 = DetailedItem(data2)

    assert item1 == item2
    assert hash(item1) == hash(item2)
