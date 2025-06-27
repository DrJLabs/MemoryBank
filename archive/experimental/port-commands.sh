#!/bin/bash
# Convenient Port Management Commands
# Add these to your ~/.bashrc or run this script to enable shortcuts

echo "🔧 Adding Port Management Aliases..."

# Add aliases to current session
alias port-scan='python3 /home/drj/*C-System/Memory-C*/mem0/openmemory/port-manager.py scan'
alias port-status='python3 /home/drj/*C-System/Memory-C*/mem0/openmemory/port-manager.py status'
alias port-find='python3 /home/drj/*C-System/Memory-C*/mem0/openmemory/port-manager.py find'
alias port-register='python3 /home/drj/*C-System/Memory-C*/mem0/openmemory/port-manager.py register'
alias port-unregister='python3 /home/drj/*C-System/Memory-C*/mem0/openmemory/port-manager.py unregister'
alias memory-dashboard='python3 /home/drj/*C-System/Memory-C*/mem0/openmemory/working-memory-dashboard.py'

echo "✅ Port Management Aliases Added:"
echo "   port-scan           - Scan and update port registry"
echo "   port-status         - Show current port status"
echo "   port-find [port]    - Find available port (optionally preferred)"
echo "   port-register <name> <port> [desc] - Register service"
echo "   port-unregister <name> - Unregister service" 
echo "   memory-dashboard    - Start memory dashboard with auto port"

echo ""
echo "🎯 Example Usage:"
echo "   port-scan                                    # Update port registry"
echo "   port-find 8080                             # Find port (prefer 8080)"
echo "   port-register myapp 3000 'My Application'   # Register service"
echo "   memory-dashboard                            # Start memory UI"

echo ""
echo "📝 To make permanent, add to ~/.bashrc:"
echo "   echo 'source /home/drj/*C-System/Memory-C*/mem0/openmemory/port-commands.sh' >> ~/.bashrc" 