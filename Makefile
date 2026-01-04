package_dir := vinted
tests_dir := tests
reports_dir := reports

# ===========
# Environment
# ===========
.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]'`
	rm -f `find . -type f -name '*~'`
	rm -f `find . -type f -name '.*~'`
	rm -rf `find . -name .pytest_cache`
	rm -rf *.egg-info
	rm -f report.html
	rm -f .coverage
	rm -rf {build,dist,.cache,.mypy_cache,.ruff_cache,.hatch,reports,.tox}
	rm -rf htmlcov/


# ===========
# Development
# ===========
.PHONY: install
install:
	pip install hatch

.PHONY: install-dev
install-dev:
	hatch env create


# ============
# Code quality
# ============
.PHONY: lint
lint:
	hatch run lint

.PHONY: lint-check
lint-check:
	hatch run ruff check $(package_dir)
	hatch run mypy $(package_dir)

.PHONY: format
format:
	hatch run format

.PHONY: type-check
type-check:
	hatch run type-check

# ======
# Tests
# ======
.PHONY: test
test:
	hatch run test

.PHONY: test-cov
test-coverage:
	mkdir -p $(reports_dir)/tests/
	hatch run pytest --cov=$(package_dir) --cov-report=html:$(reports_dir)/coverage --cov-report=term-missing --html=$(reports_dir)/tests/index.html $(tests_dir)

.PHONY: test-coverage-view
test-coverage-view: test-coverage
	python -c "import webbrowser; webbrowser.open('file://$(shell pwd)/$(reports_dir)/coverage/index.html')"


# =====
# Build
# =====
.PHONY: build
build: clean
	hatch build

.PHONY: publish
publish: build
	hatch publish

.PHONY: publish-test
publish-test: build
	hatch publish -r test

# ===
# All
# ===
.PHONY: all
all:
	hatch run all
