from typing import Any
from unittest.mock import MagicMock

from vinted.storage.mozilla import MozillaStorage


def test_mozilla_storage_save(temp_cookies_dir: Any):
    storage = MozillaStorage(temp_cookies_dir / "cookies.txt")

    mock_cookie = MagicMock()
    mock_cookie.name = "test_cookie"
    mock_cookie.value = "test_value"
    mock_cookie.domain = ".vinted.com"
    mock_cookie.path = "/"
    mock_cookie.secure = False
    mock_cookie.expires = None
    mock_cookie.discard = False
    mock_cookie.comment = None
    mock_cookie.comment_url = None

    mock_jar = MagicMock()
    mock_jar._cookies = {".vinted.com": {"/": {"test_cookie": mock_cookie}}}

    storage.save(mock_jar)

    assert storage.filepath.exists()
    content = storage.filepath.read_text()
    assert "# Netscape HTTP Cookie File" in content


def test_mozilla_storage_load(temp_cookies_dir: Any):
    storage = MozillaStorage(temp_cookies_dir / "cookies.txt")

    with storage.filepath.open("w") as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write(".vinted.com\tTRUE\t/\tFALSE\t0\ttest_cookie\ttest_value\n")

    mock_jar = MagicMock()
    storage.load(mock_jar)

    mock_jar.clear.assert_called_once()
    mock_jar.set_cookie.assert_called()


def test_mozilla_storage_load_nonexistent(temp_cookies_dir: Any):
    storage = MozillaStorage(temp_cookies_dir / "nonexistent.txt")
    mock_jar = MagicMock()

    storage.load(mock_jar)
