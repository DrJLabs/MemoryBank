# 🧪 AI-Friendly Testing Suite for Memory-C*

## Overview

This testing suite implements **AI-powered testing** with **self-correction capabilities**, **adaptive behavior**, and **intelligent failure recovery** for the Memory-C* system. It goes beyond traditional testing by incorporating:

- ✨ **Auto-correction mechanisms** for flaky tests
- 🧠 **Intelligent mocking** based on test context  
- 📊 **Confidence scoring** for test quality metrics
- 🎲 **Property-based testing** for edge case discovery
- ⚡ **Adaptive timeouts** based on historical performance
- 🔄 **Self-healing assertions** that adapt to expected changes

## Quick Start

### Run AI-Enhanced Tests
```bash
# Run all AI tests with auto-correction
python -m pytest tests/ai_memory_tests.py -v

# Run with specific AI configuration
AI_TEST_AUTO_CORRECTION=true AI_TEST_MAX_RETRIES=5 python -m pytest tests/ai_memory_tests.py

# Run property-based tests only
python -m pytest tests/ai_memory_tests.py -k "property" --hypothesis-show-statistics

# Run performance tests
python -m pytest tests/ai_memory_tests.py -k "performance" -m "not slow"
```

### Run Traditional Tests
```bash
# Existing test suite (unchanged)
python -m pytest tests/ -x mem0/ embedchain/
make test
```

## 🎯 Testing Architecture

### Multi-Layer Testing Pyramid
```
┌─────────────────────────────────────┐
│     E2E Tests (AI Integration)      │  ← Full system with AI monitoring
├─────────────────────────────────────┤
│      Integration Tests (Smart)      │  ← Component integration with mocks
├─────────────────────────────────────┤
│    Unit Tests (Self-Correcting)     │  ← Core logic with auto-correction
└─────────────────────────────────────┘
```

### Core Components

#### 1. **AI Testing Framework** (`tests/ai_testing_framework.py`)
- **`AITestFramework`**: Main testing orchestrator
- **`TestMetrics`**: Comprehensive test analysis
- **`AITestConfig`**: Configurable testing behavior
- **Auto-correction patterns** for common failures
- **Smart mocking** based on test context

#### 2. **Memory-C* Tests** (`tests/ai_memory_tests.py`)
- **Core functionality tests** with AI enhancements
- **Performance & stress testing** with adaptive timeouts
- **Integration tests** with intelligent mocking
- **Error handling** with auto-correction
- **Property-based testing** for edge cases

#### 3. **CI/CD Integration** (`.github/workflows/ai-testing-suite.yml`)
- **Intelligent test planning** based on code changes
- **Dynamic test matrix** adaptation
- **Comprehensive reporting** with AI insights
- **Security analysis** of testing framework
- **Performance benchmarking**

## 🤖 AI Testing Features

### 1. Auto-Correction Mechanisms
```python
@ai_test(config=AITestConfig(enable_auto_correction=True, max_retries=3))
def test_with_auto_correction():
    # Test will automatically retry with corrections for:
    # - ConnectionError → Mock HTTP client
    # - TimeoutError → Increase timeout
    # - KeyError → Add default values
    # - AttributeError → Mock missing methods
    pass
```

### 2. Smart Mocking
```python
@smart_mock_test(mock_patterns=["openai", "vector_db", "embedder"])
def test_with_intelligent_mocking(mock_openai, mock_vector_db, mock_embedder):
    # Automatically configured mocks based on test context
    pass
```

### 3. Property-Based Testing
```python
@property_test(strategy=MemoryTestStrategies.memory_content())
def test_property_based(content):
    # Discovers edge cases automatically using Hypothesis
    pass
```

### 4. Adaptive Configuration
```python
# Framework automatically adapts timeouts, retries, and behavior
# based on historical test performance and current context
```

## 📊 Test Metrics & Reporting

### Collected Metrics
- **Execution time** with performance trends
- **Memory usage** monitoring  
- **API call counts** for optimization
- **Success rates** and confidence scores
- **Auto-correction patterns** and frequency
- **Recommendation generation** for improvements

### Reports Generated
- **`tests/ai_test_report.json`**: Comprehensive test analysis
- **`tests/ai_test_insights.log`**: Detailed execution logs
- **Coverage reports**: HTML, XML, and terminal output
- **Performance benchmarks**: Historical trend analysis

## 🚀 CI/CD Integration

### GitHub Actions Workflow
The AI testing suite integrates with GitHub Actions to provide:

