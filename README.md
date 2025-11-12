# Python CI/CD Demo Project - GCP Free Tier

Complete CI/CD pipeline for a Python Flask application deployed on Google Cloud Platform within the Always Free tier limits.

## Features

- Automated testing with pytest
- Code quality analysis with pylint
- Security scanning with bandit
- CI/CD pipeline with Jenkins
- Deployment to Google Kubernetes Engine (GKE Autopilot)
- Docker containerization with Artifact Registry
- **Zero cost deployment** using GCP Free Tier

## Architecture

- **GKE Autopilot**: Regional cluster (us-central1)
- **Artifact Registry**: Container image storage
- **Jenkins**: CI/CD automation
- **Minimal Resources**: 64Mi RAM, 50m CPU

## Prerequisites

- Google Cloud SDK installed and configured
- Docker installed
- Terraform installed
- Python 3.9+ installed
- kubectl installed

## Complete Setup

### 1. Create GCP Project
```bash
# Create new project (replace with unique ID)
gcloud projects create your-unique-project-id
gcloud config set project your-unique-project-id

# Enable billing (required for GKE)
gcloud billing accounts list
gcloud billing projects link your-unique-project-id --billing-account=BILLING_ACCOUNT_ID
```

### 2. Configure Authentication
```bash
# Authenticate with GCP
gcloud auth login
gcloud auth application-default login
```

### 3. Deploy Infrastructure
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your project ID
sed -i '' 's/ci-cd-pipeline-477813/your-unique-project-id/g' terraform.tfvars

# Initialize and apply Terraform
terraform init
terraform plan
terraform apply -auto-approve
```

### 4. Build and Push Docker Image
```bash
cd ..

# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push image
docker build -t us-central1-docker.pkg.dev/your-unique-project-id/cicd-app/python-app:latest .
docker push us-central1-docker.pkg.dev/your-unique-project-id/cicd-app/python-app:latest
```

### 5. Update Kubernetes Manifests
```bash
# Update deployment with your project ID
sed -i '' 's/ci-cd-pipeline-477813/your-unique-project-id/g' k8s/deployment.yaml
```

### 6. Deploy to Kubernetes
```bash
# Get cluster credentials
gcloud container clusters get-credentials cicd-cluster --region=us-central1

# Create namespace and deploy
kubectl create namespace python-ci-cd
kubectl apply -f k8s/

# Verify deployment
kubectl get pods -n python-ci-cd
kubectl get services -n python-ci-cd
```

### 7. Test Application
```bash
# Port forward to test locally
kubectl port-forward -n python-ci-cd service/python-app 8080:80

# Test endpoints
curl http://localhost:8080/
curl http://localhost:8080/health
```

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest test_app.py -v

# Run application
python app.py
```

## Testing

```bash
# Run all tests
pytest -v

# Code quality check
pylint app.py

# Security scan
bandit -r . -f json
```

## Cleanup

```bash
# Delete Kubernetes resources
kubectl delete namespace python-ci-cd

# Destroy infrastructure
cd terraform
terraform destroy -auto-approve

# Delete project (optional)
gcloud projects delete your-unique-project-id
```

## Troubleshooting

- **GKE cluster creation fails**: Ensure billing is enabled
- **Docker push fails**: Run `gcloud auth configure-docker us-central1-docker.pkg.dev`
- **Pod fails to start**: Check image name matches your project ID
- **Service unreachable**: Verify namespace and service configuration

## Cost Optimization

- Uses GKE Autopilot for automatic scaling
- Minimal resource requests (64Mi RAM, 50m CPU)
- Regional cluster in us-central1 (free tier eligible)
- Single replica deployment 