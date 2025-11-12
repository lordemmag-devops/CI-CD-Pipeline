pipeline {
    agent any
    
    environment {
        PROJECT_ID = credentials('gcp-project-id')
        GOOGLE_APPLICATION_CREDENTIALS = credentials('gcp-service-account-key')
        IMAGE_NAME = 'python-app'
        REGISTRY_URL = 'us-central1-docker.pkg.dev'
        REPOSITORY = 'cicd-app'
        CLUSTER_NAME = 'cicd-cluster'
        CLUSTER_ZONE = 'us-central1'
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
                        def dockerPath = sh(script: 'which docker', returnStdout: true).trim()
                        def imageTag = "${env.BUILD_NUMBER}"
                        def fullImageName = "${REGISTRY_URL}/${GCP_PROJECT}/${REPOSITORY}/${IMAGE_NAME}:${imageTag}"
                        
                        sh "${dockerPath} build -t ${fullImageName} ."
                        sh "${dockerPath} tag ${fullImageName} ${REGISTRY_URL}/${GCP_PROJECT}/${REPOSITORY}/${IMAGE_NAME}:latest"
                        
                        env.FULL_IMAGE_NAME = fullImageName
                        env.LATEST_IMAGE_NAME = "${REGISTRY_URL}/${GCP_PROJECT}/${REPOSITORY}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }
        
        stage('Push to Artifact Registry') {
            steps {
                echo 'Pushing image to Artifact Registry...'
                withCredentials([string(credentialsId: 'gcp-project-id', variable: 'GCP_PROJECT')]) {
                    sh '''
                        DOCKER_PATH=$(which docker)
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
                        
                        ${DOCKER_PATH} push ${FULL_IMAGE_NAME}
                        ${DOCKER_PATH} push ${LATEST_IMAGE_NAME}
                    '''
                }
            }
        }
        
        stage('Deploy to GKE') {
            steps {
                echo 'Deploying to GKE...'
                withCredentials([string(credentialsId: 'gcp-project-id', variable: 'GCP_PROJECT')]) {
                    sh '''
                        gcloud container clusters get-credentials ${CLUSTER_NAME} --zone=${CLUSTER_ZONE} --project=${GCP_PROJECT}
                        
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
                    
                    # Wait for pods to be ready
                    kubectl wait --for=condition=ready pod -l app=python-app -n ${NAMESPACE} --timeout=120s
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            sh '''
                # Clean up Docker images
                DOCKER_PATH=$(which docker)
                ${DOCKER_PATH} rmi ${FULL_IMAGE_NAME} || true
                ${DOCKER_PATH} rmi ${LATEST_IMAGE_NAME} || true
                
                # Clean up Python virtual environment
                rm -rf venv || true
            '''
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}