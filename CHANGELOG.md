# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added


### Changed


### Fixed



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

[Unreleased]: https://github.com/vlymar1/vinted-api-kit/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/vlymar1/vinted-api-kit/compare/v0.1.0...v1.0.0
[0.1.0.post1]: https://github.com/vlymar1/vinted-api-kit/compare/v0.1.0...v0.1.0.post1
[0.1.0]: https://github.com/vlymar1/vinted-api-kit/releases/tag/v0.1.0
