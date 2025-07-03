"""
Pytest configuration and fixtures for MemoryBank test suite.
Provides ephemeral Postgres + pgvector database for test isolation.
"""

import os
import pytest
import psycopg
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def postgres_container():
    """
    Session-scoped ephemeral Postgres container with pgvector extension.
    Automatically starts before tests and tears down after completion.
    """
    with PostgresContainer(
        image="pgvector/pgvector:pg16",
        username="test_user",
        password="test_password",
        dbname="memorybank_test",
        port=5432
    ) as postgres:
        # Wait for container to be ready
        postgres.get_connection_url()
        
        # Enable pgvector extension
        engine = create_engine(postgres.get_connection_url())
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()

        yield postgres


@pytest.fixture(scope="function")
def test_db_url(postgres_container):
    """
    Function-scoped database URL that provides a clean database for each test.
    Uses transactions to ensure complete isolation between tests.
    """
    base_url = postgres_container.get_connection_url()

    # Create a unique database name for this test
    import uuid
    import re
    test_db_name = f"test_{uuid.uuid4().hex[:8]}"
    
    # Validate database name to prevent SQL injection (alphanumeric + underscore only)
    if not re.match(r'^[a-zA-Z0-9_]+$', test_db_name):
        raise ValueError(f"Invalid database name: {test_db_name}")

    # Connect to default database to create test database
    engine = create_engine(base_url)
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))  # End any existing transaction
        # Note: PostgreSQL doesn't support parameterized database names in DDL
        # But we've validated the name above to prevent injection
        conn.execute(text(f"CREATE DATABASE {test_db_name}"))

    # Build connection URL for the test database
    test_url = base_url.replace("/memorybank_test", f"/{test_db_name}")

    # Enable pgvector in the test database
    test_engine = create_engine(test_url)
    with test_engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    yield test_url

    # Cleanup: Drop the test database
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        # Terminate active connections to the test database
        conn.execute(text(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{test_db_name}' AND pid <> pg_backend_pid()
        """))
        conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))


@pytest.fixture(scope="function")
def test_db_session(test_db_url):
    """
    Provides a SQLAlchemy session connected to the ephemeral test database.
    Automatically rolls back transactions after each test.
    """
    engine = create_engine(test_db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_db_connection(test_db_url):
    """
    Provides a raw psycopg connection for tests that need direct database access.
    """
    conn = psycopg.connect(test_db_url, autocommit=True)

    try:
        yield conn
    finally:
        if not conn.closed:
            conn.close()


# Environment variable override for CI/external testing
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Automatically sets up test environment variables.
    Can be overridden by setting EPHEMERAL_POSTGRES_URI environment variable.
    """
    if not os.getenv("EPHEMERAL_POSTGRES_URI"):
        # This will be set by the postgres_container fixture
        pass

    # Ensure we're in test mode
    os.environ["TESTING"] = "1"
    os.environ["LOG_LEVEL"] = "DEBUG"

    yield

    # Cleanup
    os.environ.pop("TESTING", None)
    os.environ.pop("LOG_LEVEL", None)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Mark slow tests (tests that take >5 seconds)
        if "slow" in item.name or "performance" in str(item.fspath):
            item.add_marker(pytest.mark.slow) 