from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vinted.constants import (
    HTTP_STATUS_FORBIDDEN,
    HTTP_STATUS_RATE_LIMIT,
    HTTP_STATUS_UNAUTHORIZED,
)
from vinted.exceptions import (
    VintedAuthError,
    VintedConfigError,
    VintedNetworkError,
    VintedRateLimitError,
)
from vinted.session import HttpSession


@pytest.fixture
def mock_storage():
    storage = MagicMock()
    storage.load = MagicMock()
    storage.save = MagicMock()
    storage.clear = MagicMock()
    return storage


@pytest.mark.asyncio
async def test_session_init():
    session = HttpSession()
    assert session.proxy is None
    assert session.storage is None
    assert session.base_url is None


@pytest.mark.asyncio
async def test_session_init_with_proxy():
    session = HttpSession(proxy="proxy:8080")
    assert session.proxy == "proxy:8080"
    assert session.session.proxies == {"http": "http://proxy:8080", "https": "http://proxy:8080"}


@pytest.mark.parametrize(
    "url,expected_base_url,expected_locale,expected_accept_language",
    [
        (
            "https://www.vinted.fr/catalog",
            "https://www.vinted.fr",
            "fr",
            "fr-FR,fr;q=0.9",
        ),
        (
            "https://vinted.com/catalog",
            "https://vinted.com",
            "com",
            "en-US,en;q=0.9",
        ),
        (
            "https://www.vinted.co.uk/catalog",
            "https://www.vinted.co.uk",
            "co.uk",
            "en-GB,en;q=0.9",
        ),
    ],
)
def test_configure_from_url(url, expected_base_url, expected_locale, expected_accept_language):
    session = HttpSession()
    session.configure_from_url(url)

    assert session.base_url == expected_base_url
    assert session.locale == expected_locale
    assert session.session.headers["Accept-Language"] == expected_accept_language
    assert session.session.headers["Referer"] == expected_base_url


@pytest.mark.asyncio
async def test_refresh_cookies_no_base_url():
    session = HttpSession()

    with pytest.raises(VintedConfigError, match="base_url not configured"):
        await session.refresh_cookies()


@pytest.mark.asyncio
async def test_refresh_cookies_success(mock_storage):
    session = HttpSession(storage=mock_storage)
    session.base_url = "https://www.vinted.com"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch.object(session.session, "head", new=AsyncMock(return_value=mock_response)):
        await session.refresh_cookies()

    mock_storage.save.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_cookies_save_error_raises_config_error(mock_storage):
    session = HttpSession(storage=mock_storage)
    session.base_url = "https://www.vinted.com"
    mock_storage.save.side_effect = OSError("read-only filesystem")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch.object(session.session, "head", new=AsyncMock(return_value=mock_response)):
        with pytest.raises(VintedConfigError, match="Failed to save cookies"):
            await session.refresh_cookies()


@pytest.mark.asyncio
async def test_refresh_cookies_network_error(mock_storage):
    session = HttpSession(storage=mock_storage)
    session.base_url = "https://www.vinted.com"

    with patch.object(
        session.session, "head", new=AsyncMock(side_effect=Exception("Network error"))
    ):
        with pytest.raises(VintedNetworkError):
            await session.refresh_cookies()


