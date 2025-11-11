pipeline {
    agent any
    
    stages {
        stage('Hello World') {
            steps {
                echo 'Hello from Jenkins Pipeline!'
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Job Name: ${JOB_NAME}"
            }
        }
        
        stage('Check Tools') {
            steps {
                echo 'Checking available tools...'
                sh 'pwd'
                sh 'ls -la'
                sh 'python3 --version || echo "Python3 not found"'
                sh 'which python3 || echo "Python3 path not found"'
            }
        }
    }
    
    post {
        success {
            echo "✅ SUCCESS: Jenkins is working!"
        }
        failure {
            echo "❌ FAILED: Check the logs"
        }
    }
}