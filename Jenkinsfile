
pipeline {
    agent any

    environment {
        registry = "diliipbam/test"
        registryCredential = "dockerhub"
    }
    triggers {
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t diliipbam/test:latest .'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('', registryCredential) {
                        docker.image("${registry}:latest").push()
                    }
                }
            }
        }
    }
}
