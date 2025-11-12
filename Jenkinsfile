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