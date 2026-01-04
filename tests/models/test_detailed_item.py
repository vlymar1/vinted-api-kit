from vinted.models.item import DetailedItem


def test_detailed_item_creation(sample_detailed_item_data):
    item = DetailedItem(raw_data=sample_detailed_item_data)

    assert item.id == 456
    assert item.title == "Adidas Sneakers"
    assert item.description == "Great condition"
    assert item.brand_title == "Adidas"
    assert item.brand_slug == "adidas"
    assert item.size_title == "44"
    assert item.currency == "USD"
    assert item.price == 75.0
    assert item.total_item_price == 80.0
    assert item.photo == "https://example.com/photo1.jpg"


def test_detailed_item_extract_price_dict():
    data = {"price": {"amount": "100.5", "currency_code": "GBP"}}
    item = DetailedItem(raw_data=data)
    assert item.price == 100.5
    assert item.currency == "GBP"


def test_detailed_item_extract_price_string():
    data = {"price": "50.25", "currency": "EUR"}
    item = DetailedItem(raw_data=data)
    assert item.price == 50.25
    assert item.currency == "EUR"


def test_detailed_item_size_extraction(sample_detailed_item_data):
    item = DetailedItem(raw_data=sample_detailed_item_data)
    assert item.size_title == "44"


def test_detailed_item_no_size():
    data = {"id": 1, "plugins": []}
    item = DetailedItem(raw_data=data)
    assert item.size_title == ""
