import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from pybreaker import CircuitBreakerError

from app.clients.memory_bank_client import MemoryBankClient

@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_failures():
    client = MemoryBankClient()
    
    with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=MagicMock(status_code=500))
        
        for _ in range(5):
            with pytest.raises(httpx.HTTPStatusError):
                await client.search_memories("test query")
                
        with pytest.raises(CircuitBreakerError):
            await client.search_memories("test query") 