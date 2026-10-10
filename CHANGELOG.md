# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added


### Changed


### Fixed


## [1.1.1] - 2026-10-10

### Fixed

- Catalog search uses the `api.` subdomain; the `/web/gateway` path now returns 404

## [1.1.0] - 2026-10-09

### Added

- `patterns_ids[]` catalog filter support
- `CatalogItem.condition` and `CatalogItem.total_item_price`
- `VintedDeprecatedError` for features that no longer work with the Vinted API

### Changed

- Catalog search uses the new `svc-catalogue/items` endpoint with `attribute_ids[...]` filters and sends the `locale` header
- `CatalogItem.brand_title`, `size_title` and `condition` are read from `item_box` in the language of the Vinted domain
- `CatalogItem.price` is always a `float` and `CatalogItem.url` is an absolute URL
- `country_ids[]`, `city_ids[]` and `disposal[]` filters are no longer sent, the API does not support them
- Catalog URLs with the `/api/v2/catalog/items` path are rejected

### Deprecated

- `VintedClient.item_details()` now raises `VintedDeprecatedError`: Vinted removed the item details API
- `CatalogItem.is_new_item()` now raises `VintedDeprecatedError`, `created_at_ts` and `raw_timestamp` always hold epoch and 0; all three will be removed in the next major release

### Fixed

- Catalog search works again after Vinted removed `/api/v2/catalog/items`
- `status_ids[]` filter from catalog URLs is applied


## [1.0.1] - 2026-06-06

### Fixed

- Locale detection now correctly handles multi-part Vinted domains such as `vinted.co.uk` and sets the expected `Accept-Language` header
- Cookie refresh no longer deletes persisted session cookies before a successful refresh and save completes
- Runtime exceptions now match the documented public contract for configuration, validation, rate-limit, authentication, and cookie save failures


## [1.0.0] - 2026-01-05

### Added
- Multiple cookie storage backends: `json`, `mozilla`, and `pickle`
- Dataclass-based models (`CatalogItem`, `DetailedItem`) for performance and clarity
- Custom exception hierarchy to surface network, auth, and validation errors distinctly
- Automatic locale detection from target Vinted URLs
- `SortOrder` and `StorageFormat` type literals for improved typing

### Changed
- Refactored architecture: separated `api/`, `storage/`, and `models/` layers for better maintainability
- Default cookie storage format changed to `json` for security hardening
- SSL verification enabled by default for all HTTP requests
- Proxy configuration simplified to a single string parameter (`proxy="user:pass@host:port"`)
- Cookie persistence now uses strategy pattern

### Fixed
- JWT token expiration parsing (base64url padding handling)
- Retry/logging behavior for authentication failures
- Cookie persistence reliability
- Proxy handling edge cases
- Token expiration detection accuracy

## [0.1.0.post1] - 2025-08-07

### Fixed
- Logo display compatibility for PyPI
- Added project badges to README.md for better presentation
- Corrected CHANGELOG formatting and metadata

## [0.1.0] - 2025-08-07

### Added
- Asynchronous HTTP client for Vinted API with cookie management
- `VintedApi.search_items()` method for item searching with filters
- `VintedApi.item_details()` method for detailed item information
- Support for multiple Vinted domains (fr, de, sk, pl, it, etc.)
- Proxy support for web scraping
- Automatic authentication and session handling
- Cookie persistence between requests
- JWT token expiration detection and refresh
- Comprehensive error handling with retry logic
- Full typing support and async/await patterns
- CI/CD pipeline with GitHub Actions
- 80%+ test coverage

[Unreleased]: https://github.com/vlymar1/vinted-api-kit/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/vlymar1/vinted-api-kit/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/vlymar1/vinted-api-kit/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/vlymar1/vinted-api-kit/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/vlymar1/vinted-api-kit/compare/v0.1.0...v1.0.0
[0.1.0.post1]: https://github.com/vlymar1/vinted-api-kit/compare/v0.1.0...v0.1.0.post1
[0.1.0]: https://github.com/vlymar1/vinted-api-kit/releases/tag/v0.1.0
