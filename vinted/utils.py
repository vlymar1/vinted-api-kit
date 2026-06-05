"""Utility helpers.

Small helpers used across the library for formatting proxy strings and
resolving Accept-Language headers.
"""

from .constants import LOCALE_TO_ACCEPT_LANGUAGE


def format_proxy_for_log(proxy: str | None) -> str:
    """Return a short human-friendly proxy representation for logging.

    Examples:
        None -> "None"
        "user:pass@1.2.3.4:8080" -> "***@1.2.3.4:8080"

    Args:
        proxy: Proxy string or None.

    Returns:
        A redacted string safe for logs.
    """
    if not proxy:
        return "None"
    if "@" in proxy:
        parts = proxy.split("@")
        return "***@%s" % parts[-1]
    return proxy


def get_accept_language(locale: str) -> str:
    """Return an Accept-Language header value for `locale`.

    The returned value contains the full locale code and a fallback
    language prefix with a lower q-value.
    """
    locale_code = LOCALE_TO_ACCEPT_LANGUAGE.get(locale, "en-US")
    lang_prefix = locale_code.split("-")[0]
    return "%s,%s;q=0.9" % (locale_code, lang_prefix)
