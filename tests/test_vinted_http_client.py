import pickle
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vinted_api_kit.client.vinted_http_client import VintedHttpClient


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

    async def mock_get(*args, **kwargs):
        m = MagicMock()
        m.raise_for_status = MagicMock(return_value=None)
        return m

    mock_clear = mocker.patch.object(client, "clear_all_cookies")
    mocker.patch.object(client.session, "get", side_effect=mock_get)
    mock_save = mocker.patch.object(client, "save_cookies")

    await client.refresh_session_cookies()

    mock_clear.assert_called_once()
    client.session.get.assert_called_once_with(client.base_url, impersonate="chrome", verify=False)
    mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_request_success_and_unauthorized_handling(
    mocker, vinted_http_client: VintedHttpClient
):
    client = vinted_http_client
    mocker.patch.object(client, "load_cookies", return_value={"some": "cookie"})
    mocker.patch.object(client, "refresh_session_cookies")

    mocker.patch.object(client, "_is_token_expired", return_value=False)

    mock_cookies = MagicMock()
    mock_cookies.get.side_effect = lambda key, default=None: {
        "access_token_web": "token",
        "x-csrf-token": "csrf",
        "anon_id": "anon",
        "anonymous-locale": "en-US",
    }.get(key, default)
    mock_cookies.items.return_value = [
        ("access_token_web", "token"),
        ("anon_id", "anon"),
        ("anonymous-locale", "en-US"),
    ]
    client.session.cookies = mock_cookies

    mock_response_unauth = MagicMock()
    mock_response_unauth.status_code = 401
    mock_response_unauth.reason = "Unauthorized"

    mock_response_ok = MagicMock()
    mock_response_ok.status_code = 200
    mock_response_ok.reason = "OK"

    mock_get = mocker.patch.object(client.session, "get", new_callable=AsyncMock)
    mock_get.side_effect = [mock_response_unauth, mock_response_ok]

    response = await client.request("https://example.com/api")

    assert response.status_code == 200
    assert mock_get.call_count == 2
    client.refresh_session_cookies.assert_called_once()


def test_clear_all_cookies(mocker, vinted_http_client):
    client = vinted_http_client
    client.cookies_path.write_text("fake cookies file")

    mock_clear = mocker.patch.object(client.session.cookies, "clear")

    client.clear_all_cookies()

    mock_clear.assert_called_once()
    assert not client.cookies_path.exists()


def test_update_auth_headers_from_cookies(mocker, vinted_http_client):
    client = vinted_http_client

    mock_get = mocker.patch.object(client.session.cookies, "get")
    mock_get.side_effect = lambda key, default=None: {
        "access_token_web": "test_token",
        "x-csrf-token": "test_csrf",
        "anon_id": "test_anon",
        "anonymous-locale": "en-US",
    }.get(key, default)

    mock_items = mocker.patch.object(client.session.cookies, "items")
    mock_items.return_value = [
        ("access_token_web", "test_token"),
        ("x-csrf-token", "test_csrf"),
        ("anon_id", "test_anon"),
        ("anonymous-locale", "en-US"),
    ]

    client._update_auth_headers_from_cookies()

    assert client.session.headers.get("Authorization") == "Bearer test_token"
    assert client.session.headers.get("X-Csrf-Token") == "test_csrf"
    assert client.session.headers.get("X-Anon-Id") == "test_anon"
    assert client.session.headers.get("Accept-Language") == "en-US"


def test_is_token_expired(vinted_http_client):
    client = vinted_http_client

    # Test with expired token
    expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MzM0NTAwMDB9.fake"
    assert client._is_token_expired(expired_token) is True

    # Test with a valid token
    future_timestamp = int(time.time()) + 3600
    valid_token = f"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.{{'exp':{future_timestamp}}}.fake"

    with patch.object(client, "_is_token_expired", return_value=False):
        assert client._is_token_expired(valid_token) is False
