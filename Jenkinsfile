
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "your-dockerhub-username/CI-CD-Pipeline:${env.BUILD_NUMBER}"
        KUBE_NAMESPACE = "Python-CI-CD"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Set up Python') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'pytest --junitxml=test-results.xml'
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
                // Simulating AppScan with OWASP ZAP
                sh 'echo "Running security scan (simulating AppScan with ZAP)..."'
                sh 'docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py \
                    -t http://target-app:5000 -g gen.conf -r zap-report.html || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap-report.html', fingerprint: true
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build(DOCKER_IMAGE)
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
                        docker.image(DOCKER_IMAGE).push()
                    }
                }
            }
        }
        
        stage('Trigger ArgoCD Sync') {
            steps {
                // This would trigger ArgoCD to sync with the new image
                sh """
                curl -X POST \
                -H "Authorization: Bearer \$(cat /var/run/argocd/auth-token)" \
                -H "Content-Type: application/json" \
                -d '{
                    "prune": true,
                    "dryRun": false,
                    "resources": null,
                    "syncStrategy": {
                        "hook": {
                            "force": false
                        }
                    },
                    "retryStrategy": {
                        "limit": 2,
                        "backoff": {
                            "duration": "5s",
                            "factor": 2,
                            "maxDuration": "30s"
                        }
                    }
                }' \
                "https://argocd.lordemmag.com/api/v1/applications/python-demo/sync"
                """
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            slackSend(color: "good", message: "Build SUCCESSFUL: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        failure {
            slackSend(color: "danger", message: "Build FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
    }
}
