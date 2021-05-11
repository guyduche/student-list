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
        stage('Build images') {
            agent any
            steps {
                script {
                    sh '''
                    cd simple_api
                    docker build -t $IMAGE_REPO/$IMAGE_API:$IMAGE_TAG .
                    cd ../website
                    docker build -t $IMAGE_REPO/$IMAGE_WEBSITE:$IMAGE_TAG .
                    '''
                }
            }
        }
        stage('Run containers') {
            agent any
            steps {
                script {
                    sh '''
                    docker run --name $IMAGE_API -v /home/centos/student-list/simple_api/student_age.json:/data/student_age.json -d -p 5000:5000 --network jenkins_default $IMAGE_REPO/$IMAGE_API:$IMAGE_TAG
                    docker run --name $IMAGE_WEBSITE -v /home/centos/student-list/website:/var/www/html -d -p 80:80 --network jenkins_default $IMAGE_REPO/$IMAGE_WEBSITE:$IMAGE_TAG
                    sleep 5
                    '''
                }
            }
        }
        stage('Test') {
            agent any
            environment {
                STUDENT_AGE_LOGIN = credentials('student_ages')
            }
            steps {
                script {
                    sh '''
                        curl -u ${STUDENT_AGE_LOGIN} -X GET http://${IMAGE_WEBSITE} | grep -q "Student Checking"
                        curl -u ${STUDENT_AGE_LOGIN} -X GET http://${IMAGE_API}:5000/pozos/api/v1.0/get_student_ages | grep -q "student_ages"
                    '''
                }
            }
        }
        stage('Clean Containers') {
            agent any
            steps {
                script {
                    sh '''
                        docker rm -vf ${IMAGE_API} ${IMAGE_WEBSITE}
                    '''
                }
            }
        }
        stage('Clone on clients') {
            agent { docker { image 'dirane/docker-ansible:latest' } }
            environment {
                VAULT_PASSWORD = credentials('vault_password')
            }
            steps {
                script {
                    sh '''
                        cd ansible
                        echo ${VAULT_PASSWORD} > .passvault
                        ansible-playbook -i clients.yml install.yml --vault-password-file=.passvault
                        rm -rf student-list/.git .passvault
                    '''
                }
            }
        }
        stage('Deploy on clients') {
            agent { docker { image 'dirane/docker-ansible:latest' } }
            environment {
                VAULT_PASSWORD = credentials('vault_password')
            }
            steps {
                script {
                    sh '''
                        cd ansible
                        echo ${VAULT_PASSWORD} > .passvault
                        ansible-playbook -i clients.yml student_list.yml --vault-password-file=.passvault
                        rm .passvault
                    '''
                }
            }
        }
        stage('Test clients') {
            agent { docker { image 'dirane/docker-ansible:latest' } }
            environment {
                VAULT_PASSWORD = credentials('vault_password')
            }
            steps {
                script {
                    sh '''
                        cd ansible
                        echo ${VAULT_PASSWORD} > .passvault
                        ansible-playbook -i clients.yml test.yml --vault-password-file=.passvault
                        rm .passvault
                    '''
                }
            }
        }
    }
}