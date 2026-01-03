"""Constants and small type aliases used across the library.

This module contains supported locales, mapping to Accept-Language
values, URL templates and small Literal type aliases used for public
function signatures.
"""

from typing import Literal

VALID_LOCALES = [
    "pl",
    "fr",
    "at",
    "be",
    "cz",
    "de",
    "dk",
    "es",
    "fi",
    "gr",
    "hr",
    "hu",
    "it",
    "lt",
    "lu",
    "nl",
    "pt",
    "ro",
    "se",
    "sk",
    "co.uk",
    "com",
]

LOCALE_TO_ACCEPT_LANGUAGE = {
    "pl": "pl-PL",
    "fr": "fr-FR",
    "at": "de-AT",
    "be": "fr-BE",
    "cz": "cs-CZ",
    "de": "de-DE",
    "dk": "da-DK",
    "es": "es-ES",
    "fi": "fi-FI",
    "gr": "el-GR",
    "hr": "hr-HR",
    "hu": "hu-HU",
    "it": "it-IT",
    "lt": "lt-LT",
    "lu": "fr-LU",
    "nl": "nl-NL",
    "pt": "pt-PT",
    "ro": "ro-RO",
    "se": "sv-SE",
    "sk": "sk-SK",
    "co.uk": "en-GB",
    "com": "en-US",
}

VINTED_BASE_URL_TEMPLATE = "https://www.vinted.{locale}"

SortOrder = Literal["newest_first", "relevance", "price_high_to_low", "price_low_to_high"]

StorageFormat = Literal["pickle", "json", "mozilla"]

HTTP_STATUS_OK = 200
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403
HTTP_STATUS_RATE_LIMIT = 429


DEFAULT_HEADERS = {
    "Cache-Control": "max-age=0",
    "DNT": "1",
    "X-Money-Object": "true",
}
