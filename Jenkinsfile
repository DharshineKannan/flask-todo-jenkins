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
                sh 'docker network inspect shared-net >/dev/null 2>&1 || docker network create shared-net'
                sh 'docker network connect shared-net "$HOSTNAME" 2>/dev/null || true'
                sh 'docker compose -p todo-app down'
                sh 'docker compose -p todo-app up -d'
            }
        }
        stage('Smoke Test') {
            steps {
                sh '''
                    for attempt in 1 2 3 4 5 6; do
                        response=$(curl -fsS http://web:5000/health 2>/dev/null || true)
                        if [ "$response" = '{"status":"healthy"}' ]; then
                            exit 0
                        fi
                        sleep 5
                    done
                    echo "Health check failed: ${response:-no response}"
                    exit 1
                '''
            }
        }
    }
    post {
        failure {
            sh 'docker compose -p todo-app down'
        }
    }
}
