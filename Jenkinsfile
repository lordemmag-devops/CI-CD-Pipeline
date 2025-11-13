pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'python-app'
        REGISTRY_URL = 'us-central1-docker.pkg.dev'
        REPOSITORY = 'cicd-app'
        CLUSTER_NAME = 'cicd-cluster'
        CLUSTER_REGION = 'us-central1'
        NAMESPACE = 'python-ci-cd'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    . venv/bin/activate
                    python -m pytest test_app.py -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
        
        stage('Code Quality Analysis') {
            parallel {
                stage('Pylint') {
                    steps {
                        echo 'Running pylint...'
                        sh '''
                            . venv/bin/activate
                            pylint app.py --output-format=text --reports=no --score=no || true
                        '''
                    }
                }
                stage('Security Scan') {
                    steps {
                        echo 'Running security scan...'
                        sh '''
                            . venv/bin/activate
                            bandit -r . -f json -o bandit-report.json || true
                        '''
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                withCredentials([string(credentialsId: 'gcp-project-id', variable: 'GCP_PROJECT')]) {
                    script {
                        def imageTag = "${env.BUILD_NUMBER}"
                        def fullImageName = "${REGISTRY_URL}/${GCP_PROJECT}/${REPOSITORY}/${IMAGE_NAME}:${imageTag}"
                        
                        sh "docker build -t ${fullImageName} ."
                        sh "docker tag ${fullImageName} ${REGISTRY_URL}/${GCP_PROJECT}/${REPOSITORY}/${IMAGE_NAME}:latest"
                        
                        env.FULL_IMAGE_NAME = fullImageName
                        env.LATEST_IMAGE_NAME = "${REGISTRY_URL}/${GCP_PROJECT}/${REPOSITORY}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }
        
        stage('Push to Artifact Registry') {
            steps {
                echo 'Pushing image to Artifact Registry...'
                withCredentials([
                    string(credentialsId: 'gcp-project-id', variable: 'GCP_PROJECT'),
                    file(credentialsId: 'gcp-service-account-key', variable: 'GCP_KEY_FILE')
                ]) {
                    sh '''
                        gcloud auth activate-service-account --key-file="${GCP_KEY_FILE}"
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
                        
                        docker push ${FULL_IMAGE_NAME}
                        docker push ${LATEST_IMAGE_NAME}
                    '''
                }
            }
        }
        
        stage('Deploy to GKE') {
            steps {
                echo 'Deploying to GKE...'
                withCredentials([
                    string(credentialsId: 'gcp-project-id', variable: 'GCP_PROJECT'),
                    file(credentialsId: 'gcp-service-account-key', variable: 'GCP_KEY_FILE')
                ]) {
                    sh '''
                        gcloud auth activate-service-account --key-file="${GCP_KEY_FILE}"
                        
                        # Install gke-gcloud-auth-plugin
                        gcloud components install gke-gcloud-auth-plugin --quiet
                        
                        gcloud container clusters get-credentials ${CLUSTER_NAME} --region=${CLUSTER_REGION} --project=${GCP_PROJECT}
                        
                        # Create namespace if it doesn't exist
                        kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                        
                        # Update deployment image
                        kubectl set image deployment/python-app python-app=${FULL_IMAGE_NAME} -n ${NAMESPACE}
                        
                        # Apply all k8s manifests
                        kubectl apply -f k8s/ -n ${NAMESPACE}
                        
                        # Wait for rollout to complete
                        kubectl rollout status deployment/python-app -n ${NAMESPACE} --timeout=300s
                    '''
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                echo 'Verifying deployment...'
                sh '''
                    # Check pod status
                    kubectl get pods -n ${NAMESPACE} -l app=python-app
                    
                    # Check service status
                    kubectl get svc -n ${NAMESPACE}
                    
                    # Wait for deployment to be ready
                    kubectl wait --for=condition=available deployment/python-app -n ${NAMESPACE} --timeout=300s
                    
                    # Get pod status after deployment
                    kubectl get pods -n ${NAMESPACE} -l app=python-app
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            sh '''
                # Clean up Docker images
                docker rmi ${FULL_IMAGE_NAME} || true
                docker rmi ${LATEST_IMAGE_NAME} || true
                
                # Clean up Python virtual environment
                rm -rf venv || true
            '''
        }
        success {
            echo 'Pipeline completed successfully!'
            script {
                try {
                    mail to: 'your-email@gmail.com',
                         subject: "✅ Build Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                         body: "Build completed successfully!\n\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nURL: ${env.BUILD_URL}"
                } catch (Exception e) {
                    echo "Email notification failed: ${e.getMessage()}"
                }
            }
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
            script {
                try {
                    mail to: 'your-email@gmail.com',
                         subject: "❌ Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                         body: "Build failed!\n\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nURL: ${env.BUILD_URL}\nConsole: ${env.BUILD_URL}console"
                } catch (Exception e) {
                    echo "Email notification failed: ${e.getMessage()}"
                }
            }
        }
        unstable {
            script {
                try {
                    mail to: 'your-email@gmail.com',
                         subject: "⚠️ Build Unstable: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                         body: "Build unstable!\n\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nURL: ${env.BUILD_URL}"
                } catch (Exception e) {
                    echo "Email notification failed: ${e.getMessage()}"
                }
            }
        }
    }
}