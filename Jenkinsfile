
pipeline {
    agent any

    environment {
        IMAGE_NAME = "fastapi-app"
        IMAGE_TAG = "latest"
        REGISTRY = "docker.io/yourdockerhubusername"
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/yourusername/fastapi-app.git'
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t $REGISTRY/$IMAGE_NAME:$IMAGE_TAG .'
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm $REGISTRY/$IMAGE_NAME:$IMAGE_TAG pytest test_main.py'
            }
        }

        stage('Security Scan') {
            steps {
                echo 'Running AppScan... (this is a placeholder)'
                // Replace with actual AppScan CLI if needed
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push $REGISTRY/$IMAGE_NAME:$IMAGE_TAG'
                }
            }
        }

        stage('Deploy with ArgoCD') {
            steps {
                echo 'ArgoCD will auto-deploy the new image to Kubernetes'
                // Optional: update Helm values or GitOps repo if necessary
            }
        }
    }
}

