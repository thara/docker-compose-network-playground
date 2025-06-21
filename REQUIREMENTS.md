# Docker Compose Network Playground Requirements

## Project Overview
Create a Docker Compose network demonstration with multiple services that can communicate through public endpoints while maintaining private endpoints that are inaccessible to other services.

## Architecture

### Network Topology
- **Public Network**: Shared network for inter-service communication
- **Private Networks**: Individual private networks for each service's internal endpoints

### Components
1. **Network Configuration File** (`docker-compose.networks.yml`)
   - Defines shared public network
   - Manages network isolation

2. **Service Files** (3 separate compose files)
   - `docker-compose.service1.yml`
   - `docker-compose.service2.yml`
   - `docker-compose.service3.yml`

## Service Specifications

### Each Service Must Have:

#### 1. Public Endpoint
- **Path**: `/public/echo`
- **Method**: GET/POST
- **Functionality**: Echo service that returns request data with service identifier
- **Access**: Available to all services on the public network

#### 2. Private Endpoint
- **Path**: `/private/info`
- **Method**: GET
- **Functionality**: Returns sensitive service information
- **Access**: Only accessible within the service's private network

#### 3. Health Check Endpoint
- **Path**: `/health`
- **Method**: GET
- **Functionality**: Returns service status
- **Access**: Public

#### 4. Inter-Service Communication
- **Path**: `/call-others`
- **Method**: GET
- **Functionality**: 
  - Calls public endpoints of other services
  - Attempts to call private endpoints (should fail)
  - Logs all results

## Network Configuration

### Public Network
- **Name**: `public_network`
- **Driver**: bridge
- **Purpose**: Enable communication between services' public endpoints

### Private Networks
- **Names**: `service1_private`, `service2_private`, `service3_private`
- **Driver**: bridge
- **Purpose**: Isolate private endpoints

## Service Implementation

### Technology Stack
- **Language**: Python or Node.js (lightweight web framework)
- **Framework**: Flask/FastAPI (Python) or Express (Node.js)
- **Logging**: Structured JSON logging

### API Response Format
```json
{
  "service": "service-name",
  "endpoint": "endpoint-path",
  "timestamp": "ISO-8601-timestamp",
  "data": {
    // endpoint-specific data
  }
}
```

### Logging Requirements
- Log all incoming requests
- Log all outgoing inter-service calls
- Log success/failure of private endpoint access attempts
- Use structured logging format

## Docker Configuration

### Service Configuration
```yaml
services:
  service_name:
    build: ./service_name
    networks:
      - public_network
      - service_name_private
    environment:
      - SERVICE_NAME=service_name
      - PUBLIC_PORT=8080
      - PRIVATE_PORT=8081
    ports:
      - "host_port:8080"  # Public port mapping
```

### Volume Mounts
- Mount service code
- Mount logs directory for persistent logging

## Testing Requirements

### Functional Tests
1. Each service's public endpoint is accessible from other services
2. Each service's private endpoint is NOT accessible from other services
3. Health checks work for all services
4. Inter-service communication logs are generated

### Network Isolation Tests
1. Verify services cannot access each other's private networks
2. Verify all services can communicate on public network
3. Test DNS resolution within networks

## Running Instructions

### Startup Sequence
1. Start network configuration: `docker-compose -f docker-compose.networks.yml up -d`
2. Start services: 
   ```bash
   docker-compose -f docker-compose.service1.yml up -d
   docker-compose -f docker-compose.service2.yml up -d
   docker-compose -f docker-compose.service3.yml up -d
   ```

### Verification Steps
1. Check all services are healthy
2. Test public endpoints from host
3. Execute inter-service communication tests
4. Verify network isolation

## Success Criteria
- All services running and healthy
- Public endpoints accessible between services
- Private endpoints properly isolated
- Comprehensive logging of all communication attempts
- Clear demonstration of Docker network isolation principles