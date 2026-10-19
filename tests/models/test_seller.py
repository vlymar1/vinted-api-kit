from datetime import datetime, timedelta, timezone

from vinted.models.seller import Seller


def test_seller_creation():
    seller = Seller(
        raw_data={
            "id": 123,
            "login": "seller",
            "profile_url": "https://www.vinted.sk/member/123-seller",
            "photo": {"url": "https://example.com/avatar.jpg"},
            "country_code": "PL",
            "city": "Warszawa",
            "item_count": 5,
            "total_items_count": 40,
            "followers_count": 7,
            "feedback_count": 30,
            "feedback_reputation": 0.98,
            "positive_feedback_count": 28,
            "neutral_feedback_count": 1,
            "negative_feedback_count": 1,
            "last_loged_on_ts": "2026-10-19T12:45:03+02:00",
            "is_on_holiday": True,
            "business": False,
        }
    )

    assert seller.id == 123
    assert seller.login == "seller"
    assert seller.profile_url == "https://www.vinted.sk/member/123-seller"
    assert seller.photo == "https://example.com/avatar.jpg"
    assert seller.country_code == "PL"
    assert seller.city == "Warszawa"
    assert seller.item_count == 5
    assert seller.total_items_count == 40
    assert seller.followers_count == 7
    assert seller.feedback_count == 30
    assert seller.feedback_reputation == 0.98
    assert seller.positive_feedback_count == 28
    assert seller.neutral_feedback_count == 1
    assert seller.negative_feedback_count == 1
    assert seller.last_login == datetime(
        2026, 10, 19, 12, 45, 3, tzinfo=timezone(timedelta(hours=2))
    )
    assert seller.is_on_holiday is True
    assert seller.is_business is False


def test_seller_missing_fields():
    seller = Seller(raw_data={"id": 123, "photo": None, "city": None})

    assert seller.login == ""
    assert seller.photo == ""
    assert seller.city == ""
    assert seller.item_count == 0
    assert seller.feedback_reputation == 0.0
    assert seller.last_login is None
    assert seller.is_on_holiday is False


def test_seller_equality_and_hash():
    seller1 = Seller(raw_data={"id": 123})
    seller2 = Seller(raw_data={"id": 123, "login": "seller"})
    seller3 = Seller(raw_data={"id": 999})

    assert seller1 == seller2
    assert seller1 != seller3
    assert len({seller1, seller2, seller3}) == 2
