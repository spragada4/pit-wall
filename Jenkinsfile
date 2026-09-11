pipeline {
    agent any

    environment {
        IMAGE_NAME = "ghcr.io/spragada4/pit-wall"
        IMAGE_TAG  = "${env.GIT_COMMIT.take(7)}"
    }

    stages {
        stage('Free Practice: Lint') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            steps {
                sh '''
                    pip install -r requirements.txt
                    flake8 app --max-line-length=120 --exclude=app/tests
                '''
            }
        }

        stage('Free Practice: Test') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            steps {
                sh '''
                    pip install -r requirements.txt
                    pytest app/tests
                '''
            }
        }

        stage('Build') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'ghcr-credentials', usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_TOKEN')]) {
                    sh '''
                        echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                    '''
                }
            }
        }

                stage('Race Start: Canary Deploy') {
            steps {
                sh '''
                    docker stop pit-wall-canary || true
                    docker rm pit-wall-canary || true
                    docker run -d --name pit-wall-canary -p 8001:8000 ${IMAGE_NAME}:${IMAGE_TAG}
                    sleep 3
                '''
            }
        }

        stage('Safety Car: Health Gate') {
            steps {
                script {
                    def healthy = false
                    for (int i = 0; i < 5; i++) {
                        def status = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/health || true",
                            returnStdout: true
                        ).trim()
                        echo "Health check attempt ${i + 1}: HTTP ${status}"
                        if (status == "200") {
                            healthy = true
                            break
                        }
                        sleep 2
                    }
                    if (!healthy) {
                        sh '''
                            docker stop pit-wall-canary || true
                            docker rm pit-wall-canary || true
                        '''
                        error("Safety car deployed: canary failed health checks. Rolled back — production untouched.")
                    }
                }
            }
        }

        stage('Podium: Promote to Production') {
            steps {
                sh '''
                    docker stop pit-wall-app || true
                    docker rm pit-wall-app || true
                    docker stop pit-wall-canary || true
                    docker rm pit-wall-canary || true
                    docker run -d --name pit-wall-app -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }
    }
}