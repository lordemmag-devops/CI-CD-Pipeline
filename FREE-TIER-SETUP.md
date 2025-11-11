# GCP Free Tier Deployment Guide

## Free Tier Limits & Configuration

### **Always Free Resources Used:**
- **GKE Autopilot**: Regional cluster in us-central1 (free tier eligible)
- **Artifact Registry**: 0.5 GB storage (free)
- **Compute Engine**: e2-micro instances (1 per month free)
- **Cloud Storage**: 5 GB (for logs/artifacts)
- **Network**: 1 GB egress per month (free)

### **Resource Constraints Applied:**
```yaml
# Minimal container resources
resources:
  requests:
    memory: "64Mi"
    cpu: "50m"
  limits:
    memory: "128Mi" 
    cpu: "100m"

# Single replica deployment
replicas: 1
```

## Setup Instructions

### 1. Create GCP Project (Free Tier)
```bash
gcloud projects create your-demo-project-id
gcloud config set project your-demo-project-id
gcloud auth application-default login
```

### 2. Deploy Infrastructure
```bash
cd terraform

# Create terraform.tfvars
cat > terraform.tfvars << EOF
gcp_project_id = "your-demo-project-id"
gcp_region     = "us-central1"
gcp_zone       = "us-central1-a"
docker_image   = "us-central1-docker.pkg.dev/your-demo-project-id/cicd-app/python-app:latest"
EOF

# Deploy (stays within free tier)
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

### 3. Configure Jenkins (Minimal Setup)
```bash
# Get service account key
terraform output -raw cicd_service_account_key | base64 -d > gcp-key.json

# Add to Jenkins credentials:
# - gcp-project-id: your-demo-project-id
# - gcp-service-account-key: gcp-key.json file
```

### 4. Deploy Application
```bash
# Get cluster credentials
gcloud container clusters get-credentials cicd-cluster --region=us-central1

# Update deployment with your project ID
sed -i 's/PROJECT_ID/your-demo-project-id/g' k8s/deployment.yaml
grep "image:" k8s/deployment.yaml

# Deploy (minimal resources)
kubectl create namespace python-ci-cd
kubectl apply -f k8s/
```

## Free Tier Monitoring

### Check Resource Usage:
```bash
# Monitor cluster resources
kubectl top nodes
kubectl top pods -n python-ci-cd
kubectl describe pod -n python-ci-cd <pod-name>
```
### Configure Docker to authenticate with google Artifact Registry:
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev 
```
### Build Docker Image

```bash
docker built -t us-central1-docker.pkg.dev/your-demo-project-id/cicd-app/python-app:latest .
docker push us-central1-docker.pkg.dev/your-demo-project-id/cicd-app/python-app:latest
```

# Check GCP quotas
```bash
gcloud compute project-info describe --format="table(quotas.metric,quotas.usage,quotas.limit)"
```

### Cost Alerts:
```bash
# Set up billing alert (recommended: $1)
gcloud alpha billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Demo Project Budget" \
  --budget-amount=1USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90
```

## Limitations & Considerations

### **Free Tier Constraints:**
- Single zone deployment (no high availability)
- Minimal compute resources (64Mi RAM, 50m CPU)
- Limited to 1 replica
- No load balancer (use NodePort for testing)
- 0.5GB container registry storage

### **Production Considerations:**
- Upgrade to paid tier for:
  - Multi-zone clusters
  - Load balancers
  - Higher resource limits
  - Multiple replicas
  - Advanced monitoring

## Cleanup (Important!)
```bash
# Delete resources to avoid charges
kubectl delete namespace python-ci-cd
terraform destroy -var-file="terraform.tfvars"
gcloud projects delete your-demo-project-id
```

## Free Tier Best Practices

1. **Monitor Usage**: Check quotas regularly
2. **Set Alerts**: Configure billing alerts at $1
3. **Clean Up**: Delete resources when not needed
4. **Use Autopilot**: Automatic resource optimization
5. **Single Zone**: Avoid cross-zone traffic charges

## Estimated Monthly Cost: $0
- All resources configured within Always Free limits
- No egress charges for demo traffic
- Autopilot optimizes resource usage automatically