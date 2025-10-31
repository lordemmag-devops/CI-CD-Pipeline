from flask import Flask, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    try:
        return "Python CI/CD Demo - Hello World!"
    except Exception as e:
        app.logger.error(f"Error in home route: {e}")
        return "Internal Server Error", 500

@app.route('/health')
def health():
    try:
        return jsonify({"status": "healthy"})
    except Exception as e:
        app.logger.error(f"Error in health route: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        exit(1)
