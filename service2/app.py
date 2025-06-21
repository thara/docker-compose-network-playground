from flask import Flask, jsonify, request
import requests
import json
import logging
from datetime import datetime
import os

app = Flask(__name__)

SERVICE_NAME = os.getenv('SERVICE_NAME', 'service1')
PUBLIC_PORT = int(os.getenv('PUBLIC_PORT', 8080))
PRIVATE_PORT = int(os.getenv('PRIVATE_PORT', 8081))
APP_MODE = os.getenv('APP_MODE', 'all')  # 'public', 'private', or 'all'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_timestamp():
    return datetime.utcnow().isoformat() + 'Z'

def create_response(endpoint, data=None):
    return jsonify({
        "service": SERVICE_NAME,
        "endpoint": endpoint,
        "timestamp": get_timestamp(),
        "data": data or {}
    })

@app.route('/public/echo', methods=['GET', 'POST'])
def public_echo():
    if APP_MODE == 'private':
        return jsonify({"error": "Public endpoints not available in private mode"}), 404
    logger.info(f"Public echo endpoint called: {request.method}")
    
    if request.method == 'POST':
        request_data = request.get_json() or {}
    else:
        request_data = dict(request.args)
    
    data = {
        "method": request.method,
        "received": request_data,
        "message": f"Echo from {SERVICE_NAME}",
        "note": "This endpoint is accessible from other services via public network"
    }
    
    return create_response("/public/echo", data)

@app.route('/private/info', methods=['GET'])
def private_info():
    if APP_MODE == 'public':
        return jsonify({"error": "Private endpoints not available in public mode"}), 404
    logger.info("Private info endpoint called")
    
    data = {
        "sensitive_data": f"Private information from {SERVICE_NAME}",
        "internal_config": {
            "private_port": PRIVATE_PORT,
            "secret_key": "super-secret-key-12345"
        },
        "note": "This endpoint should only be accessible within the same service's private network"
    }
    
    return create_response("/private/info", data)

@app.route('/health', methods=['GET'])
def health():
    if APP_MODE == 'private':
        return jsonify({"error": "Health endpoint not available in private mode"}), 404
    logger.info("Health check endpoint called")
    
    data = {
        "status": "healthy",
        "service": SERVICE_NAME,
        "ports": {
            "public": PUBLIC_PORT,
            "private": PRIVATE_PORT
        }
    }
    
    return create_response("/health", data)

@app.route('/call-others', methods=['GET'])
def call_others():
    if APP_MODE == 'private':
        return jsonify({"error": "Call-others endpoint not available in private mode"}), 404
    logger.info("Inter-service communication test started")
    
    results = []
    other_services = ['service2', 'service3'] if SERVICE_NAME == 'service1' else \
                    ['service1', 'service3'] if SERVICE_NAME == 'service2' else \
                    ['service1', 'service2']
    
    for service in other_services:
        # Test public endpoint (should work)
        try:
            response = requests.get(f"http://{service}:8080/public/echo?test=from_{SERVICE_NAME}", timeout=5)
            results.append({
                "target": service,
                "endpoint": "/public/echo",
                "status": "success",
                "status_code": response.status_code,
                "response": response.json()
            })
            logger.info(f"Successfully called {service} public endpoint")
        except Exception as e:
            results.append({
                "target": service,
                "endpoint": "/public/echo",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"Failed to call {service} public endpoint: {e}")
        
        # Test private endpoint (should fail due to network isolation)
        # Note: This demonstrates the key concept - services can't reach each other's private endpoints
        try:
            response = requests.get(f"http://{service}-private:8081/private/info", timeout=5)
            results.append({
                "target": service,
                "endpoint": "/private/info",
                "status": "accessible_but_shouldnt_be",
                "status_code": response.status_code,
                "response": response.json(),
                "note": "This should NOT be accessible - indicates network isolation failure"
            })
            logger.warning(f"Could access {service} private endpoint (expected in this demo)")
        except Exception as e:
            results.append({
                "target": service,
                "endpoint": "/private/info",
                "status": "properly_isolated",
                "error": str(e)
            })
            logger.info(f"Private endpoint properly isolated for {service}: {e}")
    
    data = {
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "public_successes": len([r for r in results if r["endpoint"] == "/public/echo" and r["status"] == "success"]),
            "private_attempts": len([r for r in results if r["endpoint"] == "/private/info"])
        },
        "explanation": "Private endpoints should be isolated and only accessible within each service's private network. Public endpoints remain accessible between services."
    }
    
    return create_response("/call-others", data)

if __name__ == '__main__':
    port = PRIVATE_PORT if APP_MODE == 'private' else PUBLIC_PORT
    app.run(host='0.0.0.0', port=port, debug=True)