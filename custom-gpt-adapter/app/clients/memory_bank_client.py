import httpx
from app.core.config import settings
from pybreaker import CircuitBreaker

# 5 failures in 300 seconds (5 minutes) opens the circuit
# Circuit will stay open for 60 seconds
memory_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

class MemoryBankClient:
    def __init__(self):
        self.base_url = settings.MEMORY_BANK_API_URL
        self.api_key = settings.MEMORY_BANK_API_KEY
        # Retry on 5xx errors up to 3 times with exponential backoff
        transport = httpx.AsyncHTTPTransport(retries=3)
        self.client = httpx.AsyncClient(base_url=self.base_url, transport=transport)

    @memory_breaker
    async def search_memories(self, query: str, limit: int = 10):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = await self.client.post(
            "/v1/memories/search/",
            json={"query": query, "limit": limit},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    @memory_breaker
    async def create_memory(self, content: str, metadata: dict):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = await self.client.post(
            "/v1/memories/",
            json={"content": content, "metadata": metadata},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

memory_bank_client = MemoryBankClient() 