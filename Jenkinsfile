pipeline {
    agent any

    environment {
        registry = "diliipbam/saahitt-test"
        registryCredential = "dockerhub"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Docker Build') {
        agent any
        steps {
                sh 'docker build -t diliipbam/saahitt-test:latest .'
            }
        }
        stage('Docker Push') {
        agent any
        steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
          sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPassword}"
          sh 'docker push diliipbam/saahitt-test:latest'
        }
      }
    }
  }
}
