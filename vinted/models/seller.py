"""Model for a Vinted seller profile."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Seller:
    """Seller profile returned by the Vinted users endpoint.

    The class stores the original `raw_data` (hidden from the repr)
    and extracts commonly-used fields. `last_login` is `None` when the
    profile does not include it.
    """

    raw_data: dict[str, Any] = field(repr=False)
    id: int = field(init=False)
    login: str = field(init=False)
    profile_url: str = field(init=False)
    photo: str = field(init=False)
    country_code: str = field(init=False)
    city: str = field(init=False)
    item_count: int = field(init=False)
    total_items_count: int = field(init=False)
    followers_count: int = field(init=False)
    feedback_count: int = field(init=False)
    feedback_reputation: float = field(init=False)
    positive_feedback_count: int = field(init=False)
    neutral_feedback_count: int = field(init=False)
    negative_feedback_count: int = field(init=False)
    last_login: datetime | None = field(init=False)
    is_on_holiday: bool = field(init=False)
    is_business: bool = field(init=False)

    def __post_init__(self):
        self.id = self.raw_data.get("id", 0)
        self.login = self.raw_data.get("login", "")
        self.profile_url = self.raw_data.get("profile_url", "")

        photo = self.raw_data.get("photo") or {}
        self.photo = photo.get("url", "")

        self.country_code = self.raw_data.get("country_code") or ""
        self.city = self.raw_data.get("city") or ""

        self.item_count = self.raw_data.get("item_count") or 0
        self.total_items_count = self.raw_data.get("total_items_count") or 0
        self.followers_count = self.raw_data.get("followers_count") or 0

        self.feedback_count = self.raw_data.get("feedback_count") or 0
        self.feedback_reputation = float(self.raw_data.get("feedback_reputation") or 0.0)
        self.positive_feedback_count = self.raw_data.get("positive_feedback_count") or 0
        self.neutral_feedback_count = self.raw_data.get("neutral_feedback_count") or 0
        self.negative_feedback_count = self.raw_data.get("negative_feedback_count") or 0

        # Vinted spells the key as `last_loged_on_ts`
        last_login = self.raw_data.get("last_loged_on_ts")
        self.last_login = datetime.fromisoformat(last_login) if last_login else None

        self.is_on_holiday = bool(self.raw_data.get("is_on_holiday"))
        self.is_business = bool(self.raw_data.get("business"))

    def __eq__(self, other):
        if not isinstance(other, Seller):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
