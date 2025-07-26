# vinted-api-kit

**Lightweight asynchronous Python client library for accessing Vinted API and scraping item data.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Installation

Install via pip:
```bash
pip install vinted-api-kit
```
Or using poetry:
```bash
poetry add vinted-api-kit
```
---

## Quick Start

```python
import asyncio
from vinted_api_kit import VintedApi

async def main():
    async with VintedApi(locale="fr") as vinted:
        items = await vinted.search_items(
            url="https://www.vinted.fr/catalog?search_text=adidas"
        )
        for item in items:
            print(f"{item.title}: {item.price} {item.currency}")

asyncio.run(main())
```


---

## Configuration

- `locale` - locale string for API requests, e.g. `'fr'`, `'de'`, `'us'`.
- `proxies` - dictionary of proxy settings if needed.
- `client_ip` - optional IP header override.
- `cookies_dir` - directory path for persisting cookies.
- `persist_cookies` - boolean to enable or disable cookie persistence.

These can be set when creating an instance of the `VintedApi` class.

No additional environment variables are required by default.

---

## Run tests:

```shell
poetry run pytest -v
```

## Run linters and formatters:

To lint and format your code with ruff, run:

```shell
poetry run ruff check vinted_api_kit tests dev
poetry run ruff check --fix vinted_api_kit tests dev # to auto-fix issues where possible
```

Please configure ruff with a `pyproject.toml` or `.ruff.toml` file for your preferred rules.

Make sure to follow PEP8 style guidelines.

It is recommended to set up pre-commit hooks with ruff for automatic linting on git operations.

Contributions are welcome! Please open issues or pull requests.

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

---

## Maintainers / Contacts

- GitHub: [https://github.com/vlymar1](https://github.com/vlymar1)

Feel free to open issues or contact for support and collaborations.
