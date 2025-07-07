#!/bin/bash
# Custom GPT Adapter Service - Production Deployment Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
ENV_FILE="${PROJECT_ROOT}/.env.production"
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker/docker-compose.yml"
DOCKER_COMPOSE_PROD_FILE="${PROJECT_ROOT}/docker/docker-compose.prod.yml"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check for Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check for environment file
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Production environment file not found: $ENV_FILE"
        log_info "Please copy .env.production.template to .env.production and configure it"
        exit 1
    fi
    
    # Validate environment variables
    source "$ENV_FILE"
    
    required_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "MEMORY_BANK_API_URL"
        "MEMORY_BANK_API_KEY"
        "JWT_SECRET_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    log_info "Prerequisites check passed"
}

backup_database() {
    log_info "Creating database backup..."
    
    # Extract database credentials from DATABASE_URL
    if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
        DB_USER="${BASH_REMATCH[1]}"
        DB_PASS="${BASH_REMATCH[2]}"
        DB_HOST="${BASH_REMATCH[3]}"
        DB_PORT="${BASH_REMATCH[4]}"
        DB_NAME="${BASH_REMATCH[5]}"
        
        BACKUP_FILE="${PROJECT_ROOT}/backups/custom_gpt_adapter_$(date +%Y%m%d_%H%M%S).sql"
        mkdir -p "${PROJECT_ROOT}/backups"
        
        PGPASSWORD="$DB_PASS" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            log_info "Database backup created: $BACKUP_FILE"
        else
            log_warn "Database backup failed, but continuing with deployment"
        fi
    else
        log_warn "Could not parse DATABASE_URL for backup"
    fi
}

run_migrations() {
    log_info "Running database migrations..."
    
    cd "$PROJECT_ROOT"
    docker run --rm \
        --env-file "$ENV_FILE" \
        -v "${PROJECT_ROOT}:/app" \
        -w /app \
        custom-gpt-adapter-api:latest \
        alembic upgrade head
    
    if [ $? -eq 0 ]; then
        log_info "Migrations completed successfully"
    else
        log_error "Migration failed"
        exit 1
    fi
}

deploy_services() {
    log_info "Deploying services..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images
    log_info "Pulling latest images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" pull
    
    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" down
    
    # Start services
    log_info "Starting services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check service health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "API service is healthy"
    else
        log_error "API service health check failed"
        docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" logs api
        exit 1
    fi
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check API endpoint
    API_VERSION=$(curl -s http://localhost:8000/ | jq -r '.message' || echo "Failed")
    log_info "API Response: $API_VERSION"
    
    # Check metrics endpoint
    if curl -f http://localhost:8000/metrics > /dev/null 2>&1; then
        log_info "Metrics endpoint is accessible"
    else
        log_warn "Metrics endpoint check failed"
    fi
    
    # Check worker status
    WORKER_COUNT=$(docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" ps -q worker | wc -l)
    log_info "Celery workers running: $WORKER_COUNT"
    
    log_info "Deployment verification completed"
}

post_deployment_tasks() {
    log_info "Running post-deployment tasks..."
    
    # Clear Redis cache if needed
    log_info "Clearing Redis cache..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" -f "$DOCKER_COMPOSE_PROD_FILE" exec -T redis redis-cli FLUSHDB
    
    # Warm up the service
    log_info "Warming up the service..."
    curl -s http://localhost:8000/health > /dev/null
    
    log_info "Post-deployment tasks completed"
}

main() {
    log_info "Starting Custom GPT Adapter Service deployment..."
    
    check_prerequisites
    backup_database
    run_migrations
    deploy_services
    verify_deployment
    post_deployment_tasks
    
    log_info "Deployment completed successfully!"
    log_info "Monitor the services with: docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE logs -f"
}

# Run main function
main "$@" 