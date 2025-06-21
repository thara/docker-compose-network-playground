from flask import Flask, jsonify
import os
from datetime import datetime

private_app = Flask(__name__)

SERVICE_NAME = os.getenv('SERVICE_NAME', 'service1')
PRIVATE_PORT = int(os.getenv('PRIVATE_PORT', 8081))

def get_timestamp():
    return datetime.utcnow().isoformat() + 'Z'

def create_response(endpoint, data=None):
    return jsonify({
        "service": SERVICE_NAME,
        "endpoint": endpoint,
        "timestamp": get_timestamp(),
        "data": data or {}
    })

@private_app.route('/private/info', methods=['GET'])
def private_info():
    data = {
        "sensitive_data": f"Private information from {SERVICE_NAME}",
        "internal_config": {
            "private_port": PRIVATE_PORT,
            "secret_key": "super-secret-key-12345",
            "network": "private_only"
        }
    }
    
    return create_response("/private/info", data)

if __name__ == '__main__':
    private_app.run(host='0.0.0.0', port=PRIVATE_PORT, debug=True)