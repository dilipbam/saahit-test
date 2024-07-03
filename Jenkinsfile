// pipeline {
//     agent any

//     environment {
//         registry = "diliipbam/saahitt-test"
//         registryCredential = "dockerhub"
//     }

//     stages {
//         stage('Checkout') {
//             steps {
//                 checkout scm
//             }
//         }
//         stage('Docker Build customer') {
//         agent any
//         steps {
//                 sh 'docker build -t diliipbam/saahitt-test:latest .'
//             }
//         }
//         stage('Docker Push') {
//         agent any
//         steps {
//         withCredentials([usernamePassword(credentialsId: 'dockerhub', passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
//           sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPassword}"
//           sh 'docker push diliipbam/saahitt-test:latest'
//         }
//       }
//     }
//   }
// }
pipeline {
    agent any

    environment {
        registry = "diliipbam"
        registryCredential = "dockerhub"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Docker Compose') {
            steps {
                sh '''
                   curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                   chmod +x /usr/local/bin/docker-compose
                   ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
                   docker-compose --version
                '''
            }
        }

        stage('Pull Latest Images') {
            steps {
                script {
                    // Pull the latest versions of Postgres and Redis
                    sh 'docker pull postgres:15'
                    sh 'docker pull redis:5.0.4'
                }
            }
        }

        stage('Docker Compose Build and Push') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: registryCredential, passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
                        sh "docker login -u ${dockerHubUser} -p ${dockerHubPassword}"
                        sh 'docker-compose build'
                        sh 'docker-compose push'
                    }
                }
            }
        }
    }
}
