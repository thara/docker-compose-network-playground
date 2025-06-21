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
    logger.info(f"Public echo endpoint called: {request.method}")
    
    if request.method == 'POST':
        request_data = request.get_json() or {}
    else:
        request_data = dict(request.args)
    
    data = {
        "method": request.method,
        "received": request_data,
        "message": f"Echo from {SERVICE_NAME}"
    }
    
    return create_response("/public/echo", data)

@app.route('/private/info', methods=['GET'])
def private_info():
    logger.info("Private info endpoint called")
    
    data = {
        "sensitive_data": f"Private information from {SERVICE_NAME}",
        "internal_config": {
            "private_port": PRIVATE_PORT,
            "secret_key": "super-secret-key-12345"
        }
    }
    
    return create_response("/private/info", data)

@app.route('/health', methods=['GET'])
def health():
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
    logger.info("Inter-service communication test started")
    
    results = []
    other_services = ['service2', 'service3'] if SERVICE_NAME == 'service1' else \
                    ['service1', 'service3'] if SERVICE_NAME == 'service2' else \
                    ['service1', 'service2']
    
    for service in other_services:
        # Test public endpoint
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
        
        # Test private endpoint (should fail)
        try:
            response = requests.get(f"http://{service}:8081/private/info", timeout=5)
            results.append({
                "target": service,
                "endpoint": "/private/info",
                "status": "unexpected_success",
                "status_code": response.status_code,
                "response": response.json()
            })
            logger.warning(f"Unexpectedly accessed {service} private endpoint")
        except Exception as e:
            results.append({
                "target": service,
                "endpoint": "/private/info",
                "status": "blocked_as_expected",
                "error": str(e)
            })
            logger.info(f"Private endpoint properly blocked for {service}: {e}")
    
    data = {
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "public_successes": len([r for r in results if r["endpoint"] == "/public/echo" and r["status"] == "success"]),
            "private_blocked": len([r for r in results if r["endpoint"] == "/private/info" and r["status"] == "blocked_as_expected"])
        }
    }
    
    return create_response("/call-others", data)

if __name__ == '__main__':
    # Run public endpoints on PUBLIC_PORT
    from threading import Thread
    
    def run_private_server():
        private_app = Flask(__name__ + "_private")
        
        @private_app.route('/private/info', methods=['GET'])
        def private_info_server():
            return private_info()
        
        private_app.run(host='0.0.0.0', port=PRIVATE_PORT, debug=False)
    
    # Start private server in background thread
    private_thread = Thread(target=run_private_server)
    private_thread.daemon = True
    private_thread.start()
    
    # Run main app with public endpoints
    app.run(host='0.0.0.0', port=PUBLIC_PORT, debug=True)