pipeline {
    agent any
    
    triggers {
        githubPush()
        pollSCM('H/5 * * * *')
    }
    
    environment {
        GCP_PROJECT_ID = credentials('gcp-project-id')
        GCP_REGION = 'us-central1'
        GCP_ZONE = 'us-central1-a'
        ARTIFACT_REGISTRY = "${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cicd-app"
        DOCKER_IMAGE = "${ARTIFACT_REGISTRY}/python-app:${BUILD_NUMBER}"
        GKE_CLUSTER = 'cicd-cluster'
        KUBE_NAMESPACE = 'python-ci-cd'
    }
    
    stages {
        stage('Build') {
            steps {
                checkout scm
                sh 'python3 -m pip install --upgrade pip'
                sh 'python3 -m pip install -r requirements.txt'
                sh 'docker build -t ${DOCKER_IMAGE} .'
            }
        }
        
        stage('Test') {
            steps {
                sh 'python3 -m pytest --junitxml=test-results.xml'
                sh 'pylint --exit-zero app.py test_app.py > pylint-report.txt || true'
                sh 'bandit -r . -f txt -o bandit-report.txt || true'
            }
            post {
                always {
                    junit 'test-results.xml'
                    archiveArtifacts artifacts: '*-report.txt', fingerprint: true
                }
            }
        }
        
        stage('Deploy') {
            steps {
                withCredentials([file(credentialsId: 'gcp-service-account-key', variable: 'GCP_KEY_FILE')]) {
                    sh 'gcloud auth activate-service-account --key-file=${GCP_KEY_FILE}'
                    sh 'gcloud config set project ${GCP_PROJECT_ID}'
                    sh 'gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev'
                }
                sh 'docker push ${DOCKER_IMAGE}'
                sh 'gcloud container clusters get-credentials ${GKE_CLUSTER} --zone=${GCP_ZONE}'
                sh '''
                    kubectl create namespace ${KUBE_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                    kubectl set image deployment/python-app python-app=${DOCKER_IMAGE} -n ${KUBE_NAMESPACE}
                    kubectl rollout status deployment/python-app -n ${KUBE_NAMESPACE} --timeout=300s
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            slackSend(color: "good", message: "✅ GCP Build SUCCESSFUL: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        failure {
            slackSend(color: "danger", message: "❌ GCP Build FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
    }
}