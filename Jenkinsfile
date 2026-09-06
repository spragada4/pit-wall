pipeline {
    agent any

    environment {
        IMAGE_NAME = "ghcr.io/spragada4/pit-wall"
        IMAGE_TAG  = "${env.GIT_COMMIT.take(7)}"
    }

    stages {
        stage('Free Practice: Lint') {
            steps {
                sh '''
                    python3 -m venv .ci-venv
                    . .ci-venv/bin/activate
                    pip install -r requirements.txt
                    flake8 app --max-line-length=120 --exclude=app/tests
                '''
            }
        }

        stage('Free Practice: Test') {
            steps {
                sh '''
                    . .ci-venv/bin/activate
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

        stage('Deploy') {
            steps {
                sh '''
                    docker stop pit-wall-app || true
                    docker rm pit-wall-app || true
                    docker run -d --name pit-wall-app -p 8000:8000 ${IMAGE_NAME}:latest
                '''
            }
        }
    }
}