#### Intelligent Test Planning
- **Change detection**: Only runs relevant tests based on modified files
- **Dynamic matrix**: Adapts Python versions and test suites based on context
- **Performance optimization**: Caches dependencies and results

#### Multi-Stage Testing
1. **AI Framework Tests**: Core testing with auto-correction
2. **Integration Tests**: System interactions with smart mocking  
3. **Security Analysis**: Framework security assessment
4. **Performance Benchmarks**: Historical performance tracking

#### Comprehensive Reporting
- **GitHub Summaries**: Rich markdown reports with insights
- **PR Comments**: Automated test result posting
- **Artifact Collection**: Detailed reports and logs
- **Codecov Integration**: Coverage analysis and trends

### Manual Workflow Dispatch
```yaml
# Trigger manual testing with custom configuration
inputs:
  test_level: [unit, integration, all]
  enable_auto_correction: [true, false]  
  max_retries: [1-10]
```

## 🔧 Configuration

### Environment Variables
```bash
# AI Testing Configuration
export AI_TEST_AUTO_CORRECTION=true
export AI_TEST_MAX_RETRIES=3
export AI_TEST_MODE=ci
export OPENAI_API_KEY=test_key_for_ci

# Pytest Configuration  
export PYTEST_MARKERS="not slow"
export HYPOTHESIS_PROFILE=ci
```

### Test Markers
```bash
# Available pytest markers
pytest -m "ai_framework"      # AI framework tests
pytest -m "property"          # Property-based tests  
pytest -m "performance"       # Performance tests
pytest -m "auto_correction"   # Auto-correction tests
pytest -m "not slow"          # Exclude slow tests
```

## 🛠️ Development Workflow

### Adding New AI Tests
```python
from tests.ai_testing_framework import ai_test, AITestConfig

@ai_test(config=AITestConfig(enable_auto_correction=True))
def test_new_feature():
    """Test with AI enhancements"""
    # Your test code here
    return {"status": "success", "data": result}
```

### Property-Based Testing
```python
from tests.ai_testing_framework import property_test, MemoryTestStrategies

@property_test(strategy=MemoryTestStrategies.memory_content())
def test_memory_property(content):
    """Property-based test for memory operations"""
    # Hypothesis will generate various content inputs
    memory = Memory()
    result = memory.add(content, user_id="test")
    assert result is not None
```

### Performance Testing
```python
@ai_test(config=AITestConfig(adaptive_timeouts=True))
def test_performance_sensitive():
    """Test with adaptive timeout management"""
    # Framework automatically adjusts timeouts based on history
    pass
```

## 📈 Best Practices

### 1. Test Organization
- **Group related tests** in classes with descriptive names
- **Use descriptive test names** that explain the scenario
- **Apply appropriate markers** for test categorization
- **Include return values** for AI analysis and metrics

### 2. AI Framework Usage
- **Enable auto-correction** for flaky external dependencies
- **Use smart mocking** for complex integration scenarios  
- **Apply property-based testing** for input validation
- **Monitor metrics** to identify optimization opportunities

### 3. CI/CD Integration
- **Use change detection** to optimize test execution
- **Monitor performance trends** through CI metrics
- **Review AI insights** in GitHub Actions summaries
- **Update test configuration** based on CI feedback

## 🔍 Troubleshooting

### Common Issues

#### Auto-Correction Not Working
```bash
# Check configuration
echo $AI_TEST_AUTO_CORRECTION
export AI_TEST_AUTO_CORRECTION=true

# Verify framework loading
python -c "from tests.ai_testing_framework import AITestFramework; print('OK')"
```

#### Property Tests Failing
```bash
# Increase examples for better coverage
pytest -k "property" --hypothesis-max-examples=1000

# Show detailed statistics
pytest -k "property" --hypothesis-show-statistics
```

#### Performance Tests Timing Out
```bash
# Enable adaptive timeouts
export AI_TEST_ADAPTIVE_TIMEOUTS=true

# Check historical performance
cat tests/ai_test_report.json | jq '.performance'
```

### Debug Mode
```bash
# Enable detailed logging
export AI_TEST_DEBUG=true
python -m pytest tests/ai_memory_tests.py -v -s --tb=long
```

## 🎯 Future Enhancements

### Planned Features
- **Machine learning test optimization** based on historical data
- **Automated test generation** from code changes
- **Advanced failure pattern recognition**
- **Integration with more AI services**
- **Enhanced property strategy generation**

