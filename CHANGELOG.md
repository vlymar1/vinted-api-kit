# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- User profile retrieval functionality
- Support for fetching user's own items
- Enhanced error handling for network timeouts

## [0.1.0] - 2025-01-30

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

[Unreleased]: https://github.com/vlymar-dev/vinted-api-kit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/vlymar-dev/vinted-api-kit/releases/tag/v0.1.0