@pytest.mark.asyncio
async def test_request_with_401_retry(mock_storage):
    session = HttpSession(storage=mock_storage)
    session.base_url = "https://www.vinted.com"
    session.locale = "com"

    mock_response_401 = MagicMock()
    mock_response_401.status_code = HTTP_STATUS_UNAUTHORIZED

    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.json.return_value = {"items": []}

    mock_head_response = MagicMock()
    mock_head_response.status_code = 200
    mock_head_response.raise_for_status = MagicMock()

    with patch.object(
        session.session, "get", new=AsyncMock(side_effect=[mock_response_401, mock_response_200])
    ):
        with patch.object(session.session, "head", new=AsyncMock(return_value=mock_head_response)):
            response = await session.request("https://api.vinted.com/test")

            assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_with_429_raises_rate_limit_error(mock_storage):
    session = HttpSession(storage=mock_storage)
    session.base_url = "https://www.vinted.com"
    session.locale = "com"

    mock_response_429 = MagicMock()
    mock_response_429.status_code = HTTP_STATUS_RATE_LIMIT
    mock_response_429.reason = "Too Many Requests"

    mock_head_response = MagicMock()
    mock_head_response.status_code = 200
    mock_head_response.raise_for_status = MagicMock()

    with patch.object(session.session, "get", new=AsyncMock(return_value=mock_response_429)):
        with patch.object(session.session, "head", new=AsyncMock(return_value=mock_head_response)):
            with pytest.raises(VintedRateLimitError) as exc_info:
                await session.request("https://api.vinted.com/test")

    assert exc_info.value.status_code == HTTP_STATUS_RATE_LIMIT
    assert exc_info.value.response is mock_response_429


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [HTTP_STATUS_UNAUTHORIZED, HTTP_STATUS_FORBIDDEN])
async def test_request_with_auth_failure_after_retry_raises_auth_error(mock_storage, status_code):
    session = HttpSession(storage=mock_storage)
    session.base_url = "https://www.vinted.com"
    session.locale = "com"

    mock_response_auth = MagicMock()
    mock_response_auth.status_code = status_code
    mock_response_auth.reason = "Auth failed"

    mock_head_response = MagicMock()
    mock_head_response.status_code = 200
    mock_head_response.raise_for_status = MagicMock()

    with patch.object(
        session.session, "get", new=AsyncMock(side_effect=[mock_response_auth, mock_response_auth])
    ):
        with patch.object(session.session, "head", new=AsyncMock(return_value=mock_head_response)):
            with pytest.raises(VintedAuthError) as exc_info:
                await session.request("https://api.vinted.com/test")

    assert exc_info.value.status_code == status_code
    assert exc_info.value.response is mock_response_auth


@pytest.mark.asyncio
async def test_request_network_error():
    session = HttpSession()
    session.base_url = "https://www.vinted.com"
    session.locale = "com"

    with patch.object(
        session.session, "get", new=AsyncMock(side_effect=Exception("Network error"))
    ):
        with pytest.raises(VintedNetworkError):
            await session.request("https://api.vinted.com/test")


@pytest.mark.asyncio
async def test_load_cookies_no_storage():
    session = HttpSession()
    result = session._load_cookies()
    assert result is False


@pytest.mark.asyncio
async def test_load_cookies_with_storage(mock_storage):
    session = HttpSession(storage=mock_storage)
    result = session._load_cookies()

    assert result is True
    mock_storage.load.assert_called_once()


@pytest.mark.asyncio
async def test_clear_session_cookies(mock_storage):
    session = HttpSession(storage=mock_storage)
    with patch.object(session.session.cookies, "clear") as clear_mock:
        session._clear_session_cookies()

    clear_mock.assert_called_once()
    mock_storage.clear.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_cookies_network_error_does_not_clear_storage(mock_storage):
    session = HttpSession(storage=mock_storage)
    session.base_url = "https://www.vinted.com"

    with patch.object(session.session.cookies, "clear") as clear_mock:
        with patch.object(
            session.session, "head", new=AsyncMock(side_effect=Exception("Network error"))
        ):
            with pytest.raises(VintedNetworkError):
                await session.refresh_cookies()

    clear_mock.assert_called_once()
    mock_storage.save.assert_not_called()
    mock_storage.clear.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_cookies_success_does_not_clear_storage(mock_storage):
    session = HttpSession(storage=mock_storage)
    session.base_url = "https://www.vinted.com"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch.object(session.session.cookies, "clear") as clear_mock:
        with patch.object(session.session, "head", new=AsyncMock(return_value=mock_response)):
            await session.refresh_cookies()

    clear_mock.assert_called_once()
    mock_storage.save.assert_called_once()
    mock_storage.clear.assert_not_called()
