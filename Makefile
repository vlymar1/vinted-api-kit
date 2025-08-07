package_dir := vinted_api_kit
tests_dir := tests
reports_dir := reports

# ===========
# Environment
# ===========

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf `find . -name .pytest_cache`
	rm -rf *.egg-info
	rm -f report.html
	rm -f .coverage
	rm -rf {build,dist,.cache,.mypy_cache,.ruff_cache,reports,.tox}

# ============
# Code quality
# ============

.PHONY: lint-check
lint-check:
	ruff check $(package_dir)
	mypy $(package_dir)

.PHONY: lint-reformat
lint-reformat:
	ruff check --fix $(package_dir)
	ruff format $(package_dir)

# ======
# Tests
# ======
.PHONY: test-coverage
test-coverage:
	mkdir -p $(reports_dir)/tests/
	pytest --cov=vinted_api_kit --cov-config .coveragerc --html=$(reports_dir)/tests/index.html tests/
	coverage html -d $(reports_dir)/coverage

.PHONY: test-coverage-view
test-coverage-view:
	coverage html -d $(reports_dir)/coverage
	python -c "import webbrowser; webbrowser.open('file://$(shell pwd)/reports/coverage/index.html')"
