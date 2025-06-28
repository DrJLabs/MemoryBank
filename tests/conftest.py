"""
Modern pytest configuration and fixtures for Memory-C* testing suite
Following 2024/2025 best practices for pytest fixture organization
"""

import os
import sys
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock

import pytest

# Graceful imports with fallbacks
try:
    import pytest_asyncio
    PYTEST_ASYNCIO_AVAILABLE = True
except ImportError:
    PYTEST_ASYNCIO_AVAILABLE = False
    # Create mock pytest_asyncio.fixture
    class MockAsyncIOFixture:
        @staticmethod
        def fixture(*args, **kwargs):
            return pytest.fixture(*args, **kwargs)
    pytest_asyncio = MockAsyncIOFixture()

try:
    from hypothesis import strategies as st
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Create mock strategies
    class MockStrategies:
        @staticmethod
        def text(*args, **kwargs):
            return lambda: "test_string"
        @staticmethod
        def characters(*args, **kwargs):
            return lambda: "abcd"
        @staticmethod
        def dictionaries(*args, **kwargs):
            return lambda: {}
        @staticmethod
        def integers(*args, **kwargs):
            return lambda: 42
        @staticmethod
        def floats(*args, **kwargs):
            return lambda: 0.5
        @staticmethod
        def booleans(*args, **kwargs):
            return lambda: True
        @staticmethod
        def one_of(*args, **kwargs):
            return lambda: args[0]() if args else "test"
    st = MockStrategies()

# Ensure the project root is in the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Try to import the AI testing framework
try:
    from tests.ai_testing_framework import AITestFramework, AITestConfig, TestMetrics
    AI_FRAMEWORK_AVAILABLE = True
except ImportError:
    AI_FRAMEWORK_AVAILABLE = False


# ==================== SESSION SCOPED FIXTURES ====================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def tmp_dir_factory():
    """Session-scoped temporary directory factory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def test_config():
    """Global test configuration."""
    return {
        "test_env": "pytest",
        "debug": True,
        "timeout": 30,
        "api_timeout": 5,
    }


# ==================== MODULE SCOPED FIXTURES ====================

@pytest.fixture(scope="module")
def memory_config():
    """Memory configuration for testing."""
    return {
        "llm": {
            "provider": "openai",
            "config": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1500,
            }
        },
        "embedder": {
            "provider": "openai",
            "config": {
                "model": "text-embedding-ada-002",
            }
        },
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "test_memory",
                "path": "/tmp/test_chroma_db",
            }
        }
    }


# ==================== FUNCTION SCOPED FIXTURES ====================

@pytest.fixture
def isolated_tmp_path(tmp_path):
    """Isolated temporary directory for each test."""
    # Change to tmp directory for test isolation
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_cwd)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    env_vars = {
        "OPENAI_API_KEY": "test_openai_key_12345",
        "ANTHROPIC_API_KEY": "test_anthropic_key_12345",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment without API keys for testing error cases."""
    env_vars_to_remove = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "GOOGLE_API_KEY",
        "AZURE_OPENAI_API_KEY",
    ]
    
    for var in env_vars_to_remove:
        monkeypatch.delenv(var, raising=False)


# ==================== AI TESTING FRAMEWORK FIXTURES ====================

if AI_FRAMEWORK_AVAILABLE:
    @pytest.fixture
    def ai_test_framework():
        """AI testing framework with modern configuration."""
        config = AITestConfig(
            enable_auto_correction=True,
            confidence_threshold=0.8,
            max_retries=3,
            adaptive_timeouts=True,
            smart_mocking=True,
            property_based_testing=True,
            timeout_base=5.0,
            timeout_multiplier=1.5,
        )
        return AITestFramework(config=config)

    @pytest.fixture
    def ai_test_config():
        """Modern AI test configuration."""
        return AITestConfig(
            enable_auto_correction=True,
            confidence_threshold=0.85,
            max_retries=3,
            adaptive_timeouts=True,
            smart_mocking=True,
            property_based_testing=True,
        )


