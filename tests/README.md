# Reddit Scraper Tests

This directory contains comprehensive unit tests for the Reddit Scraper application.

## Test Structure

- `test_integration.py` - Integration tests that test core functionality without external dependencies
- `test_utils.py` - Tests for utility functions (logging, file operations)
- `test_reddit_scraper.py` - Comprehensive unit tests including mocked HTTP requests (requires `responses` library)
- `conftest.py` - Pytest configuration and shared fixtures

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

Using pytest (recommended):
```bash
python -m pytest tests/
```

Using unittest:
```bash
python -m unittest discover tests/
```

### Run Specific Test Files

```bash
# Integration tests (no external dependencies)
python -m pytest tests/test_integration.py

# Utility function tests
python -m pytest tests/test_utils.py

# Full unit tests (requires responses library)
python -m pytest tests/test_reddit_scraper.py
```

### Run Tests with Coverage

```bash
pip install pytest-cov
python -m pytest tests/ --cov=src.reddit_scraper --cov-report=html
```

## Test Coverage

The tests cover:

- ✅ Scraper initialization with various configurations
- ✅ Config file loading and error handling
- ✅ Post data extraction and filtering
- ✅ JSON file saving (individual and combined)
- ✅ Log management functionality
- ✅ Utility functions
- ✅ HTTP request mocking (with responses library)
- ✅ Error handling and edge cases

## Dependencies

### Required
- `pytest` - Test framework
- `unittest.mock` - Built-in mocking (Python 3.3+)

### Optional
- `responses` - HTTP request mocking (for network-related tests)
- `pytest-mock` - Additional mocking utilities
- `pytest-cov` - Coverage reporting

## Notes

- Tests that require the `responses` library will be skipped if it's not installed
- Integration tests work without any external dependencies
- All tests use temporary directories and don't affect your actual files
- The scraper's sleep functionality is set to minimal values during testing for speed
- Tests automatically configure the Python path to import from the `src/` directory
