pipeline {
    agent any

    environment {
        registry = "dilipbam/saahitt"
        registryCredential = "dockerhub"
    }

    stage('Build Customer Image') {
        steps{
            script {
                dockerImage = docker.build registry +  ":V$BUILD_NUMBER"
            }
        }
    }

    stage('Upload Customer Image'){
        steps {
            script {
                docker.withRegistry('',registryCredential){
                    dockerImage.push("V$BUILD_NUMBER")
                    dockerImage.push('latest')
                }
            }
        }
    }

    stage('Remove Unused docker image') {
        steps {
            sh "docker rmi $registry:V$BUILD_NUMBER"
        }
    }
        // stage('Checkout') {
        //     steps {
        //         checkout scm
        //     }
        // }
        // stage('Build and Push Customer Image') {
        //     steps {
        //         script {
        //             dockerImage = docker.build("${env.REGISTRY}/${env.IMAGE_NAME}-customer:${env.BUILD_ID}", "--build-arg SERVICE=customer .")
        //             docker.withRegistry("https://${env.REGISTRY}", "ghcr") {
        //                 dockerImage.push("latest")
        //             }
        //         }
        //     }
        // }
        // stage('Build and Push Venue Image') {
        //     steps {
        //         script {
        //             dockerImage = docker.build("${env.REGISTRY}/${env.IMAGE_NAME}-venue:${env.BUILD_ID}", "--build-arg SERVICE=venue .")
        //             docker.withRegistry("https://${env.REGISTRY}", "ghcr") {
        //                 dockerImage.push("latest")
        //             }
        //         }
        //     }
        // }
        // stage('Build and Push Super Admin Image') {
        //     steps {
        //         script {
        //             dockerImage = docker.build("${env.REGISTRY}/${env.IMAGE_NAME}-super_admin:${env.BUILD_ID}", "--build-arg SERVICE=super_admin .")
        //             docker.withRegistry("https://${env.REGISTRY}", "ghcr") {
        //                 dockerImage.push("latest")
        //             }
        //         }
        //     }
        // }
        // stage('Build and Push Postgres Image') {
        //     steps {
        //         script {
        //             dockerImage = docker.build("${env.REGISTRY}/${env.IMAGE_NAME}-postgres:${env.BUILD_ID}", "--build-arg SERVICE=postgres .")
        //             docker.withRegistry("https://${env.REGISTRY}", "ghcr") {
        //                 dockerImage.push("latest")
        //             }
        //         }
        //     }
        // }
    }
