pipeline {
    agent any
    stages {
        stage('Clone') {
            steps {
                git url: 'https://github.com/DharshineKannan/flask-todo-jenkins.git', branch: 'main'
            }
        }
        stage('Build') {
            steps {
                withCredentials([string(credentialsId: 'db-password', variable: 'DB_PASS')]) {
                    sh 'echo "DB_PASSWORD=$DB_PASS" > .env'
                    sh 'docker compose -p todo-app build'
                }
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker compose -p todo-app down'
                sh 'docker compose -p todo-app up -d'
            }
        }
        stage('Smoke Test') {
            steps {
                sh 'sleep 5'
                sh 'curl -f http://todo-app:5000/ || exit 1'
            }
        }
    }
    post {
        failure {
            sh 'docker compose -p todo-app down'
        }
    }
}
