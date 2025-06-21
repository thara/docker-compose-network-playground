#!/bin/bash

set -e

echo "🛑 Stopping Docker Compose Network Playground"
echo "============================================="

# Function to stop services
stop_services() {
    echo "🔻 Stopping services..."
    
    echo "  Stopping service3..."
    docker-compose -f docker-compose.service3.yml down
    
    echo "  Stopping service2..."
    docker-compose -f docker-compose.service2.yml down
    
    echo "  Stopping service1..."
    docker-compose -f docker-compose.service1.yml down
    
    echo "✅ All services stopped"
}

# Function to stop networks
stop_networks() {
    echo "🌐 Stopping networks..."
    docker-compose -f docker-compose.networks.yml down
    echo "✅ Networks removed"
}

# Function to clean up (optional)
cleanup() {
    if [ "$1" = "--clean" ]; then
        echo "🧹 Cleaning up..."
        
        echo "  Removing unused images..."
        docker image prune -f
        
        echo "  Removing unused networks..."
        docker network prune -f
        
        echo "✅ Cleanup completed"
    fi
}

# Main execution
main() {
    stop_services
    stop_networks
    cleanup "$1"
    
    echo ""
    echo "✅ Docker Compose Network Playground stopped"
    
    if [ "$1" != "--clean" ]; then
        echo "💡 Use './stop.sh --clean' to also remove unused Docker resources"
    fi
}

main "$@"