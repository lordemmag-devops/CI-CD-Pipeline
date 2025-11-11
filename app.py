try:
    from flask import Flask, jsonify
except ImportError as e:
    print(f"Failed to import Flask: {e}")
    exit(1)

import logging
import time

try:
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)
except Exception as e:
    logging.error(f"Failed to initialize Flask app: {e}")
    exit(1)

@app.route('/')
def home():
    try:
        return "Python CI/CD Demo - Hello World!"
    except (ValueError, TypeError) as e:
        app.logger.error(f"Home route validation error: {e}")
        return "Bad Request", 400
    except Exception as e:
        app.logger.error(f"Error in home route: {e}")
        return "Internal Server Error", 500

@app.route('/health')
def health():
    try:
        health_status = {
            "status": "healthy",
            "timestamp": str(time.time()),
            "service": "ci-cd-pipeline"
        }
        return jsonify(health_status), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": "Internal error"}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        exit(1)
