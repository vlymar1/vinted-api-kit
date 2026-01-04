from pathlib import Path

import pytest

from vinted.models.config import ClientConfig


def test_config_default_values():
    config = ClientConfig()

    assert config.proxy is None
    assert config.cookies_dir == Path(".")
    assert config.persist_cookies is False
    assert config.storage_format == "json"


def test_config_with_values(tmp_path):
    config = ClientConfig(
        proxy="proxy:8080", cookies_dir=tmp_path, persist_cookies=True, storage_format="mozilla"
    )

    assert config.proxy == "proxy:8080"
    assert config.cookies_dir == tmp_path
    assert config.persist_cookies is True
    assert config.storage_format == "mozilla"


def test_config_creates_cookies_dir(tmp_path):
    cookies_dir = tmp_path / "cookies"
    assert not cookies_dir.exists()

    _ = ClientConfig(cookies_dir=cookies_dir)

    assert cookies_dir.exists()


def test_config_string_path_conversion():
    config = ClientConfig(cookies_dir=Path("./cookies"))

    assert isinstance(config.cookies_dir, Path)
    assert config.cookies_dir == Path("./cookies")


@pytest.mark.parametrize("format", ["pickle", "json", "mozilla"])
def test_config_valid_storage_formats(format):
    config = ClientConfig(storage_format=format)
    assert config.storage_format == format
