import asyncio
import pickle
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vinted_api_kit.client import VintedHttpClient


def test_init_headers_and_attrs(vinted_http_client: VintedHttpClient):
    client = vinted_http_client

    assert "User-Agent" in client.session.headers
    assert "X-Forwarded-For" in client.session.headers
    assert client.cookies_path.exists() is False


@patch("pickle.dump")
def test_save_cookies_call_pickle_dump(mock_pickle_dump, vinted_http_client: VintedHttpClient):
    client = vinted_http_client
    cookies_jar = client.session.cookies.jar
    setattr(cookies_jar, "_cookies", {"sessid": "123456"})
    client.persist_cookies = True

    client.save_cookies()

    mock_pickle_dump.assert_called_once()


def test_load_cookies_with_existing_file(tmp_path, vinted_http_client: VintedHttpClient):
    client = vinted_http_client
    client.persist_cookies = True
    cookie_path = client.cookies_path
    cookie_path.write_bytes(pickle.dumps({"sessid": "abc"}))

    cookies = client.load_cookies()

    assert cookies == {"sessid": "abc"}


def test_configure_from_url_sets_base_url_and_locale(vinted_http_client):
    client = vinted_http_client
    url = "https://www.vinted.fr/catalog/123"

    client.configure_from_url(url)

    assert client.base_url == "https://www.vinted.fr"
    assert client.locale == "fr"
    assert client.session.headers["Referer"] == client.base_url


@pytest.mark.asyncio
async def test_refresh_session_cookies_calls(mocker, vinted_http_client):
    client = vinted_http_client
    client.base_url = "https://test"

    async def mock_head(*args, **kwargs):
        m = MagicMock()
        m.raise_for_status = MagicMock(return_value=None)
        return m

    mocker.patch.object(client.session, "head", side_effect=mock_head)
    mock_save = mocker.patch.object(client, "save_cookies")

    await client.refresh_session_cookies()

    client.session.head.assert_called_once_with(client.base_url)
    mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_request_success_and_unauthorized_handling(
    mocker, vinted_http_client: VintedHttpClient
):
    client = vinted_http_client
    mocker.patch.object(client, "load_cookies", return_value={"some": "cookie"})
    fut = asyncio.Future()
    fut.set_result(None)
    mocker.patch.object(client, "refresh_session_cookies", return_value=fut)
    mocker.patch.object(
        client.session.cookies,
        "get",
        side_effect=lambda key, default=None: {
            "access_token_web": "token",
            "x-csrf-token": "csrf",
            "anon_id": "anon",
            "anonymous-locale": "en-US",
        }.get(key, default),
    )

    async def mock_response_unauth():
        m = AsyncMock()
        m.status_code = 401
        m.reason = "Unauthorized"
        m.json.return_value = {}
        m.raise_for_status.return_value = None
        return m

    async def mock_response_ok():
        m = AsyncMock()
        m.status_code = 200
        m.reason = "OK"
        m.json.return_value = {}
        m.raise_for_status.return_value = None
        return m

    side_effects = [mock_response_unauth(), mock_response_ok()]
    mock_get = mocker.patch.object(client.session, "get", side_effect=side_effects)

    response = await client.request("https://example.com/api")

    assert response.status_code == 200
    assert mock_get.call_count == 2