### Integration Opportunities  
- **Linear issue creation** from test failures
- **GitHub Projects** integration for test planning
- **Memory-C* insights** for test case generation
- **Automated documentation** from test behaviors

---

## 📚 Additional Resources

- **Hypothesis Documentation**: https://hypothesis.readthedocs.io/
- **Pytest Documentation**: https://docs.pytest.org/
- **Memory-C* Documentation**: Local project documentation
- **CI/CD Best Practices**: `.github/workflows/` examples

## 🤝 Contributing

When adding new tests:
1. **Follow the AI testing patterns** demonstrated in existing tests
2. **Use appropriate decorators** (`@ai_test`, `@property_test`, etc.)
3. **Include comprehensive docstrings** explaining test scenarios
4. **Return structured data** for AI analysis when possible
5. **Test your changes** with the full AI testing suite

---

**Happy Testing! 🧪✨** 

# MemoryBank Test Suite

This directory contains the test suite for MemoryBank, featuring ephemeral Postgres databases for complete test isolation.

## Quick Start

1. **Install test dependencies:**
   ```bash
   pip install -r dependencies/test.txt
   ```

2. **Run all tests:**
   ```bash
   pytest
   ```

3. **Run tests with coverage:**
   ```bash
   pytest --cov=app --cov-report=html
   ```

4. **Run tests in parallel:**
   ```bash
   pytest -n auto
   ```

## Ephemeral Postgres Setup

Our test suite uses **ephemeral Postgres containers** with pgvector extension for complete test isolation. Each test gets a fresh database, eliminating flaky tests caused by shared state.

### Key Features

- **Complete Isolation**: Each test gets its own database
- **pgvector Support**: Vector extension pre-installed and ready
- **Fast Setup**: Containers start automatically via testcontainers
- **Parallel Safe**: Tests can run concurrently without conflicts
- **CI Ready**: Works in GitHub Actions and other CI environments

### Available Fixtures

```python
def test_my_feature(test_db_url):
    """Use test_db_url for SQLAlchemy engine creation."""
    engine = create_engine(test_db_url)
    # Your test code here

def test_with_session(test_db_session):
    """Use test_db_session for SQLAlchemy ORM operations."""
    result = test_db_session.execute(text("SELECT 1"))
    # Your test code here

def test_raw_connection(test_db_connection):
    """Use test_db_connection for raw psycopg2 access."""
    with test_db_connection.cursor() as cur:
        cur.execute("SELECT 1")
        # Your test code here
```

### Test Organization

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_ephemeral_postgres.py  # Fixture validation tests
├── unit/                    # Unit tests
├── integration/             # Integration tests
└── performance/             # Performance tests (marked as slow)
```

### Test Markers

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests requiring database
- `@pytest.mark.slow` - Tests taking >5 seconds (skip with `-m "not slow"`)

### Running Specific Test Types

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run tests matching a pattern
pytest -k "test_database"
```

## Environment Variables

- `EPHEMERAL_POSTGRES_URI` - Override to use external Postgres instance
- `TESTING=1` - Automatically set during test runs
- `LOG_LEVEL=DEBUG` - Automatically set for detailed logging

## CI/CD Integration

The ephemeral Postgres setup works seamlessly in CI environments:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pip install -r dependencies/test.txt
    pytest --cov=app --cov-fail-under=80 -n auto
```

No additional services or setup required - testcontainers handles everything.

## Troubleshooting

### Docker Issues
If you encounter Docker-related errors:
1. Ensure Docker is running
2. Check Docker permissions for your user
3. Try running tests without parallelization: `pytest -n 0`

### Slow Test Startup
First test run may be slow while Docker pulls the pgvector image. Subsequent runs are much faster.

### Memory Usage
Each test creates a new database. For large test suites, consider:
- Using `@pytest.mark.slow` for expensive tests
- Running tests in smaller batches
- Increasing Docker memory limits

## Contributing

When adding new tests:

1. **Use appropriate fixtures** - `test_db_url`, `test_db_session`, or `test_db_connection`
2. **Add proper markers** - `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
3. **Test isolation** - Don't rely on data from other tests
4. **Clean up** - Fixtures handle cleanup automatically

## Next Steps

This setup enables Sprint-0 goals:
- ✅ **S0-EPH-PG**: Ephemeral Postgres fixture implemented
- 🔄 **S0-PAR**: Parallel testing ready (use `pytest -n auto`)
- 🔄 **S0-CG**: Coverage gate ready (use `--cov-fail-under=80`)
- 🔄 **S0-LIC**: License scanning (separate CI job) 