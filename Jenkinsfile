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
// pipeline {
//     agent any

//     environment {
//         dockerImage = 'saahitt-customer' // Replace with your Docker image name
//         dockerHubRepo = 'dilipbam/saahitt-customer' // Replace with your Docker Hub repository path
//         dockerTag = "${dockerImage}-${BUILD_NUMBER}" // Tag with Jenkins build number
//         dockerHubCredentials = credentials('dockerhub')
//     }

//     stages {
//         stage('Checkout') {
//             steps {
//                 checkout scm
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 script {
//                     // Build the Docker image
//                     sh "docker build -t ${dockerImage}:${dockerTag} ."
//                 }
//             }
//         }

//         stage('Tag and Push Docker Image') {
//             steps {
//                 script {
//                     // Tag the Docker image
//                     sh "docker tag ${dockerImage}:${dockerTag} ${dockerHubRepo}:${dockerTag}"
                    
//                     // Log in to Docker Hub
//                     sh "echo ${DOCKER_HUB_PASSWORD} | docker login -u ${DOCKER_HUB_USERNAME} --password-stdin"

//                     // Push the Docker image to Docker Hub
//                     sh "docker push ${dockerHubRepo}:${dockerTag}"
//                 }
//             }
//         }
//     }

//     post {
//         always {
//             // Clean up workspace
//             cleanWs()
//         }
//     }
// }
// pipeline {
//     agent any

//     environment {
//         dockerImage = 'saahitt-customer' // Replace with your Docker image name
//         dockerHubRepo = 'dilipbam/saahitt-customer' // Replace with your Docker Hub repository path
//         dockerTag = "${dockerImage}-${BUILD_NUMBER}" // Dynamic versioning with Jenkins build number
//         dockerHubCredentials = credentials('dockerhub') // Use ID of credentials defined in Jenkins global configuration
//     }

//     stages {
//         stage('Checkout') {
//             steps {
//                 checkout scm
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 script {
//                     // Build the Docker image
//                     sh "docker build -t ${dockerImage}:${dockerTag} ."
//                 }
//             }
//         }

//         stage('Tag and Push Docker Image') {
//             steps {
//                 script {
//                     // Tag the Docker image
//                     sh "docker tag ${dockerImage}:${dockerTag} ${dockerHubRepo}:${dockerTag}"
                    
//                     // Log in to Docker Hub
//                     withCredentials([dockerHubCredentials]) {
//                         sh "docker login -u ${dockerHubCredentials.username} -p ${dockerHubCredentials.password}"
                        
//                         // Push the Docker image to Docker Hub
//                         sh "docker push ${dockerHubRepo}:${dockerTag}"
//                     }
//                 }
//             }
//         }
//     }

//     post {
//         always {
//             // Clean up workspace
//             cleanWs()
//         }
//     }
// }
pipeline {
    agent any

    environment {
        dockerImage = 'saahitt-customer' // Replace with your Docker image name
        dockerTag = "${dockerImage}-${BUILD_NUMBER}" // Dynamic versioning with Jenkins build number
        dockerHubRepo = 'dilipbam/saahitt-customer'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Build Docker image
                    sh "docker build -t ${dockerImage}:${dockerTag} ."

                    // Tag Docker image
                    sh "docker tag ${dockerImage}:${dockerTag} ${dockerHubRepo}:${dockerTag}"

                    // Authenticate and push to Docker Hub
                    withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_HUB_USERNAME', passwordVariable: 'DOCKER_HUB_PASSWORD')]) {
                        sh "docker login -u ${DOCKER_HUB_USERNAME} -p ${DOCKER_HUB_PASSWORD}"
                        sh "docker push ${dockerHubRepo}:${dockerTag}"
                    }
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
