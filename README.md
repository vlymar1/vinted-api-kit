<div align="center">

![Vinted Api Kit logo](https://raw.githubusercontent.com/vlymar1/vinted-api-kit/main/assets/logo.png)

***Lightweight asynchronous Python client library for accessing Vinted API and scraping item data.***

[![Package Version](https://img.shields.io/pypi/v/vinted-api-kit.svg)](https://pypi.org/project/vinted-api-kit/)
[![Python Version](https://img.shields.io/pypi/pyversions/vinted-api-kit.svg)](https://pypi.org/project/vinted-api-kit/)
[![codecov](https://codecov.io/github/vlymar1/vinted-api-kit/graph/badge.svg?token=SLCFGVYDOM)](https://codecov.io/github/vlymar1/vinted-api-kit)
[![Downloads](https://static.pepy.tech/badge/vinted-api-kit)](https://pepy.tech/project/vinted-api-kit)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Typed](https://img.shields.io/badge/typed-mypy-blue)](http://mypy-lang.org/)
[![License](https://img.shields.io/pypi/l/vinted-api-kit.svg)](https://github.com/vlymar1/vinted-api-kit/blob/main/LICENSE)
</div>

## ✨ Features

- 🚀 **Asynchronous** - Built with asyncio for high performance
- 🌍 **Auto-locale Detection** - Automatically detects locale from URL
- 🔍 **Item Search** - Search catalog with filters, sorting and pagination
- 📦 **Item Details** - Get complete item information with rich metadata
- 🍪 **Cookie Persistence** - Automatic session management with multiple storage formats
- 🔐 **Proxy Support** - Simple string-based proxy configuration
- 📊 **Type Hints** - Full typing support with Literal types for better IDE experience
- 🎯 **Dataclass Models** - Fast and efficient data models (15% performance boost)
- 🛡️ **Custom Exceptions** - Detailed error hierarchy for precise error handling
- 💾 **Flexible Storage** - Choose between pickle, JSON, or Mozilla cookie formats

## 📚 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Migration Guide](#migration-guide)
- [Development](#development)
- [Changelog](#changelog)
- [License](#license)

## Installation

Install via pip:
```bash
pip install vinted-api-kit
```
Or using poetry:
```bash
poetry add vinted-api-kit
```

## Usage

### Basic Example
```python
import asyncio
from vinted import VintedClient

async def main():
    async with VintedClient() as client:
        items = await client.search_items(
            url="https://www.vinted.com/catalog?search_text=nike",
            per_page=5
        )

        for item in items:
            print(f"• {item.title} - {item.price} {item.currency}")

asyncio.run(main())
```

---

### Configuration

#### 🔐 Proxy Support

> Use a proxy by passing a simple connection string:
```python
async with VintedClient(
    proxy="user:pass@proxy.example.com:8080"  # Format: [user:pass@]host:port
) as client:
    items = await client.search_items(url)
```

#### 💾 Cookie Persistence

> Save cookies between sessions to avoid repeated authentication:
```python
from pathlib import Path

async with VintedClient(
    persist_cookies=True,              # Enable persistence
    cookies_dir=Path("./cookies"),     # Storage directory
    storage_format="json"              # Format: pickle | json | mozilla
) as client:
    items = await client.search_items(url)
```

**Storage formats:**
- **`"json"`** (default) - Human-readable, portable across platforms
- **`"pickle"`** - Fastest, Python-native binary format
- **`"mozilla"`** - Browser-compatible Netscape format

#### 🔍 Search Options

> Use type-safe sorting and pagination:
```python
from vinted import SortOrder

items = await client.search_items(
    url="https://www.vinted.de/catalog?brand_ids[]=53",
    per_page=20,                      # Items per page (1-96)
    page=1,                           # Page number
    order="price_low_to_high"         # Sort order (IDE auto-complete)
)
```

**Available sort orders:**
- `newest_first` - Most recent items
- `relevance` - Best match
- `price_low_to_high` - Cheapest first
- `price_high_to_low` - Most expensive first

#### 📦 Raw Data

> Get raw JSON dictionaries instead of parsed models:
```python
raw_items = await client.search_items(
    url="https://www.vinted.com/catalog?search_text=shoes",
    raw_data=True  # Returns list[dict] instead of list[CatalogItem]
)
```

---

### Item Details

> Fetch detailed information about a specific item:
```python
item = await client.item_details(
    url="https://www.vinted.com/items/1234567890"
)

print(f"Title: {item.title}")
print(f"Brand: {item.brand_title}")
print(f"Size: {item.size_title}")
print(f"Price: {item.price} {item.currency}")
print(f"Total: {item.total_item_price}")
print(f"Description: {item.description}")

# Or get raw JSON
raw_item = await client.item_details(url, raw_data=True)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `proxy` | `str \| None` | `None` | Proxy string: `"user:pass@host:port"` or `"host:port"` |
| `cookies_dir` | `Path \| None` | `Path(".")` | Directory for cookie storage |
| `persist_cookies` | `bool` | `False` | Enable cookie persistence between sessions |
| `storage_format` | `"json" \| "pickle" \| "mozilla"` | `"json"` | Cookie storage format |

**Storage formats:** `json` (default), `pickle`, `mozilla`. See [Storage Formats](#storage-formats:) for details.



### Exception Handling
```python
from vinted import (
    VintedClient,
    VintedError,           # Base exception
    VintedAPIError,        # API errors (4xx, 5xx)
    VintedAuthError,       # Authentication failures
    VintedNetworkError,    # Network/connection errors
    VintedConfigError,     # Invalid configuration
    VintedValidationError, # Input validation errors
    VintedRateLimitError,  # Rate limiting (429)
)

try:
    async with VintedClient(proxy="invalid://proxy") as client:
        items = await client.search_items(url)
except VintedConfigError as e:
    print(f"Configuration error: {e}")
except VintedValidationError as e:
    print(f"Invalid input: {e}")
except VintedRateLimitError as e:
    print(f"Rate limited: {e.status_code}")
except VintedAuthError as e:
    print(f"Auth failed: {e}")
except VintedNetworkError as e:
    print(f"Network error: {e.original_error}")
except VintedAPIError as e:
    print(f"API error: {e.status_code}")
```


---
## Migration Guide
### (v0.x → v1.0)
### Breaking Changes

If you're upgrading from version 0.x, here are the key changes:

#### 1. Import Path Changed
```python
# ❌ Old (v0.x)
from vinted_api_kit import VintedApi

# ✅ New (v1.0)
from vinted import VintedClient
```

#### 2. Class Renamed
```python
# ❌ Old
async with VintedApi() as api:
    pass

# ✅ New
async with VintedClient() as client:
    pass
```

#### 3. Locale Parameter Removed
```python
# ❌ Old (manual locale)
async with VintedApi(locale="fr") as api:
    items = await api.search_items(url)

# ✅ New (auto-detected from URL)
async with VintedClient() as client:
    items = await client.search_items(url)  # Locale detected from URL
```

#### 4. Proxy Configuration Changed
```python
# ❌ Old (dict format)
async with VintedApi(
    proxies={"http": "http://user:pass@proxy:8080"}
) as api:
    pass

# ✅ New (simple string)
async with VintedClient(
    proxy="user:pass@proxy:8080"  # ← Without "http://"
) as client:
    pass
```

#### 5. New Storage Format Option
```python
# ✅ New feature in v1.0
async with VintedClient(
    persist_cookies=True,
    storage_format="json"  # Choose: "json", "pickle", "mozilla"
) as client:
    pass
```

### Quick Migration Checklist

- [ ] Change import: `vinted_api_kit` → `vinted`
- [ ] Rename class: `VintedApi` → `VintedClient`
- [ ] Remove `locale` parameter (auto-detected)
- [ ] Update proxy format: dict → string
- [ ] Optional: Choose storage format

### Full Example

**Before (v0.x):**
```python
from vinted_api_kit import VintedApi

async with VintedApi(
    locale="fr",
    proxies={"http": "http://proxy:8080"},
    persist_cookies=True
) as api:
    items = await api.search_items(
        url="https://www.vinted.fr/catalog?search_text=nike"
    )
```

**After (v1.0):**
```python
from vinted import VintedClient

async with VintedClient(
    proxy="proxy:8080",
    persist_cookies=True,
    storage_format="pickle"  # New option!
) as client:
    items = await client.search_items(
        url="https://www.vinted.fr/catalog?search_text=nike"
    )
```

---
## Development

### Setup
```bash
git clone https://github.com/vlymar1/vinted-api-kit.git
cd vinted-api-kit

pip install hatch
hatch shell
```

### Project Structure
```
vinted-api-kit/
├── vinted/             # Main package
│   ├── api/            # API endpoint handlers
│   ├── models/         # Data models (dataclasses)
│   ├── storage/        # Cookie storage strategies
│   ├── client.py       # Main client (VintedClient)
│   ├── session.py      # HTTP session management
│   ├── auth.py         # Authentication logic
│   ├── constants.py    # Constants and type definitions
│   ├── exceptions.py   # Custom exceptions
│   └── utils.py        # Utility functions
├── tests/              # Test suite
└── examples/           # Usage examples
```

### Testing
```bash
make test-coverage      # Run tests with coverage
make test-coverage-view # View coverage report in browser
```

### Code Quality
```bash
make lint-check         # Check code with ruff and mypy
make lint-reformat      # Format and fix code with ruff
```

### Cleanup
```bash
make clean              # Remove cache files and build artifacts
```

### Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write tests for new features
- Update CHANGELOG.md for notable changes
- Run `make lint-check` before committing
- Contributions welcome! Open issues or pull requests

---
## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for the list of notable changes per version.

### How to create and maintain changelog?

- Start a `CHANGELOG.md` file at the root of your repo.
- Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format for consistent structure.
- For each release version, record:
  - Added — new features
  - Changed — updates/improvements
  - Fixed — bug fixes
  - Removed — deprecated or removed features
- Update changelog **before** tagging a new release (e.g., `v1.0.0`).
- Automate changelog generation optionally by tools such as:
  - [github-changelog-generator](https://github.com/github-changelog-generator/github-changelog-generator)
  - [auto-changelog](https://github.com/CookPete/auto-changelog)
  - Conventional commits combined with [semantic-release](https://semantic-release.gitbook.io/semantic-release/)

---
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

_⚠ Disclaimer_

This library is intended for personal and lawful use only.
The author is not responsible for any misuse, including but not limited to:
- Violations of applicable laws or regulations
- Breaches of terms of service of third-party websites

_By using this library, you agree that you are solely responsible for your actions._

---
## Maintainers / Contacts

- GitHub: [https://github.com/vlymar1](https://github.com/vlymar1)

Feel free to open issues or contact for support and collaborations.
