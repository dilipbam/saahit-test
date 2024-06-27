pipeline {
    agent any

    environment {
        registry = "dilipbam/saahitt-customer"
        registryCredential = "dockerhub"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Customer Image') {
            steps {
                script {
                    dockerImage = docker.build("${env.registry}:V${env.BUILD_NUMBER}", "--build-arg SERVICE=customer .")
                }
            }
        }
        stage('Upload Customer Image') {
            steps {
                script {
                    docker.withRegistry('', env.registryCredential) {
                        dockerImage.push("V${env.BUILD_NUMBER}")
                        dockerImage.push('latest')
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
