"""Public client entrypoint.

`VintedClient` provides a small, high-level interface to the library's
catalog and item lookup functionality. It wires together a session,
cookie storage and API wrappers.
"""

import logging
from pathlib import Path
from typing import Type, Union

from .api.catalog import CatalogAPI
from .api.items import ItemsAPI
from .constants import SortOrder, StorageFormat
from .models.config import ClientConfig
from .models.item import CatalogItem, DetailedItem
from .session import HttpSession
from .storage.base import CookieStorage
from .storage.json import JsonStorage
from .storage.mozilla import MozillaStorage
from .storage.pickle import PickleStorage
from .utils import format_proxy_for_log

logger = logging.getLogger(__name__)


class VintedClient:
    """High-level client for Vinted operations.

    The client is an async context manager that exposes `search_items`
    and `item_details`. Cookie persistence is configurable via
    `persist_cookies` and `storage_format`.
    """

    def __init__(
        self,
        proxy: str | None = None,
        cookies_dir: Path | None = None,
        persist_cookies: bool = False,
        storage_format: StorageFormat = "json",
    ):
        """Create a `VintedClient`.

        Args:
            proxy: Optional proxy URL used by the underlying session.
            cookies_dir: Directory where cookie files will be stored.
            persist_cookies: When True, cookies are saved/loaded from disk.
            storage_format: One of `"json"`, `"pickle"` or `"mozilla"`.
        """
        config = ClientConfig(
            proxy=proxy,
            cookies_dir=cookies_dir or Path("."),
            persist_cookies=persist_cookies,
            storage_format=storage_format,
        )

        logger.info("Initializing VintedClient: proxy=%s", format_proxy_for_log(config.proxy))

        storage = self._create_storage(config)

        self._session = HttpSession(
            proxy=config.proxy,
            storage=storage,
        )

        self._catalog = CatalogAPI(self._session)
        self._items = ItemsAPI(self._session)

    def _create_storage(self, config: ClientConfig) -> CookieStorage | None:
        """Return a configured `CookieStorage` instance or None.

        When `persist_cookies` is False this returns None.
        """
        if not config.persist_cookies:
            return None

        filepath = self._generate_storage_path(config)

        storage_map: dict[str, Type[CookieStorage]] = {
            "pickle": PickleStorage,
            "json": JsonStorage,
            "mozilla": MozillaStorage,
        }

        storage_class = storage_map[config.storage_format]
        return storage_class(filepath)

    def _generate_storage_path(self, config: ClientConfig) -> Path:
        """Generate a filename for persisted cookies.

        Filenames include proxy host/port when a proxy is configured to avoid
        collisions between different proxy sessions.
        """
        filename = "cookies"

        if config.proxy:
            if "@" in config.proxy:
                ip_port = config.proxy.split("@")[-1]
            else:
                ip_port = config.proxy
            parts = ip_port.split(":")
            if len(parts) >= 2:
                ip = parts[0]
                port = parts[1]
                filename = f"cookies_{ip}_{port}"

        extensions = {
            "pickle": ".pk",
            "json": ".json",
            "mozilla": ".txt",
        }

        filename += extensions[config.storage_format]

        return config.cookies_dir / filename

    async def search_items(
        self,
        url: str,
        per_page: int = 20,
        page: int = 1,
        timestamp: int | None = None,
        order: SortOrder | None = None,
        raw_data: bool = False,
    ) -> Union[list[CatalogItem], list[dict]]:
        """Search the catalog and return parsed items or raw response.

        Args:
            url: Catalog URL or search endpoint.
            per_page: Number of items per page.
            page: Page index.
            timestamp: Optional timestamp used by the API.
            order: Sort order string.
            raw_data: When True returns raw dicts instead of model objects.

        Returns:
            A list of `CatalogItem` instances or raw dicts when `raw_data`.
        """
        return await self._catalog.search(
            url=url,
            per_page=per_page,
            page=page,
            timestamp=timestamp,
            order=order,
            raw_data=raw_data,
        )

    async def item_details(
        self,
        url: str,
        raw_data: bool = False,
    ) -> Union[DetailedItem, dict]:
        """Fetch item details by URL.

        Args:
            url: Item page URL or API endpoint.
            raw_data: When True returns raw dict instead of `DetailedItem`.

        Returns:
            `DetailedItem` or raw dict when `raw_data` is True.
        """
        return await self._items.get_details(url=url, raw_data=raw_data)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(
                "Exception in context: %s: %s",
                exc_type.__name__,
                exc_val,
                exc_info=(exc_type, exc_val, exc_tb),
            )
        await self._session.close()
        return False

    async def close(self):
        """Close the underlying session and release resources."""
        await self._session.close()
