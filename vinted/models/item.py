"""Models for parsed Vinted API responses.

This module exposes lightweight dataclasses that wrap raw API JSON
for easier consumption by callers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class CatalogItem:
    """Lightweight representation of an item returned in catalog listings.

    The class stores the original `raw_data` (hidden from the repr)
    and extracts commonly-used fields like `id`, `title`, `price` and
    `photo` for convenience.
    """

    raw_data: dict[str, Any] = field(repr=False)
    id: int = field(init=False)
    title: str = field(init=False)
    brand_title: str = field(init=False)
    size_title: str = field(init=False)
    currency: str = field(init=False)
    price: float = field(init=False)
    photo: str = field(init=False)
    url: str = field(init=False)
    created_at_ts: datetime = field(init=False)
    raw_timestamp: int = field(init=False)

    def __post_init__(self):
        self.id = self.raw_data.get("id", 0)
        self.title = self.raw_data.get("title", "")
        self.brand_title = self.raw_data.get("brand_title", "")
        self.size_title = self.raw_data.get("size_title", "")

        price = self.raw_data.get("price") or {}
        self.currency = price.get("currency_code", "")
        self.price = price.get("amount", 0.0)

        photo = self.raw_data.get("photo") or {}
        self.photo = photo.get("url", "")
        self.url = self.raw_data.get("url", "")
        self.created_at_ts = self._parse_created_at(self.raw_data)

        high_res = photo.get("high_resolution") or {}
        self.raw_timestamp = high_res.get("timestamp", 0)

    @staticmethod
    def _parse_created_at(data: dict) -> datetime:
        """Parse created timestamp from item `photo.high_resolution`.

        Returns a timezone-aware `datetime`. If timestamp is missing,
        returns epoch (1970-01-01 UTC).
        """
        photo = data.get("photo") or {}
        high_res = photo.get("high_resolution") or {}
        timestamp = high_res.get("timestamp", 0)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def __eq__(self, other):
        if not isinstance(other, CatalogItem):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def is_new_item(self, minutes: int = 1) -> bool:
        """Return True when the item was created within `minutes`.

        Args:
            minutes: Age threshold in minutes (default: 1).
        """
        delta = datetime.now(timezone.utc) - self.created_at_ts
        return delta.total_seconds() < minutes * 60


@dataclass
class DetailedItem:
    """Detailed representation of a single item.

    Extracts price, size, photos and other metadata from the raw API
    payload to present a stable, typed object to callers.
    """

    raw_data: dict = field(repr=False)
    id: int = field(init=False)
    title: str = field(init=False)
    description: str = field(init=False)
    brand_title: str = field(init=False)
    brand_slug: str = field(init=False)
    size_title: str = field(init=False)
    currency: str = field(init=False)
    price: float = field(init=False)
    total_item_price: float = field(init=False)
    photo: str = field(init=False)
    url: str = field(init=False)
    created_at_ts: datetime = field(init=False)
    raw_timestamp: int | None = field(init=False)

    def __post_init__(self):
        self.id = self.raw_data.get("id", 0)
        self.title = self.raw_data.get("title", "")
        self.description = self.raw_data.get("description", "")

        brand_dto = self.raw_data.get("brand_dto") or {}
        self.brand_title = brand_dto.get("title", "")
        self.brand_slug = brand_dto.get("slug", "")
        self.size_title = self._get_size_title(self.raw_data)

        self.currency, self.price = self._extract_price_data(self.raw_data)
        self.total_item_price = self._extract_total_price(self.raw_data)

        self.photo = self._get_first_photo_url(self.raw_data)
        self.url = self.raw_data.get("url", "")
        self.created_at_ts = self._get_created_at_ts(self.raw_data)

        photos = self.raw_data.get("photos") or []
        if photos and photos[0] and isinstance(photos[0], dict):
            self.raw_timestamp = (photos[0].get("high_resolution") or {}).get("timestamp")
        else:
            self.raw_timestamp = None

    @staticmethod
    def _extract_price_data(data: dict) -> tuple[str, float]:
        """Extract currency and price as (currency, float).

        Handles different shapes: dict or string and falls back to 0.0
        on parse errors.
        """
        price_data = data.get("price")
        currency = data.get("currency", "")

        if isinstance(price_data, dict):
            currency = price_data.get("currency_code", currency)
            price_amount = price_data.get("amount", "0")
        elif isinstance(price_data, str):
            price_amount = price_data
        else:
            price_amount = "0"

        try:
            price_float = float(price_amount)
        except (ValueError, TypeError):
            price_float = 0.0

        return currency, price_float

    @staticmethod
    def _extract_total_price(data: dict) -> float:
        """Extract total_item_price as float, tolerant to formats."""
        total_price_data = data.get("total_item_price")

        if isinstance(total_price_data, dict):
            price_amount = total_price_data.get("amount", "0")
        elif isinstance(total_price_data, str):
            price_amount = total_price_data
        else:
            price_amount = "0"

        try:
            return float(price_amount)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def _get_size_title(data: dict) -> str:
        """Extract the size attribute from plugin data if present."""
        for plugin in data.get("plugins", []):
            if plugin.get("name") == "attributes":
                for attr in plugin.get("data", {}).get("attributes", []):
                    if attr.get("code") == "size":
                        val = attr.get("data", {}).get("value", "")
                        return str(val) if val is not None else ""
        return ""

    @staticmethod
    def _get_first_photo_url(data: dict) -> str:
        """Return the URL of the first photo if available."""
        photos = data.get("photos", [])
        return photos[0].get("url", "") if photos else ""

    @staticmethod
    def _get_created_at_ts(data: dict) -> datetime:
        """Return a timezone-aware creation datetime from photos metadata.

        Falls back to now() when timestamp is missing.
        """
        timestamp = data.get("photos", [{}])[0].get("high_resolution", {}).get("timestamp", 0)
        return (
            datetime.fromtimestamp(timestamp, tz=timezone.utc)
            if timestamp
            else datetime.now(tz=timezone.utc)
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DetailedItem):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
