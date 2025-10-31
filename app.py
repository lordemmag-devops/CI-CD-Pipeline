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
        # Validate service dependencies
        if not app:
            raise RuntimeError("Flask app not initialized")
        
        # Perform basic health checks
        try:
            timestamp = time.time()
        except (OSError, OverflowError) as te:
            app.logger.error(f"Time error: {te}")
            timestamp = "unavailable"
        
        try:
            health_status = {
                "status": "healthy",
                "timestamp": str(timestamp),
                "service": "ci-cd-pipeline"
            }
        except (MemoryError, KeyError) as de:
            app.logger.error(f"Dictionary creation error: {de}")
            health_status = {"status": "healthy", "error": "partial_data"}
        return jsonify(health_status), 200
    except (ValueError, TypeError) as e:
        app.logger.error(f"Health check validation error: {e}")
        return jsonify({"status": "unhealthy", "error": "Validation failed"}), 400
    except (KeyError, AttributeError) as e:
        app.logger.error(f"Health check attribute error: {e}")
        return jsonify({"status": "unhealthy", "error": "Configuration error"}), 500
    except (OSError, IOError) as e:
        app.logger.error(f"Health check I/O error: {e}")
        return jsonify({"status": "unhealthy", "error": "Service unavailable"}), 503
    except (ConnectionError, TimeoutError) as e:
        app.logger.error(f"Health check connection error: {e}")
        return jsonify({"status": "unhealthy", "error": "Connection failed"}), 503
    except RuntimeError as e:
        app.logger.critical(f"Health check runtime error: {e}")
        return jsonify({"status": "unhealthy", "error": "Service not ready"}), 503
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": "Internal error"}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        exit(1)
