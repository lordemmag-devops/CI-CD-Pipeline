# Python CI/CD Demo Project - GCP Free Tier

This project demonstrates a complete CI/CD pipeline for a Python Flask application deployed on Google Cloud Platform within the Always Free tier limits.

## Features

- Automated testing with pytest
- Code quality analysis with pylint
- Security scanning with bandit
- CI/CD pipeline with Jenkins
- Deployment to Google Kubernetes Engine (GKE Autopilot)
- Docker containerization with Artifact Registry
- **Zero cost deployment** using GCP Free Tier

## Architecture

- **GKE Autopilot**: Zonal cluster (us-central1-a)
- **Artifact Registry**: Container image storage
- **Jenkins**: CI/CD automation
- **Minimal Resources**: 64Mi RAM, 50m CPU

## Quick Setup

1. **Create GCP Project**:
   ```bash
   gcloud projects create your-demo-project-id
   gcloud config set project your-demo-project-id
   ```

2. **Deploy Infrastructure**:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your project ID
   terraform init && terraform apply
   ```

3. **Deploy Application**:
   ```bash
   gcloud container clusters get-credentials cicd-cluster --region=us-central1
   kubectl create namespace python-ci-cd
   cd ..
   kubectl apply -f k8s/
   ```

## Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
