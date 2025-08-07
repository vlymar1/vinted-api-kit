from datetime import datetime, timezone


class DetailedItem:
    """
    Detailed representation of a Vinted item with extended information.

    Attributes
    ----------
    raw_data : dict
        Original raw data dictionary from API.
    id : int
        Unique identifier of the item.
    title : str
        Item title.
    description : str
        Item description text.
    brand_title : str
        Brand name.
    brand_slug : str
        Brand slug (URL-friendly).
    size_title : str
        Size label extracted from item attributes.
    currency : str
        Currency code of the price.
    price : float
        Price amount.
    total_item_price : float
        Total price including fees or adjustments.
    photo : str
        URL of the first photo.
    url : str
        URL to the item on Vinted.
    created_at_ts : datetime
        Creation date/time of the item (UTC).
    raw_timestamp : int
        Raw timestamp from the high resolution photo metadata.
    """

    def __init__(self, data: dict):
        """
        Initialize DetailedItem from raw data dictionary.

        Parameters
        ----------
        data : dict
            Raw response data from Vinted API.
        """
        self.raw_data = data
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description")
        brand_dto = data.get("brand_dto") or {}
        self.brand_title = brand_dto.get("title")
        self.brand_slug = brand_dto.get("slug")
        self.size_title = self._get_size_title(data)
        price_data = data.get("price") or {}
        self.currency = price_data.get("currency_code")
        self.price = price_data.get("amount")
        total_item_price_data = data.get("total_item_price") or {}
        self.total_item_price = total_item_price_data.get("amount")
        self.photo = self._get_first_photo_url(data)
        self.url = data.get("url")
        self.created_at_ts = self._get_created_at_ts(data)
        photos = data.get("photos") or []
        if photos and photos[0] and isinstance(photos[0], dict):
            self.raw_timestamp = (photos[0].get("high_resolution") or {}).get("timestamp")
        else:
            self.raw_timestamp = None

    @staticmethod
    def _get_size_title(data: dict) -> str:
        """
        Extracts the size title from plugins attributes.

        Parameters
        ----------
        data : dict
            Raw item data containing plugins info.

        Returns
        -------
        str
            Size label or empty string if not found.
        """
        for plugin in data.get("plugins", []):
            if plugin.get("name") == "attributes":
                for attr in plugin.get("data", {}).get("attributes", []):
                    if attr.get("code") == "size":
                        val = attr.get("data", {}).get("value", "")
                        return str(val) if val is not None else ""
        return ""

    @staticmethod
    def _get_first_photo_url(data: dict) -> str:
        """
        Retrieves URL of the first photo of the item.

        Parameters
        ----------
        data : dict
            Raw item data.

        Returns
        -------
        str
            URL string or empty if missing.
        """
        photos = data.get("photos", [])
        return photos[0].get("url", "") if photos else ""

    @staticmethod
    def _get_created_at_ts(data: dict) -> datetime:
        """
        Parses the creation timestamp from photo metadata.

        Parameters
        ----------
        data : dict
            Item data containing photos info.

        Returns
        -------
        datetime
            UTC datetime of creation or current time if missing.
        """
        timestamp = data.get("photos", [{}])[0].get("high_resolution", {}).get("timestamp", 0)
        return (
            datetime.fromtimestamp(timestamp, tz=timezone.utc)
            if timestamp
            else datetime.now(tz=timezone.utc)
        )

    def __eq__(self, other):
        """Compare equality by item ID."""
        return self.id == other.id

    def __hash__(self):
        """Hash by item ID."""
        return hash(("id", self.id))
