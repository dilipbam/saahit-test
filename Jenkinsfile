// pipeline {
//     agent any

//     environment {
//         registry = "dilipbam/saahitt-customer"
//         registryCredential = "dockerhub"
//     }

//     stages {
//         stage('Checkout') {
//             steps {
//                 checkout scm
//             }
//         }
//         stage('Build Customer Image') {
//             steps {
//                 script {
//                     dockerImage = docker.build("${env.registry}:V${env.BUILD_NUMBER}", "--build-arg SERVICE=customer_app .")
//                 }
//             }
//         }
//         stage('Upload Customer Image') {
//             steps {
//                 script {
//                     docker.withRegistry('', env.registryCredential) {
//                         dockerImage.push("V${env.BUILD_NUMBER}")
//                         dockerImage.push('latest')
//                     }
//                 }
//             }
//         }
//     }

//     post {
//         always {
//             cleanWs()
//         }
//     }
// }
// pipeline {
//     agent any

//     environment {
//         registry = "dilipbam/saahitt-customer"
//         registryCredential = "dockerhub"  // Ensure this is the ID of the credential you created
//     }

//     stages {
//         stage('Checkout') {
//             steps {
//                 checkout scm
//             }
//         }
//         stage('Build Customer Image') {
//             steps {
//                 script {
//                     dockerImage = docker.build("${env.registry}:V${env.BUILD_NUMBER}", "--build-arg SERVICE=customer_app .")
//                 }
//             }
//         }
//         stage('Upload Customer Image') {
//             steps {
//                 script {
//                     docker.withRegistry('https://index.docker.io/v1/', env.registryCredential) {
//                         dockerImage.push("V${env.BUILD_NUMBER}")
//                         dockerImage.push('latest')
//                     }
//                 }
//             }
//         }
//     }

//     post {
//         always {
//             cleanWs()
//         }
//     }
// }
pipeline {
    agent any

    environment {
        dockerImage = 'saahitt-customer' // Replace with your Docker image name
        dockerHubRepo = 'dilipbam/saahitt-customer' // Replace with your Docker Hub repository path
        dockerTag = "${dockerImage}-${BUILD_NUMBER}" // Tag with Jenkins build number
        registryCredential = "dockerhub"
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
                    // Build the Docker image
                    sh "docker build -t ${dockerImage}:${dockerTag} ."
                }
            }
        }

        stage('Tag and Push Docker Image') {
            steps {
                script {
                    // Tag the Docker image
                    sh "docker tag ${dockerImage}:${dockerTag} ${dockerHubRepo}:${dockerTag}"
                    
                    // Log in to Docker Hub
                    sh "echo ${DOCKER_HUB_PASSWORD} | docker login -u ${DOCKER_HUB_USERNAME} --password-stdin"

                    // Push the Docker image to Docker Hub
                    sh "docker push ${dockerHubRepo}:${dockerTag}"
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace
            cleanWs()
        }
    }
}
