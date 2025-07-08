# Python CI/CD Demo  Project

This project demonstrates a complete CI/CD pipeline for a Python Flask application

## Features

- Automated testing with pytest
- Code quality analysis with pylint
- Security scanning with bandit and ghcr.io zaproxy 
- CI pipeline with Jenkins
- CD pipeline with ArgoCD deploying to Kubernetes
- Docker containerization

## Pipeline Overview

1. **On code commit:**
   - Checkout code
   - Set up Python environment
   - Run unit tests
   - Perform code quality analysis
   - Run security scans
   - Build Docker image
   - Push to Docker registry
   - Trigger ArgoCD sync

## Local Development

1. Clone the repository
2. Set up virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
