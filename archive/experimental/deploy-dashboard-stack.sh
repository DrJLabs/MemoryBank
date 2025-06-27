#!/bin/bash

# Dashboard Stack Deployment Script
# Fixes Dashy integration issues with Portainer and other services

set -e

echo "🚀 Deploying Dashboard Stack with Proxy Solutions..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_warning "This script should not be run as root for security reasons"
fi

# Check Docker availability
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    exit 1
fi

print_status "Docker is available and running"

# Create dashboard directory structure
DASHBOARD_DIR="$HOME/dashboard-stack"
mkdir -p "$DASHBOARD_DIR"
cd "$DASHBOARD_DIR"

print_status "Setting up dashboard in: $DASHBOARD_DIR"

# Copy configuration files
cp ../dashy-config-updated.yml ./dashy-config.yml
cp ../nginx.conf ./nginx.conf
cp ../portainer-proxy.conf ./portainer-proxy.conf
cp ../docker-compose-dashboard.yml ./docker-compose.yml

print_status "Configuration files copied"

# Update Dashy configuration in running container
print_status "Updating Dashy configuration..."
docker cp ./dashy-config.yml dashy:/app/public/conf.yml

# Test current services
print_status "Testing current services..."

# Test Dashy
if curl -f http://localhost:4000 &> /dev/null; then
    print_success "✅ Dashy is accessible at http://localhost:4000"
else
    print_warning "⚠️ Dashy may not be accessible"
fi

# Test Portainer HTTPS
if curl -k -f https://localhost:9443 &> /dev/null; then
    print_success "✅ Portainer HTTPS is accessible at https://localhost:9443"
else
    print_warning "⚠️ Portainer HTTPS may not be accessible"
fi

# Test Portainer HTTP
if curl -f http://localhost:8000 &> /dev/null; then
    print_success "✅ Portainer HTTP is accessible at http://localhost:8000"
else
    print_warning "⚠️ Portainer HTTP may not be accessible"
fi

# Test Memory services
if curl -f http://localhost:3010 &> /dev/null; then
    print_success "✅ Memory Dashboard is accessible at http://localhost:3010"
else
    print_warning "⚠️ Memory Dashboard may not be accessible"
fi

if curl -f http://localhost:8765 &> /dev/null; then
    print_success "✅ Memory API is accessible at http://localhost:8765"
else
    print_warning "⚠️ Memory API may not be accessible"
fi

# Deploy proxy services (optional)
read -p "Deploy proxy services to fix CORS/iframe issues? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Deploying proxy services..."
    
    # Stop any existing proxy services
    docker-compose down 2>/dev/null || true
    
    # Start new proxy services
    docker-compose up -d nginx-proxy portainer-proxy
    
    print_success "Proxy services deployed!"
    print_status "Available proxy endpoints:"
    echo "  - Dashboard Proxy: http://localhost:8080 (CORS-enabled Dashy)"
    echo "  - Portainer Proxy: http://localhost:9080 (iframe-friendly Portainer)"
    
    # Update Dashy config to use proxy URLs
    print_status "Updating Dashy to use proxy URLs..."
    docker cp ./dashy-config.yml dashy:/app/public/conf.yml
    docker restart dashy
else
    print_status "Skipping proxy deployment"
fi

# Create helpful scripts
cat > quick-update-dashy.sh << 'EOF'
#!/bin/bash
# Quick script to update Dashy configuration
echo "Updating Dashy configuration..."
docker cp ./dashy-config.yml dashy:/app/public/conf.yml
docker restart dashy
echo "Dashy configuration updated!"
EOF

chmod +x quick-update-dashy.sh

print_success "Dashboard stack deployment complete!"

echo ""
echo "📋 Summary:"
echo "  🌐 Main Dashboard: http://localhost:4000"
echo "  🐳 Portainer (HTTPS): https://localhost:9443 (may show security warnings)"
echo "  🐳 Portainer (HTTP): http://localhost:8000"
echo "  🧠 Memory Dashboard: http://localhost:3010"
echo "  📊 Memory API: http://localhost:8765"
echo ""
echo "🔧 Troubleshooting:"
echo "  • If services show security errors, use the proxy versions"
echo "  • For iframe issues, ensure target='sametab' in config"
echo "  • Check Docker logs: docker logs dashy"
echo "  • Update config: ./quick-update-dashy.sh"
echo ""
echo "🎯 Next steps:"
echo "  1. Open http://localhost:4000 in your browser"
echo "  2. Test service integrations"
echo "  3. Customize dashy-config.yml as needed"
echo "  4. Run ./quick-update-dashy.sh after config changes"

print_success "All done! 🎉" 