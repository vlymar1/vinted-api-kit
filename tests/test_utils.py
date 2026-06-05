import pytest

from vinted.utils import format_proxy_for_log, get_accept_language


def test_format_proxy_with_auth():
    proxy = "user:pass@proxy.com:8080"
    result = format_proxy_for_log(proxy)
    assert result == "***@proxy.com:8080"


def test_format_proxy_without_auth():
    proxy = "proxy.com:8080"
    result = format_proxy_for_log(proxy)
    assert result == "proxy.com:8080"


def test_format_proxy_none():
    result = format_proxy_for_log(None)
    assert result == "None"


@pytest.mark.parametrize(
    "locale,expected",
    [
        ("fr", "fr-FR,fr;q=0.9"),
        ("de", "de-DE,de;q=0.9"),
        ("com", "en-US,en;q=0.9"),
    ],
)
def test_get_accept_language(locale, expected):
    result = get_accept_language(locale)
    assert result == expected
