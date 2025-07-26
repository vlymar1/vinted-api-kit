from datetime import datetime, timezone


class CatalogItem:
    """
    Catalog item representation used in search results.

    Attributes
    ----------
    raw_data : dict
        Raw data dictionary from the API.
    id : int
        Unique item ID.
    title : str
        Item title.
    brand_title : str
        Brand name.
    size_title : str
        Size label.
    currency : str
        Currency code.
    price : float
        Item price amount.
    photo : str
        URL of the main photo.
    url : str
        Item URL on Vinted.
    created_at_ts : datetime
        Item creation datetime (UTC).
    raw_timestamp : int
        Raw timestamp from photo metadata.
    """

    def __init__(self, data):
        """
        Initialize CatalogItem from API data.

        Parameters
        ----------
        data : dict
            Raw catalog item data.
        """
        self.raw_data = data
        self.id = data.get('id')
        self.title = data.get('title')
        self.brand_title = data.get('brand_title')
        self.size_title = data.get('size_title')
        self.currency = data.get('price').get('currency_code')
        self.price = data.get('price').get('amount')
        self.photo = data.get('photo').get('url')
        self.url = data.get('url')
        self.created_at_ts = self._get_created_at_ts(data)
        self.raw_timestamp = data.get('photo').get('high_resolution').get('timestamp')

    @staticmethod
    def _get_created_at_ts(data: dict) -> datetime:
        """
        Parse creation timestamp from photo metadata.

        Parameters
        ----------
        data : dict
            Item data with photo details.

        Returns
        -------
        datetime
            UTC creation datetime or current time if unavailable.
        """
        timestamp = data.get('photos', {}).get('high_resolution', {}).get('timestamp', 0)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else datetime.now(tz=timezone.utc)

    def __eq__(self, other):
        """Items are equal if IDs match."""
        return self.id == other.id

    def __hash__(self):
        """Hash based on unique ID."""
        return hash(('id', self.id))

    def is_new_item(self, minutes=1):
        """
        Determine if the item is new within a time threshold.

        Parameters
        ----------
        minutes : int
            Time window in minutes to consider item as new.

        Returns
        -------
        bool
            True if item created within `minutes` from now.
        """
        delta = datetime.now(timezone.utc) - self.created_at_ts
        return delta.total_seconds() < minutes * 60
