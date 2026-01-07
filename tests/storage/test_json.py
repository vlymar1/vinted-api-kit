import json
from unittest.mock import MagicMock

import pytest

from vinted.storage.json import JsonStorage


def test_json_storage_save(temp_cookies_dir):
    storage = JsonStorage(temp_cookies_dir / "cookies.json")

    class FakeCookie:
        def __init__(self):
            self.name = "test_cookie"
            self.value = "test_value"
            self.domain = "domain.com"
            self.path = "/"
            self.secure = False
            self.expires = None
            self.discard = False
            self.comment = None
            self.comment_url = None
            self.rest = {}
            self.rfc2109 = False

    mock_jar = MagicMock()
    mock_jar._cookies = {"domain.com": {"/": {"cookie_name": FakeCookie()}}}

    storage.save(mock_jar)

    assert storage.filepath.exists()
    with storage.filepath.open("r") as f:
        data = json.load(f)
        assert "domain.com|/|cookie_name" in data
        assert data["domain.com|/|cookie_name"]["name"] == "test_cookie"


def test_json_storage_load(temp_cookies_dir):
    storage = JsonStorage(temp_cookies_dir / "cookies.json")

    test_data = {
        "domain.com|/|cookie": {
            "name": "test_cookie",
            "value": "test_value",
            "domain": "domain.com",
            "path": "/",
            "secure": False,
            "expires": None,
            "discard": False,
            "comment": None,
            "comment_url": None,
            "rest": {},
            "rfc2109": False,
        }
    }

    with storage.filepath.open("w") as f:
        json.dump(test_data, f)

    mock_jar = MagicMock()
    storage.load(mock_jar)

    mock_jar.clear.assert_called_once()
    mock_jar.set_cookie.assert_called_once()


def test_json_storage_load_nonexistent(temp_cookies_dir):
    storage = JsonStorage(temp_cookies_dir / "nonexistent.json")
    mock_jar = MagicMock()

    storage.load(mock_jar)


def test_json_storage_corrupted_file(temp_cookies_dir):
    storage = JsonStorage(temp_cookies_dir / "corrupted.json")

    with storage.filepath.open("w") as f:
        f.write("not valid json{{{")

    mock_jar = MagicMock()

    with pytest.raises(Exception):
        storage.load(mock_jar)


def test_json_storage_empty_file(temp_cookies_dir):
    storage = JsonStorage(temp_cookies_dir / "empty.json")

    with storage.filepath.open("w") as f:
        json.dump({}, f)

    mock_jar = MagicMock()
    storage.load(mock_jar)

    mock_jar.clear.assert_called_once()
