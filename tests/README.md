# Testing Documentation

This directory contains comprehensive tests for the Diabetes Tracker application using pytest.

## Test Structure

### Test Files

- **`test_app.py`** - Core application tests including authentication, data management, AI recommendations, and Flask application tests
- **`test_chart.py`** - Chart functionality and API endpoint tests

### Test Categories

The tests are organized into several categories:

#### Unit Tests
- **Authentication Tests** (`TestAuthentication` class)
  - User registration and login
  - Password hashing
  - User existence checking
  - Duplicate registration prevention

- **Data Management Tests** (`TestDataManagement` class)
  - Entry saving and retrieval
  - User history and statistics
  - Chart data formatting
  - Entry deletion

- **AI Recommendation Tests** (`TestAIRecommendations` class)
  - Basic recommendation generation
  - Blood sugar analysis
  - Meal and exercise suggestions

#### Integration Tests
- **Flask Application Tests** (`TestFlaskApplication` class)
  - Route existence and functionality
  - API endpoint testing
  - Response validation

- **Complete Workflow Tests** (`TestIntegration` class)
  - End-to-end user workflows
  - Cross-module integration

- **Chart Integration Tests** (`TestChartIntegration` class)
  - Chart data consistency with history
  - Performance testing

#### API Tests
- **Chart API Tests** (`TestChartAPI` class)
  - Endpoint accessibility
  - Response structure validation
  - Data format verification

## Running Tests

### Prerequisites

Install development dependencies:
```bash
make install-dev
# or
pip install -r requirements-dev.txt
```

### Basic Test Commands

#### Using Makefile (Recommended)
```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run specific test files
make test-app
make test-chart

# Run tests with coverage
make test-cov

# Run tests quickly (no coverage)
make test-fast

# Run tests with debug output
make test-debug
```

#### Using pytest directly
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_app.py -v

# Run specific test class
python -m pytest tests/test_app.py::TestAuthentication -v

# Run specific test method
python -m pytest tests/test_app.py::TestAuthentication::test_register_user_success -v

# Run tests with markers
python -m pytest tests/ -m "not integration" -v  # Unit tests only
python -m pytest tests/ -m "integration" -v      # Integration tests only
```

#### Using the test runner script
```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type app
python run_tests.py --type chart

# Run with coverage
python run_tests.py --type coverage

# Run in watch mode
python run_tests.py --watch

# Generate HTML report
python run_tests.py --html
```

### Test Markers

The tests use pytest markers for categorization:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.chart` - Chart functionality tests

### Coverage Reports

Generate coverage reports:
```bash
# HTML coverage report
make test-cov

# View coverage in browser
open htmlcov/index.html
```

## Test Configuration

### pytest.ini
The `pytest.ini` file configures:
- Test discovery patterns
- Output formatting
- Coverage settings
- Custom markers

### Fixtures

The tests use several pytest fixtures:

- **`temp_data_dir`** - Creates temporary directory for test data
- **`auth_manager`** - Provides AuthManager instance with test data directory
- **`data_manager`** - Provides DataManager instance with test data directory
- **`ai_engine`** - Provides AIRecommendationEngine instance
- **`app_url`** - Base URL for API tests
- **`test_user`** - Test user for chart data
- **`sample_chart_data`** - Sample chart data for testing

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure
```python
import pytest

class TestNewFeature:
    """Test new feature functionality"""
    
    def test_feature_works(self, fixture_name):
        """Test that the feature works correctly"""
        # Arrange
        expected = "expected result"
        
        # Act
        result = function_to_test()
        
        # Assert
        assert result == expected
    
    @pytest.mark.integration
    def test_feature_integration(self):
        """Test feature integration with other components"""
        # Integration test code
        pass
```

### Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern** (Arrange, Act, Assert)
3. **Use appropriate fixtures** for setup and teardown
4. **Mark tests appropriately** with pytest markers
5. **Test both success and failure cases**
6. **Use meaningful assertions** with clear error messages
7. **Keep tests independent** - each test should be able to run in isolation

## Continuous Integration

The tests are configured to run in CI/CD pipelines:

```bash
# Run all CI checks
make ci

# Generate XML report for CI
make test-xml
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you're running tests from the project root
2. **Missing dependencies**: Run `make install-dev` to install all test dependencies
3. **Flask app not available**: Some tests skip if Flask app can't be imported
4. **Connection errors**: Chart tests require the app to be running on localhost:5001

### Debug Mode
```bash
# Run tests with debug output
make test-debug

# Run specific test with debug
python -m pytest tests/test_app.py::TestAuthentication::test_register_user_success -v -s
```

### Test Isolation
Each test uses temporary data directories to ensure isolation. The fixtures handle cleanup automatically.

## Performance

- **Unit tests**: Should run in under 5 seconds
- **Integration tests**: May take longer due to API calls
- **Chart tests**: Require running application

Use `make test-fast` for quick feedback during development. 