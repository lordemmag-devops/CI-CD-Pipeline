pipeline {
    agent any
    
    triggers {
        githubPush()
        pollSCM('H/5 * * * *')
    }
    
    environment {
        GCP_PROJECT_ID = credentials('gcp-project-id')
        GCP_REGION = 'us-central1'
        ARTIFACT_REGISTRY = "${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cicd-app"
        DOCKER_IMAGE = "${ARTIFACT_REGISTRY}/python-app:${BUILD_NUMBER}"
        GKE_CLUSTER = 'cicd-cluster'
        KUBE_NAMESPACE = 'python-ci-cd'
    }
    
    stages {
        stage('Setup') {
            steps {
                checkout scm
                withCredentials([file(credentialsId: 'gcp-service-account-key', variable: 'GCP_KEY_FILE')]) {
                    sh 'gcloud auth activate-service-account --key-file=${GCP_KEY_FILE}'
                    sh 'gcloud config set project ${GCP_PROJECT_ID}'
                }
            }
        }
        
        stage('Test') {
            steps {
                sh 'python3 -m pip install --upgrade pip'
                sh 'python3 -m pip install -r requirements.txt'
                sh 'python3 -m pytest --junitxml=test-results.xml || true'
                sh 'pylint --exit-zero app.py test_app.py > pylint-report.txt || true'
                sh 'bandit -r . -f txt -o bandit-report.txt || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: '*-report.txt,test-results.xml', fingerprint: true, allowEmptyArchive: true
                }
            }
        }
        
        stage('Build & Deploy') {
            steps {
                sh 'gcloud builds submit --tag ${DOCKER_IMAGE} .'
                sh 'gcloud container clusters get-credentials ${GKE_CLUSTER} --region=${GCP_REGION}'
                sh '''
                    kubectl create namespace ${KUBE_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                    kubectl set image deployment/python-app python-app=${DOCKER_IMAGE} -n ${KUBE_NAMESPACE} || \
                    kubectl create deployment python-app --image=${DOCKER_IMAGE} -n ${KUBE_NAMESPACE}
                    kubectl rollout status deployment/python-app -n ${KUBE_NAMESPACE} --timeout=300s
                    kubectl expose deployment python-app --port=80 --target-port=5000 -n ${KUBE_NAMESPACE} || true
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo "✅ Build SUCCESSFUL: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
        failure {
            echo "❌ Build FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        }
    }
}