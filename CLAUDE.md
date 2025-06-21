# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Docker Compose network playground demonstrating inter-service communication with network isolation. The project consists of multiple Docker Compose files that create services with both public and private endpoints to showcase Docker networking concepts.

## Architecture

### Multi-Compose File Structure
- `docker-compose.networks.yml` - Defines shared networks (`public_network`) and manages network isolation
- `docker-compose.service1.yml`, `docker-compose.service2.yml`, `docker-compose.service3.yml` - Individual service definitions

### Network Architecture
- **Public Network** (`public_network`): Shared bridge network for inter-service communication
- **Private Networks** (`service1_private`, `service2_private`, `service3_private`): Isolated networks for each service's private endpoints

### Service Design Pattern
Each service implements:
- Public endpoint (`/public/echo`) - accessible across services via public network
- Private endpoint (`/private/info`) - only accessible within service's private network
- Health endpoint (`/health`) - public health check
- Inter-service communication endpoint (`/call-others`) - demonstrates network access patterns

## Common Commands

### Starting the Environment
```bash
# Start networks first
docker-compose -f docker-compose.networks.yml up -d

# Start all services
docker-compose -f docker-compose.service1.yml up -d
docker-compose -f docker-compose.service2.yml up -d
docker-compose -f docker-compose.service3.yml up -d
```

### Development and Testing
```bash
# View service logs
docker-compose -f docker-compose.service1.yml logs -f

# Test public endpoints (replace with actual ports)
curl http://localhost:8001/public/echo
curl http://localhost:8001/health
curl http://localhost:8001/call-others

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
docker network inspect docker-compose-network-playground_public_network

# View service network connections
docker inspect <container_name> | grep NetworkMode
```

## Implementation Guidelines

### Service Configuration Pattern
Services should be configured with:
- Connection to both public and private networks
- Environment variables: `SERVICE_NAME`, `PUBLIC_PORT`, `PRIVATE_PORT`
- Port mapping for public endpoints only
- Structured JSON logging for all requests and inter-service calls

### API Response Format
All endpoints return standardized JSON with `service`, `endpoint`, `timestamp`, and `data` fields.

### Network Isolation Testing
The `/call-others` endpoint should attempt to call both public and private endpoints of other services, logging success/failure to demonstrate network isolation effectiveness.

## Expected Behavior
- Public endpoints accessible between services
- Private endpoints return connection errors when accessed from other services
- Comprehensive logging of all communication attempts
- Clear demonstration of Docker network isolation principles

## ToDo
- Add missing service dependencies
- Implement comprehensive network isolation test cases
- Create detailed documentation for each service's network configuration