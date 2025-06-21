#!/bin/bash

set -e

echo "🐳 Docker Compose Network Playground Startup Script"
echo "================================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to start networks
start_networks() {
    echo "🌐 Starting networks..."
    docker-compose -f docker-compose.networks.yml up -d
    echo "✅ Networks created"
}

# Function to start services
start_services() {
    echo "🚀 Starting services..."
    
    echo "  Starting service1..."
    docker-compose -f docker-compose.service1.yml up -d --build
    
    echo "  Starting service2..."
    docker-compose -f docker-compose.service2.yml up -d --build
    
    echo "  Starting service3..."
    docker-compose -f docker-compose.service3.yml up -d --build
    
    echo "✅ All services started"
}

# Function to wait for services to be healthy
wait_for_services() {
    echo "⏳ Waiting for services to be ready..."
    
    services=("service1:8001" "service2:8002" "service3:8003")
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        echo "  Checking $name on port $port..."
        
        max_attempts=30
        attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
                echo "  ✅ $name is ready"
                break
            fi
            
            attempt=$((attempt + 1))
            if [ $attempt -eq $max_attempts ]; then
                echo "  ❌ $name failed to start after $max_attempts attempts"
                exit 1
            fi
            
            sleep 2
        done
    done
    
    echo "✅ All services are ready"
}

# Function to show service status
show_status() {
    echo ""
    echo "📊 Service Status:"
    echo "=================="
    echo "Service 1: http://localhost:8001"
    echo "Service 2: http://localhost:8002" 
    echo "Service 3: http://localhost:8003"
    echo ""
    echo "Available endpoints:"
    echo "  /health - Health check"
    echo "  /public/echo - Public echo service"
    echo "  /call-others - Test inter-service communication"
    echo ""
    echo "🔍 To view logs: docker-compose -f docker-compose.service1.yml logs -f"
    echo "🛑 To stop all: ./stop.sh"
}

# Main execution
main() {
    check_docker
    start_networks
    start_services
    wait_for_services
    show_status
    
    echo ""
    echo "🎉 Docker Compose Network Playground is ready!"
    echo "Try: curl http://localhost:8001/call-others"
}

main "$@"