pipeline {
    environment {
        IMAGE_API = "filrouge_simple_api"
        IMAGE_WEBSITE = "filrouge_website"
        IMAGE_TAG = "latest"
        IMAGE_REPO = "guyduche"
        STAGING = "aurelien-staging"
        PRODUCTION = "aurelien-production"
    }
    agent none
    stages {
        stage('Clone repo') {
            agent any
            steps {
                script {
                    sh '''
                    git clone https://github.com/guyduche/student-list.git || echo "already cloned"
                    cd student-list || echo "already in student-list"
                    '''
                }
            }
        }
        stage('Build simple_api image') {
            agent any
            steps {
                script {
                    sh '''
                    cd simple_api
                    docker build -t $IMAGE_REPO/$IMAGE_API:$IMAGE_TAG .
                    '''
                }
            }
        }
        stage('Run simple_api') {
            agent any
            steps {
                script {
                    sh '''
                    docker run --name $IMAGE_API -v /home/centos/student-list/simple_api/student_age.json:/data/student_age.json -d -p 5000:5000 --network jenkins_default $IMAGE_REPO/$IMAGE_API:$IMAGE_TAG
                    sleep 5
                    '''
                }
            }
        }
        stage('Test simple_api') {
            agent any
            environment {
                STUDENT_AGE_LOGIN = credentials('student_ages')
            }
            steps {
                script {
                    sh '''
                        curl -u ${STUDENT_AGE_LOGIN} -X GET http://${IMAGE_API}:5000/pozos/api/v1.0/get_student_ages | grep -q "student_ages"
                    '''
                }
            }
        }
        stage('Clean simple_api Container') {
            agent any
            steps {
                script {
                    sh '''
                    docker rm -vf ${IMAGE_API}
                    '''
                }
            }
        }
    }
}