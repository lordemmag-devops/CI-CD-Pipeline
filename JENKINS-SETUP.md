# Complete Jenkins Setup Guide

## Step 1: Install Jenkins

### Option A: Using Homebrew (Recommended)
```bash
# Install Jenkins
brew install jenkins-lts

# Start Jenkins
brew services start jenkins-lts

# Access Jenkins at: http://localhost:8080
```

### Option B: Using Docker
```bash
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins jenkins/jenkins:lts
```

## Step 2: Initial Jenkins Setup

1. **Get Initial Password**:
   ```bash
   cat ~/.jenkins/secrets/initialAdminPassword
   ```

2. **Open Jenkins**: http://localhost:8080

3. **Install Suggested Plugins** (click "Install suggested plugins")

4. **Create Admin User**:
   - Username: admin
   - Password: [your-password]
   - Full name: Admin
   - Email: your-email@example.com

## Step 3: Install Required Plugins

Go to **Manage Jenkins** → **Plugins** → **Available plugins**

Search and install:
- ✅ **Pipeline** (should be pre-installed)
- ✅ **Git** (should be pre-installed)
- ✅ **GitHub** 
- ✅ **Google Kubernetes Engine**
- ✅ **Google Container Registry Auth**

## Step 4: Configure System Tools

### A. Configure Git
1. **Manage Jenkins** → **Tools**
2. Scroll to **Git** section
3. Click **Add Git**
4. **Name**: `Default`
5. **Path to Git executable**: `/usr/local/bin/git`
6. Click **Save**

### B. Install gcloud CLI (if not installed)
```bash
# Install gcloud
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verify installation
gcloud --version
```

### C. Install kubectl (if not installed)
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

## Step 5: Add GCP Credentials

### A. Get Service Account Key
```bash
cd terraform
terraform output -raw cicd_service_account_key | base64 -d > gcp-key.json
```

### B. Add Credentials to Jenkins
1. **Manage Jenkins** → **Credentials**
2. Click **System** → **Global credentials**
3. Click **+ Add Credentials**

**Credential 1: Project ID**
- Kind: **Secret text**
- Secret: `ci-cd-pipeline-477813`
- ID: `gcp-project-id`
- Description: `GCP Project ID`

**Credential 2: Service Account Key**
- Kind: **Secret file**
- File: Upload `gcp-key.json`
- ID: `gcp-service-account-key`
- Description: `GCP Service Account Key`

## Step 6: Create Pipeline Job

1. **New Item** → Enter name: `CI-CD-Pipeline`
2. Select **Pipeline** → Click **OK**

### Configure Pipeline:
**General Tab:**
- ✅ Check **GitHub project**
- Project URL: `https://github.com/lordemmag-devops/CI-CD-Pipeline`

**Build Triggers:**
- ✅ Check **GitHub hook trigger for GITScm polling**
- ✅ Check **Poll SCM**: `H/5 * * * *`

**Pipeline Tab:**
- Definition: **Pipeline script from SCM**
- SCM: **Git**
- Repository URL: `https://github.com/lordemmag-devops/CI-CD-Pipeline.git`
- Branch: `*/master`
- Script Path: `Jenkinsfile`

Click **Save**

## Step 7: Test Pipeline

### Simple Test Jenkinsfile
```groovy
pipeline {
    agent any
    
    stages {
        stage('Test Environment') {
            steps {
                echo 'Testing Jenkins setup...'
                sh 'python3 --version'
                sh 'gcloud --version'
                sh 'kubectl version --client'
            }
        }
        
        stage('Test Credentials') {
            steps {
                withCredentials([
                    string(credentialsId: 'gcp-project-id', variable: 'PROJECT'),
                    file(credentialsId: 'gcp-service-account-key', variable: 'KEY_FILE')
                ]) {
                    echo "Project: ${PROJECT}"
                    sh 'ls -la ${KEY_FILE}'
                }
            }
        }
    }
}
```

## Step 8: GitHub Webhook (Optional)

1. Go to GitHub repository → **Settings** → **Webhooks**
2. Click **Add webhook**
3. Payload URL: `http://your-jenkins-url:8080/github-webhook/`
4. Content type: `application/json`
5. Events: **Just the push event**
6. Click **Add webhook**

## Step 9: Run First Build

1. Go to your pipeline job
2. Click **Build Now**
3. Monitor **Console Output**

## Troubleshooting

### Common Issues:
1. **Python not found**: Install Python 3
2. **gcloud not found**: Add to PATH or install
3. **Credentials not working**: Re-create with exact IDs
4. **Permission denied**: Check file permissions

### Verify Setup:
```bash
# Check if tools are available
which python3
which gcloud
which kubectl

# Test GCP authentication
gcloud auth list
gcloud config list
```

## Next Steps

Once basic setup works:
1. Use the full CI/CD Jenkinsfile
2. Configure GitHub webhooks
3. Monitor builds and deployments
4. Set up notifications (Slack, email)