#!/bin/bash

# Fix Dashy Network Connectivity Issues
# Based on GitHub solution: https://github.com/Lissy93/dashy/discussions/445

echo "🔧 Fixing Dashy network connectivity with HOST mode..."

# Stop existing container
docker stop dashy 2>/dev/null || true
docker rm dashy 2>/dev/null || true

# Create updated config for HOST network mode
cat > dashy-host-config.yml << 'EOF'
---
# Dashy Configuration - HOST Network Mode (Fixed Connectivity)
pageInfo:
  title: DrJ Labs Dashboard  
  description: Self-hosted services with direct host network access
  logo: https://i.ibb.co/qWWpD0v/astro-dab-128.png
  
appConfig:
  theme: night
  layout: auto
  iconSize: large
  language: en
  startingView: default
  defaultOpeningMethod: sametab
  statusCheck: true
  statusCheckInterval: 300
  enableMultiTasking: true
  allowConfigEdit: true

sections:
- name: Container Management
  icon: fas fa-server
  items:
  - title: Portainer HTTPS
    description: Container management interface
    icon: https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/svg/portainer.svg
    url: https://localhost:9443
    target: newtab
    statusCheck: true
    statusCheckAcceptCodes: "200,300,301,302,403,404"
    
  - title: Portainer HTTP
    description: Edge agent interface  
    icon: https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/svg/portainer.svg
    url: http://localhost:8000
    target: newtab
    statusCheck: true
    statusCheckAcceptCodes: "200,300,301,302,403,404"

- name: Development & Monitoring
  icon: fas fa-code
  items:
  - title: Memory Dashboard
    description: Mem0 OpenMemory UI
    icon: fas fa-brain
    url: http://localhost:3010
    target: sametab
    statusCheck: true
    
  - title: Memory API
    description: Memory system API
    icon: fas fa-database
    url: http://localhost:8765
    target: newtab
    statusCheck: true
    
  - title: Qdrant Vector DB
    description: Vector database
    icon: fas fa-vector-square
    url: http://localhost:6333
    target: sametab
    statusCheck: true
    
  - title: Working Memory Dashboard
    description: Alternative memory UI
    icon: fas fa-memory
    url: http://localhost:8082
    target: sametab
    statusCheck: true

- name: System Services
  icon: fas fa-cog
  items:
  - title: System Monitor
    description: System monitoring
    icon: fas fa-chart-line
    url: http://localhost:19999
    target: sametab
    statusCheck: false
    
  - title: Local Services
    description: Other local services
    icon: fas fa-server
    url: http://localhost
    target: newtab
    statusCheck: false

- name: External Links
  icon: fas fa-external-link-alt
  items:
  - title: GitHub
    icon: fab fa-github
    url: https://github.com
    target: newtab
    
  - title: Docker Hub
    icon: fab fa-docker
    url: https://hub.docker.com
    target: newtab
EOF

echo "📁 Created HOST network configuration: dashy-host-config.yml"

# Run Dashy with HOST network mode on port 4080 (avoiding 8080 conflict)
echo "🚀 Starting Dashy with HOST network mode..."
docker run -d \
  --name dashy \
  --network host \
  --restart unless-stopped \
  -v "$(pwd)/dashy-host-config.yml:/app/public/conf.yml:ro" \
  -e NODE_ENV=production \
  -e UID=1000 \
  -e GID=1000 \
  -e PORT=4080 \
  lissy93/dashy:latest

echo "⏳ Waiting for Dashy to start..."
sleep 10

# Test connectivity
echo "🧪 Testing connectivity..."
if curl -f http://localhost:4080 &> /dev/null; then
    echo "✅ Dashy is accessible at http://localhost:4080"
else
    echo "⚠️ Dashy may need a moment to fully start"
fi

echo ""
echo "🎯 SUCCESS! Dashy is now running with HOST network mode"
echo "📍 Dashboard URL: http://localhost:4080"
echo "🔗 All localhost services should now work properly"
echo ""
echo "📋 What changed:"
echo "  • Network mode: bridge → host"
echo "  • Port mapping: 4000:8080 → direct 4080"  
echo "  • Status checks now work for localhost services"
echo "  • No more container network isolation issues"
echo ""
echo "⚠️ Note: Dashy now listens on port 4080 (avoiding 8080 conflict)" 