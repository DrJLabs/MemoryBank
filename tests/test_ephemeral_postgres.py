"""
Test ephemeral Postgres fixture functionality.
Validates that the test database is properly isolated and includes pgvector extension.
"""

import pytest
from sqlalchemy import create_engine, text


def test_postgres_container_is_running(postgres_container):
    """Test that the Postgres container is running and accessible."""
    connection_url = postgres_container.get_connection_url()
    assert connection_url is not None
    
    # Test direct connection
    engine = create_engine(connection_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        assert "PostgreSQL" in version


def test_pgvector_extension_available(test_db_connection):
    """Test that pgvector extension is available in the test database."""
    with test_db_connection.cursor() as cur:
        # Check if vector extension is installed
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM pg_extension WHERE extname = 'vector'
            )
        """)
        extension_exists = cur.fetchone()[0]
        assert extension_exists, "pgvector extension should be installed"
        
        # Test basic vector operations
        cur.execute("SELECT '[1,2,3]'::vector")
        vector_result = cur.fetchone()[0]
        assert vector_result is not None


def test_database_isolation_between_tests(test_db_url):
    """Test that each test gets a fresh, isolated database."""
    engine = create_engine(test_db_url)
    
    with engine.connect() as conn:
        # Create a test table
        conn.execute(text("""
            CREATE TABLE test_isolation (
                id SERIAL PRIMARY KEY,
                data TEXT
            )
        """))
        
        # Insert test data
        conn.execute(text("INSERT INTO test_isolation (data) VALUES ('test_data')"))
        conn.commit()
        
        # Verify data exists
        result = conn.execute(text("SELECT COUNT(*) FROM test_isolation"))
        count = result.fetchone()[0]
        assert count == 1


def test_database_isolation_second_test(test_db_url):
    """Second test to verify database isolation - should not see previous test's data."""
    engine = create_engine(test_db_url)
    
    with engine.connect() as conn:
        # This table should NOT exist from the previous test
        try:
            conn.execute(text("SELECT COUNT(*) FROM test_isolation"))
            # If we get here, isolation failed
            assert False, "Database isolation failed - previous test's table still exists"
        except Exception:
            # Expected - table should not exist
            pass
        
        # Create the same table name - should work without conflicts
        conn.execute(text("""
            CREATE TABLE test_isolation (
                id SERIAL PRIMARY KEY,
                different_data INTEGER
            )
        """))
        conn.commit()


def test_sqlalchemy_session_fixture(test_db_session):
    """Test that SQLAlchemy session fixture works correctly."""
    # This test uses the session fixture
    # Session should be connected and functional
    result = test_db_session.execute(text("SELECT 1 as test_value"))
    test_value = result.fetchone()[0]
    assert test_value == 1


@pytest.mark.slow
def test_concurrent_database_access(test_db_url):
    """Test that the database can handle concurrent connections."""
    import threading
    import time
    
    results = []
    errors = []
    
    def worker(worker_id):
        try:
            engine = create_engine(test_db_url)
            with engine.connect() as conn:
                # Simulate some work
                time.sleep(0.1)
                result = conn.execute(text("SELECT :worker_id as id"), {"worker_id": worker_id})
                worker_result = result.fetchone()[0]
                results.append(worker_result)
        except Exception as e:
            errors.append(str(e))
    
    # Start multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify results
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 5, f"Expected 5 results, got {len(results)}"
    assert sorted(results) == [0, 1, 2, 3, 4] 