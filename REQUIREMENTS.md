# Docker Compose Network Playground Requirements

## Project Overview
Create a Docker Compose network demonstration with multiple services that can communicate through public endpoints while maintaining private endpoints that are inaccessible to other services.

## Architecture

### Network Topology
- **Public Network**: Shared network for inter-service communication (`public_network`)
- **Private Networks**: Individual private networks for each service's internal endpoints (`service1_private`, `service2_private`, `service3_private`)

### Dual-Container Architecture
Each service is implemented as **two separate containers**:

1. **Public Container**: Handles public endpoints, connected to `public_network`
2. **Private Container**: Handles private endpoints, connected to service-specific private network only

### Components
1. **Network Configuration File** (`docker-compose.networks.yml`)
   - Defines shared public network
   - Manages network isolation

2. **Service Files** (3 separate compose files with dual containers each)
   - `docker-compose.service1.yml` - Creates `service1` and `service1-private` containers
   - `docker-compose.service2.yml` - Creates `service2` and `service2-private` containers
   - `docker-compose.service3.yml` - Creates `service3` and `service3-private` containers

## Service Specifications

### Each Service Must Have:

#### Public Container Endpoints:

##### 1. Public Echo Endpoint
- **Path**: `/public/echo`
- **Method**: GET/POST
- **Container**: Public container only
- **Functionality**: Echo service that returns request data with service identifier
- **Access**: Available to all services on the public network

##### 2. Health Check Endpoint
- **Path**: `/health`
- **Method**: GET
- **Container**: Public container only
- **Functionality**: Returns service status
- **Access**: Public

##### 3. Inter-Service Communication
- **Path**: `/call-others`
- **Method**: GET
- **Container**: Public container only
- **Functionality**: 
  - Calls public endpoints of other services (succeeds)
  - Attempts to call private endpoints at `service-name-private:8081` (fails with network error)
  - Logs all results

#### Private Container Endpoints:

##### 4. Private Information Endpoint
- **Path**: `/private/info`
- **Method**: GET
- **Container**: Private container only
- **Functionality**: Returns sensitive service information
- **Access**: Only accessible within the service's private network (truly isolated)

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
- **Language**: Python with Flask
- **Framework**: Single Flask app with APP_MODE environment variable
- **Container Modes**: 
  - `APP_MODE=public`: Serves only public endpoints
  - `APP_MODE=private`: Serves only private endpoints
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
  # Public container
  service_name:
    build: ./service_name
    container_name: service_name
    networks:
      - public_network
      - service_name_private  # Can access own private container
    environment:
      - SERVICE_NAME=service_name
      - PUBLIC_PORT=8080
      - PRIVATE_PORT=8081
      - APP_MODE=public
    ports:
      - "host_port:8080"  # Public port mapping

  # Private container
  service_name-private:
    build: ./service_name
    container_name: service_name-private
    networks:
      - service_name_private
    environment:
      - SERVICE_NAME=service_name
      - PUBLIC_PORT=8080
      - PRIVATE_PORT=8081
      - APP_MODE=private
    # No port mapping - internal only
```

### Volume Mounts
- Mount service code
- Mount logs directory for persistent logging

## Testing Requirements

### Functional Tests
1. Public containers can access other services' public endpoints ✅
2. Public containers can access their own private endpoints ✅
3. Public containers cannot access other services' private endpoints ❌ (network isolation)
4. Public containers return 404 for private endpoint requests ❌ (APP_MODE=public)
5. Private containers serve only private endpoints ✅
6. Health checks work for all public containers ✅
7. Inter-service communication logs are generated ✅

### Network Isolation Tests
1. Verify public containers cannot reach private containers of other services ❌
2. Verify all public containers can communicate on public network ✅
3. Verify private containers are isolated to their own networks ✅
4. Test DNS resolution: `service-name` (public) vs `service-name-private` (private) ✅

### Expected Results
- **Public-to-public communication**: SUCCESS ✅
- **Same-service private access**: SUCCESS ✅ (service1 → service1-private)
- **Cross-service private access**: NETWORK ERROR ❌ (service1 → service2-private)
- **Private endpoint on public container**: 404 ERROR ❌ (APP_MODE restriction)

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
1. Check all containers are running (should see 6 total: 3 public + 3 private)
2. Test public endpoints from host (ports 8001-8003)
3. Execute inter-service communication tests (`/call-others`)
4. Verify network isolation (private endpoints return connection errors)
5. Test APP_MODE restrictions (private endpoints on public containers return 404)

## Success Criteria
- **6 containers running**: 3 public + 3 private containers ✅
- **Public endpoints accessible** between services ✅
- **Private endpoints network isolated** (connection errors) ✅
- **APP_MODE enforcement** (404 errors for wrong endpoint types) ✅
- **Comprehensive logging** of all communication attempts ✅
- **True Docker network isolation** demonstrated ✅

## Implementation Status
✅ **COMPLETED** - True network isolation achieved through dual-container architecture with APP_MODE environment variable controlling endpoint availability.