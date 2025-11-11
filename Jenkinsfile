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
        // ========== BUILD SECTION ==========
        stage('Build') {
            parallel {
                stage('Checkout & Setup') {
                    steps {
                        checkout scm
                        sh 'python3 -m pip install --upgrade pip'
                        sh 'python3 -m pip install -r requirements.txt'
                    }
                }
                
                stage('Build Docker Image') {
                    steps {
                        sh 'docker build -t ${DOCKER_IMAGE} .'
                    }
                }
            }
        }
        
        // ========== TEST SECTION ==========
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'python3 -m pytest --junitxml=test-results.xml'
                    }
                    post {
                        always {
                            junit 'test-results.xml'
                        }
                    }
                }
                
                stage('Code Quality Analysis') {
                    steps {
                        sh 'pylint --exit-zero app.py test_app.py > pylint-report.txt || true'
                        sh 'bandit -r . -f txt -o bandit-report.txt || true'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: '*-report.txt', fingerprint: true
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        sh 'echo "Running security scan..."'
                        sh '''
                            docker run --rm \
                                -v $(pwd):/zap/wrk/:rw \
                                ghcr.io/zaproxy/zap-baseline:latest \
                                -t http://target-app:5000 \
                                -g /zap/wrk/gen.conf \
                                -r /zap/wrk/zap-report.html || true
                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'zap-report.html', fingerprint: true, allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        // ========== DEPLOY SECTION ==========
        stage('Deploy') {
            stages {
                stage('Authenticate GCP') {
                    steps {
                        withCredentials([file(credentialsId: 'gcp-service-account-key', variable: 'GCP_KEY_FILE')]) {
                            sh 'gcloud auth activate-service-account --key-file=${GCP_KEY_FILE}'
                            sh 'gcloud config set project ${GCP_PROJECT_ID}'
                            sh 'gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev'
                        }
                    }
                }
                
                stage('Push Docker Image') {
                    steps {
                        sh 'docker push ${DOCKER_IMAGE}'
                    }
                }
                
                stage('Deploy to GKE') {
                    steps {
                        sh 'gcloud container clusters get-credentials ${GKE_CLUSTER} --zone=${GCP_ZONE}'
                        sh '''
                            kubectl create namespace ${KUBE_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                            kubectl set image deployment/python-app python-app=${DOCKER_IMAGE} -n ${KUBE_NAMESPACE}
                            kubectl rollout status deployment/python-app -n ${KUBE_NAMESPACE} --timeout=300s
                        '''
                    }
                }
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