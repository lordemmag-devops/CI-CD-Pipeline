pipeline {
    agent any
    
    environment {
        GCP_PROJECT_ID = 'ci-cd-pipeline-477813'
        GCP_REGION = 'us-central1'
        ARTIFACT_REGISTRY = "${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cicd-app"
        DOCKER_IMAGE = "${ARTIFACT_REGISTRY}/python-app:${BUILD_NUMBER}"
        GKE_CLUSTER = 'cicd-cluster'
        KUBE_NAMESPACE = 'python-ci-cd'
    }
    
    stages {
        stage('Environment Check') {
            steps {
                echo 'Checking environment...'
                sh 'pwd && ls -la'
                sh 'python3 --version || echo "Python3 not available"'
                sh 'gcloud --version || echo "gcloud not available"'
                sh 'kubectl version --client || echo "kubectl not available"'
            }
        }
        
        stage('GCP Auth') {
            steps {
                echo 'Authenticating with GCP...'
                withCredentials([file(credentialsId: 'gcp-service-account-key', variable: 'GCP_KEY_FILE')]) {
                    sh 'gcloud auth activate-service-account --key-file=${GCP_KEY_FILE}'
                    sh 'gcloud config set project ${GCP_PROJECT_ID}'
                    sh 'gcloud config list'
                }
            }
        }
        
        stage('Simple Test') {
            steps {
                echo 'Running basic tests...'
                sh 'python3 -c "print(\'Hello from Python\')"'
                sh 'echo "Build number: ${BUILD_NUMBER}"'
                sh 'echo "Docker image: ${DOCKER_IMAGE}"'
            }
        }
    }
    
    post {
        success {
            echo "✅ Build SUCCESSFUL: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
        failure {
            echo "❌ Build FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
    }
}