# ==================== MOCK AND DATA FIXTURES ====================

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client with realistic responses."""
    from unittest.mock import Mock
    
    mock_client = Mock()
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    
    # Configure the mock chain
    mock_message.content = "Test response from OpenAI"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_memory_data():
    """Sample memory data for testing."""
    return {
        "memories": [
            {
                "id": "test_memory_1",
                "content": "User prefers coffee over tea",
                "metadata": {"user_id": "user_123", "category": "preference"},
                "created_at": "2024-01-01T10:00:00Z",
                "score": 0.95,
            },
            {
                "id": "test_memory_2", 
                "content": "User is working on a Python project",
                "metadata": {"user_id": "user_123", "category": "project"},
                "created_at": "2024-01-01T11:00:00Z",
                "score": 0.87,
            },
        ]
    }


@pytest.fixture
def sample_user_ids():
    """Sample user IDs for testing."""
    return [
        "user_123",
        "user_456", 
        "user_789",
        "test_user_001",
        "demo_user_002",
    ]


# ==================== HYPOTHESIS STRATEGIES ====================

@pytest.fixture
def memory_content_strategy():
    """Hypothesis strategy for generating memory content."""
    return st.text(
        alphabet=st.characters(whitelist_categories=['Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Zs']),
        min_size=10,
        max_size=500
    )


@pytest.fixture  
def user_id_strategy():
    """Hypothesis strategy for generating user IDs."""
    return st.text(
        alphabet=st.characters(whitelist_categories=['Lu', 'Ll', 'Nd', 'Pc']),
        min_size=5,
        max_size=50
    ).map(lambda x: f"user_{x}")


@pytest.fixture
def metadata_strategy():
    """Hypothesis strategy for generating metadata."""
    return st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(
            st.text(min_size=1, max_size=100),
            st.integers(min_value=0, max_value=1000),
            st.floats(min_value=0.0, max_value=1.0),
            st.booleans(),
        ),
        min_size=0,
        max_size=10
    )


# ==================== ASYNC FIXTURES ====================

@pytest_asyncio.fixture
async def async_memory_client(memory_config):
    """Async memory client for testing."""
    try:
        from mem0.memory.main import AsyncMemory
        client = AsyncMemory(config=memory_config)
        yield client
        # Cleanup
        await client.close() if hasattr(client, 'close') else None
    except ImportError:
        pytest.skip("AsyncMemory not available")


# ==================== PERFORMANCE AND MONITORING FIXTURES ====================

@pytest.fixture
def performance_monitor():
    """Monitor test performance and resource usage."""
    import time
    import psutil
    
    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss
    
    yield {
        "start_time": start_time,
        "start_memory": start_memory,
        "process": process,
    }
    
    end_time = time.time()
    end_memory = process.memory_info().rss
    
    duration = end_time - start_time
    memory_delta = end_memory - start_memory
    
    # Log performance metrics if test is slow
    if duration > 1.0:  # Log if test takes more than 1 second
        print(f"\n⚠️  Slow test detected: {duration:.2f}s, Memory delta: {memory_delta/1024/1024:.2f}MB")


# ==================== FIXTURE COMBINATIONS ====================

@pytest.fixture
def memory_test_setup(mock_env_vars, memory_config, mock_openai_client, monkeypatch):
    """Combined fixture for memory testing setup."""
    # We can't easily mock imports without pytest-mock, so we'll just provide the setup
    return {
        "env_vars": mock_env_vars,
        "config": memory_config,
        "openai_client": mock_openai_client,
    }


# ==================== AUTOUSE FIXTURES ====================

@pytest.fixture(autouse=True)
def setup_test_logging(caplog):
    """Automatically configure logging for all tests."""
    import logging
    
    # Set consistent log levels for testing
    logging.getLogger("mem0").setLevel(logging.DEBUG)
    logging.getLogger("tests").setLevel(logging.DEBUG)
    
    yield
    
    # Clear logs after each test
    caplog.clear()


@pytest.fixture(autouse=True) 
def create_reports_dir():
    """Ensure reports directory exists for coverage and test reports."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)


# ==================== ERROR HANDLING AND DEBUGGING ====================

@pytest.fixture
def debug_mode():
    """Enable debug mode for detailed test information."""
    return {
        "verbose": True,
        "capture": False,
        "trace": True,
    }


# ==================== PYTEST HOOKS (Configuration) ====================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers dynamically if needed
    config.addinivalue_line(
        "markers", "integration_slow: Integration tests that are slow"
    )
    
    # Configure hypothesis settings only if available
    if HYPOTHESIS_AVAILABLE:
        try:
            from hypothesis import settings
            settings.register_profile(
                "ci", 
                max_examples=50, 
                deadline=2000,
                suppress_health_check=[],
            )
            settings.register_profile(
                "dev",
                max_examples=10,
                deadline=1000,
            )
        except ImportError:
            pass  # Gracefully handle if hypothesis isn't available


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Auto-mark slow tests
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)
            
        # Auto-mark AI framework tests
        if "ai_" in item.name or "AI" in str(item.cls):
            item.add_marker(pytest.mark.ai_framework)
            
        # Auto-mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)


def pytest_runtest_setup(item):
    """Setup for each test run."""
    # Skip AI framework tests if not available
    if item.get_closest_marker("ai_framework") and not AI_FRAMEWORK_AVAILABLE:
        pytest.skip("AI Testing Framework not available")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom terminal summary information."""
    if hasattr(terminalreporter, 'stats'):
        passed = len(terminalreporter.stats.get('passed', []))
        failed = len(terminalreporter.stats.get('failed', []))
        
        terminalreporter.write_sep("=", "Memory-C* Test Suite Summary")
        terminalreporter.write_line(f"✅ Passed: {passed}")
        terminalreporter.write_line(f"❌ Failed: {failed}")
        
        if failed == 0 and passed > 0:
            terminalreporter.write_line("🎉 All tests passed! Great work!") 