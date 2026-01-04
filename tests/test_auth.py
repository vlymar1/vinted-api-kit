import base64
import json
import time

from vinted.auth import AuthManager


def test_auth_manager_init(mock_async_session):
    auth = AuthManager(mock_async_session)
    assert auth.session == mock_async_session


def test_is_token_expired_no_token(mock_async_session):
    mock_async_session.cookies.get.return_value = None

    auth = AuthManager(mock_async_session)
    assert auth.is_token_expired() is True


def test_is_token_expired_invalid_token(mock_async_session):
    mock_async_session.cookies.get.return_value = "invalid.token.format"

    auth = AuthManager(mock_async_session)
    assert auth.is_token_expired() is True


def test_is_token_expired_valid_token_not_expired(mock_async_session):
    future_timestamp = int(time.time()) + 3600
    payload = {"exp": future_timestamp}
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    token = f"header.{payload_b64}.signature"

    mock_async_session.cookies.get.return_value = token

    auth = AuthManager(mock_async_session)
    assert auth.is_token_expired() is False


def test_is_token_expired_valid_token_expired(mock_async_session):
    past_timestamp = int(time.time()) - 3600
    payload = {"exp": past_timestamp}
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    token = f"header.{payload_b64}.signature"

    mock_async_session.cookies.get.return_value = token

    auth = AuthManager(mock_async_session)
    assert auth.is_token_expired() is True


def test_validate_jwt_expiration_malformed():
    result = AuthManager._validate_jwt_expiration("malformed")
    assert result is True


def test_validate_jwt_expiration_missing_exp():
    payload = {"sub": "user"}
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    token = f"header.{payload_b64}.signature"

    result = AuthManager._validate_jwt_expiration(token)
    assert result is True
