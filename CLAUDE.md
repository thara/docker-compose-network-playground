# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Docker Compose network playground demonstrating inter-service communication with network isolation. The project consists of multiple Docker Compose files that create services with both public and private endpoints to showcase Docker networking concepts.

## Architecture

### Multi-Compose File Structure
- `docker-compose.networks.yml` - Defines only the shared `public_network`
- `docker-compose.service1.yml`, `docker-compose.service2.yml`, `docker-compose.service3.yml` - Individual service definitions with public and private containers, each creating its own private network

### Network Architecture
- **Public Network** (`public_network`): Shared bridge network for inter-service communication (external: true in service files)
- **Private Networks** (`service1_private`, `service2_private`, `service3_private`): Isolated networks created by each service file (no external: true)

### Service Design Pattern
Each service runs in **two separate containers**:

#### Public Container (e.g., `service1`)
- Connected to: `public_network` + `service1_private`
- Serves: `/public/echo`, `/health`, `/call-others`
- Port mapping: `8001:8080` (external access)
- Environment: `APP_MODE=public`
- Can access: Own private container (`service1-private`)

#### Private Container (e.g., `service1-private`)
- Connected to: `service1_private` network only
- Serves: `/private/info`
- No external port mapping (internal only)
- Environment: `APP_MODE=private`

### True Network Isolation
- **Same-service access**: ✅ Public containers can access their own private containers
- **Cross-service private access**: ❌ Public containers cannot access other services' private containers  
- **Private container isolation**: ❌ Private containers isolated to their own networks only
- **Inter-service communication**: Limited to public endpoints only

## Common Commands

### Starting the Environment
```bash
# Start networks first
docker-compose -f docker-compose.networks.yml up -d

# Start all services (each creates both public and private containers)
docker-compose -f docker-compose.service1.yml up -d
docker-compose -f docker-compose.service2.yml up -d
docker-compose -f docker-compose.service3.yml up -d
```

### Development and Testing
```bash
# View service logs
docker-compose -f docker-compose.service1.yml logs -f

# Test public endpoints
curl http://localhost:8001/public/echo
curl http://localhost:8001/health
curl http://localhost:8001/call-others

# Test private endpoint isolation (should fail)
curl http://localhost:8002/private/info  # Returns 404 - blocked by APP_MODE=public

# Stop services
docker-compose -f docker-compose.service1.yml down
docker-compose -f docker-compose.service2.yml down  
docker-compose -f docker-compose.service3.yml down
docker-compose -f docker-compose.networks.yml down
```

### Network Inspection
```bash
# Inspect networks
docker network ls
docker network inspect public_network

# View running containers
docker ps  # Should show 6 containers (3 public + 3 private)

# Test same-service private access (should work)
docker exec service1 python3 -c "import requests; print(requests.get('http://service1-private:8081/private/info').json())"

# Test cross-service isolation (should fail)
docker exec service1 python3 -c "import requests; requests.get('http://service2-private:8081/private/info')"
# Should fail with connection error - demonstrates proper isolation
```

## Implementation Guidelines

### Service Configuration Pattern
Services are configured as two containers:

#### Public Container Configuration:
- Environment: `APP_MODE=public`, `SERVICE_NAME`, `PUBLIC_PORT`, `PRIVATE_PORT`
- Networks: `public_network` + own private network (e.g., `service1_private`)
- Port mapping: External access (e.g., `8001:8080`)
- Endpoints: `/public/echo`, `/health`, `/call-others`
- Access: Can reach own private container

#### Private Container Configuration:
- Environment: `APP_MODE=private`, `SERVICE_NAME`, `PUBLIC_PORT`, `PRIVATE_PORT`
- Networks: Service-specific private network only (e.g., `service1_private`)
- No port mapping: Internal access only
- Endpoints: `/private/info`

### API Response Format
All endpoints return standardized JSON with `service`, `endpoint`, `timestamp`, and `data` fields.

### Network Isolation Testing
The `/call-others` endpoint tests network isolation by attempting to call:
- Own private endpoint: `http://service1-private:8081/private/info` (✅ succeeds - same network)
- Other services' public endpoints: `http://service2:8080/public/echo` (✅ succeeds)
- Other services' private endpoints: `http://service2-private:8081/private/info` (❌ fails with connection error)

### APP_MODE Environment Variable
- `APP_MODE=public`: Only serves public endpoints (`/public/echo`, `/health`, `/call-others`)
- `APP_MODE=private`: Only serves private endpoints (`/private/info`)
- `APP_MODE=all`: Serves all endpoints (legacy mode, not used in current implementation)

## Expected Behavior
- **Public endpoints**: ✅ Accessible between public containers via `public_network`
- **Private endpoints**: ❌ Network isolated - connection errors when accessed from other services
- **Cross-service private access**: ❌ Properly blocked at network level
- **Public container private access**: ❌ Blocked at application level (404 error)
- Comprehensive logging of all communication attempts
- Clear demonstration of true Docker network isolation principles

## ToDo
- Add comprehensive automated testing for network isolation
- Implement health checks for private containers
- Add monitoring and metrics collection
- Create additional test scenarios for edge cases