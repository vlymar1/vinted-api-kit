from unittest.mock import MagicMock

from vinted.storage.pickle import PickleStorage


def test_pickle_storage_save(temp_cookies_dir):
    storage = PickleStorage(temp_cookies_dir / "cookies.pk")

    mock_jar = MagicMock()
    mock_jar._cookies = {"domain": {"path": {"name": "cookie"}}}

    storage.save(mock_jar)

    assert storage.filepath.exists()


def test_pickle_storage_load(temp_cookies_dir):
    storage = PickleStorage(temp_cookies_dir / "cookies.pk")

    save_jar = MagicMock()
    save_jar._cookies = {"domain": {"path": {"cookie": "value"}}}
    storage.save(save_jar)

    load_jar = MagicMock()
    load_jar._cookies = MagicMock()

    storage.load(load_jar)

    load_jar._cookies.update.assert_called_once_with({"domain": {"path": {"cookie": "value"}}})


def test_pickle_storage_load_nonexistent(temp_cookies_dir):
    storage = PickleStorage(temp_cookies_dir / "nonexistent.pk")

    mock_jar = MagicMock()

    storage.load(mock_jar)


def test_storage_exists(temp_cookies_dir):
    storage = PickleStorage(temp_cookies_dir / "cookies.pk")
    assert not storage.exists()

    storage.filepath.touch()
    assert storage.exists()


def test_storage_clear(temp_cookies_dir):
    storage = PickleStorage(temp_cookies_dir / "cookies.pk")
    storage.filepath.touch()

    storage.clear()
    assert not storage.exists()


def test_storage_clear_nonexistent(temp_cookies_dir):
    storage = PickleStorage(temp_cookies_dir / "nonexistent.pk")

    storage.clear()
