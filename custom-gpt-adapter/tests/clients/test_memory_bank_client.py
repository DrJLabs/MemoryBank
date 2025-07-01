import pytest
import httpx
from httpx import Request, ConnectError
from pybreaker import CircuitBreakerError

from app.clients.memory_bank_client import MemoryBankClient
from app.core.config import settings

@pytest.fixture
def memory_bank_client():
    # Ensure client is created with a base URL for testing
    settings.MEMORY_BANK_API_URL = "http://test-memory-bank"
    client = MemoryBankClient()
    # Reset the circuit breaker before each test
    client.memory_breaker.reset()
    return client

@pytest.mark.asyncio
async def test_search_memories_success(memory_bank_client: MemoryBankClient, httpx_mock):
    """Test successful memory search."""
    mock_response = {"results": [{"id": "123", "content": "test memory"}]}
    httpx_mock.add_response(url=f"{settings.MEMORY_BANK_API_URL}/v1/memories/search/", json=mock_response, status_code=200)
    response = await memory_bank_client.search_memories(query="test")
    assert response == mock_response

@pytest.mark.asyncio
async def test_search_memories_http_error(memory_bank_client: MemoryBankClient, httpx_mock):
    """Test that an HTTP error raises an exception."""
    httpx_mock.add_response(url=f"{settings.MEMORY_BANK_API_URL}/v1/memories/search/", status_code=500)
    with pytest.raises(httpx.HTTPStatusError):
        await memory_bank_client.search_memories(query="test")

@pytest.mark.asyncio
async def test_create_memory_network_error(memory_bank_client: MemoryBankClient, httpx_mock):
    """Test that a network error (e.g., timeout) is handled."""
    def raise_connect_error(request: Request):
        raise ConnectError("Connection failed", request=request)

    httpx_mock.add_callback(raise_connect_error)

    with pytest.raises(ConnectError):
        await memory_bank_client.create_memory(content="new memory", metadata={})

@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_failures(memory_bank_client: MemoryBankClient, httpx_mock):
    """Test that the circuit breaker opens after multiple failures."""
    httpx_mock.add_response(status_code=503) # Service Unavailable

    # Fail 5 times to trip the breaker
    for _ in range(5):
        with pytest.raises(httpx.HTTPStatusError):
            await memory_bank_client.search_memories(query="test")
    assert memory_bank_client.memory_breaker.current_state == "open"
    # The 6th call should immediately fail with CircuitBreakerError
    with pytest.raises(CircuitBreakerError):
        await memory_bank_client.search_memories(query="test")

@pytest.mark.asyncio
async def test_circuit_breaker_resets_after_timeout(memory_bank_client: MemoryBankClient, httpx_mock, mocker):
    """Test that the circuit breaker resets after the timeout."""
    # Mock time to control the breaker's reset
    mock_time = mocker.patch("time.time")
    
    httpx_mock.add_response(status_code=500)

    # Trip the breaker
    for _ in range(5):
        with pytest.raises(httpx.HTTPStatusError):
            await memory_bank_client.create_memory("fail", {})
    assert memory_bank_client.memory_breaker.is_open
    # Move time forward past the reset timeout (60s)
    mock_time.return_value += 61
    # The breaker should now be in "half-open" state, and the next call will try again
    httpx_mock.add_response(status_code=200, json={"id": "1", "content": "success"})
    response = await memory_bank_client.create_memory("succeed", {})
    assert response is not None
    assert memory_bank_client.memory_breaker.is_closed 