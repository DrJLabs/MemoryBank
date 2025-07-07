# Custom GPT Adapter Service - Deployment Guide

This guide covers the deployment and operational setup of the Custom GPT Adapter Service.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL client tools (for database operations)
- Python 3.12+ (for management scripts)
- Access to Memory Bank Service API
- SSL certificates (for production)

## Quick Start

### 1. Environment Configuration

Copy the production environment template and configure it:

```bash
cp .env.production.template .env.production
# Edit .env.production with your actual values
```

Key configuration values:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `MEMORY_BANK_API_URL`: Your Memory Bank Service API endpoint
- `MEMORY_BANK_API_KEY`: API key for Memory Bank Service
- `JWT_SECRET_KEY`: Strong random key for JWT tokens

### 2. Deploy the Service

Run the production deployment script:

```bash
./scripts/deploy/deploy-production.sh
```

This script will:
- Validate prerequisites
- Create database backup (if upgrading)
- Run database migrations
- Deploy all services via Docker Compose
- Verify deployment health

### 3. Create Your First Custom GPT Application

Register a Custom GPT application:

```bash
python scripts/manage/manage_custom_gpt_app.py create "My Custom GPT" --rate-limit "100/minute"
```

Save the generated `client_id` and `client_secret` securely!

### 4. Generate API Documentation

Create API documentation:

```bash
python scripts/manage/generate_api_docs.py --output-dir docs/api
```

View documentation locally:

```bash
python docs/api/serve.py
# Open http://localhost:8080 in your browser
```

## Service Management

### Application Management

List all applications:
```bash
python scripts/manage/manage_custom_gpt_app.py list
```

Update application:
```bash
python scripts/manage/manage_custom_gpt_app.py update <client_id> --rate-limit "200/minute"
```

Reset client secret:
```bash
python scripts/manage/manage_custom_gpt_app.py reset-secret <client_id>
```

View application statistics:
```bash
python scripts/manage/manage_custom_gpt_app.py stats <client_id>
```

### Service Operations

View logs:
```bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml logs -f
```

Restart services:
```bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml restart
```

Scale workers:
```bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d --scale worker=4
```

## Monitoring

### Grafana Dashboard

Access Grafana at `http://localhost:3000`
- Default username: `admin`
- Password: Set via `grafana_password` Docker secret

Import the pre-configured dashboard from `/monitoring/grafana-dashboard.json`

### Prometheus Metrics

Access raw metrics at `http://localhost:9090`

Key metrics to monitor:
- Request rate and latency
- Error rates
- Celery queue length
- Circuit breaker status

## Integration Testing

### Test OAuth Authentication

```bash
# Get access token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_SECRET"

# Use token for API call
curl -X POST http://localhost:8000/api/v1/search \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "test search"}'
```

### Load Testing

Create a load test script:

```python
# load_test.py
import asyncio
import httpx
import time

async def test_search(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/search",
        json={"query": "load test"},
        headers=headers
    )
    return response.status_code, response.elapsed.total_seconds()

async def run_load_test(base_url, token, concurrent_requests=10, total_requests=100):
    async with httpx.AsyncClient(base_url=base_url) as client:
        tasks = []
        for i in range(total_requests):
            if len(tasks) >= concurrent_requests:
                done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = list(tasks)
            
            task = asyncio.create_task(test_search(client, token))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
    
    return results

# Run the test
if __name__ == "__main__":
    TOKEN = "your-access-token"
    results = asyncio.run(run_load_test("http://localhost:8000", TOKEN))
    
    success_count = sum(1 for status, _ in results if status == 200)
    avg_time = sum(time for _, time in results) / len(results)
    
    print(f"Success rate: {success_count}/{len(results)}")
    print(f"Average response time: {avg_time:.3f}s")
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify DATABASE_URL is correct
   - Check PostgreSQL is running and accessible
   - Ensure database user has proper permissions

2. **Redis Connection Failed**
   - Verify REDIS_URL is correct
   - Check Redis is running
   - Test connection: `redis-cli -h <host> ping`

3. **Memory Bank Service Integration Failed**
   - Verify MEMORY_BANK_API_URL is correct
   - Check API key is valid
   - Test endpoint accessibility

4. **High Error Rates**
   - Check Grafana dashboard for error patterns
   - Review logs for specific errors
   - Verify rate limits aren't too restrictive

### Debug Mode

Enable debug logging:
```bash
# In .env.production
API_LOG_LEVEL=debug
ENABLE_DEBUG_MODE=true
```

### Rollback Procedure

If deployment fails:

1. Stop new services:
   ```bash
   docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml down
   ```

2. Restore database (if migrations were run):
   ```bash
   psql $DATABASE_URL < backups/custom_gpt_adapter_YYYYMMDD_HHMMSS.sql
   ```

3. Deploy previous version:
   ```bash
   docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d
   ```

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong JWT secret key
- [ ] Enable HTTPS for production
- [ ] Restrict database access
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Review rate limits
- [ ] Set up backup schedule

## Next Steps

1. Set up alerting in Grafana
2. Configure log aggregation
3. Create operational runbooks
4. Schedule security audit
5. Plan disaster recovery testing

For additional support, refer to the [API Documentation](./docs/api/) or contact the development team. 