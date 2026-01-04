from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vinted.constants import HTTP_STATUS_UNAUTHORIZED
from vinted.exceptions import VintedAPIError, VintedNetworkError
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


def test_configure_from_url():
    session = HttpSession()
    session.configure_from_url("https://www.vinted.fr/catalog")

    assert session.base_url == "https://www.vinted.fr"
    assert session.locale == "fr"
    assert "Accept-Language" in session.session.headers


@pytest.mark.asyncio
async def test_refresh_cookies_no_base_url():
    session = HttpSession()

    with pytest.raises(VintedAPIError, match="base_url not configured"):
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
async def test_clear_cookies(mock_storage):
    session = HttpSession(storage=mock_storage)
    session._clear_cookies()

    mock_storage.clear.assert_called_once()
