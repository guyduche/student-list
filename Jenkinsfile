pipeline {
    environment {
        IMAGE_API = "filrouge_simple_api"
        IMAGE_WEBSITE = "filrouge_website"
        IMAGE_TAG = "latest"
        IMAGE_REPO = "guyduche"
    }
    agent none
    stages {
        stage('Clone repo') {
            agent any
            environment {
                GITHUB_CRED = credentials('github_http')
            }
            steps {
                script {
                    sh '''
                    git clone https://${GITHUB_CRED}@github.com/guyduche/student-list.git || echo "already cloned"
                    '''
                }
            }
        }
        stage('Build images') {
            agent any
            steps {
                script {
                    sh '''
                    docker build -t $IMAGE_REPO/$IMAGE_API:$IMAGE_TAG student-list/simple_api
                    docker build -t $IMAGE_REPO/$IMAGE_WEBSITE:$IMAGE_TAG student-list/website
                    '''
                }
            }
        }
        stage('Run containers') {
            agent any
            environment {
                API_CRED = credentials('student_list')
            }
            steps {
                script {
                    sh '''
                    docker run --name $IMAGE_API -v /home/centos/student-list/simple_api/student_age.json:/data/student_age.json -d -p 5000:5000 --network jenkins_default $IMAGE_REPO/$IMAGE_API:$IMAGE_TAG
                    docker run --name $IMAGE_WEBSITE -v /home/centos/student-list/website:/var/www/html -d -e USERNAME=${API_CRED_USR} -e PASSWORD=${API_CRED_PSW} -p 80:80 --network jenkins_default $IMAGE_REPO/$IMAGE_WEBSITE:$IMAGE_TAG
                    sleep 5
                    '''
                }
            }
        }
        stage('Test') {
            agent any
            steps {
                script {
                    sh '''
                        curl -d "submit=yes" $IMAGE_WEBSITE | grep -q "alice"
                    '''
                }
            }
        }
        stage('Clean') {
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
                GITHUB_CRED = credentials('github_http')
            }
            steps {
                script {
                    sh '''
                        cd ansible
                        ansible-playbook -i clients.yml install.yml -e "github_cred=${GITHUB_CRED}"
                    '''
                }
            }
        }
        stage('Deploy on clients') {
            agent { docker { image 'dirane/docker-ansible:latest' } }
            environment {
                DOCKERHUB_CRED = credentials('dockerhub')
                API_CRED = credentials('student_list')
            }
            steps {
                script {
                    sh '''
                        cd ansible
                        ansible-playbook -i clients.yml student_list.yml -e "dockerhub_username=${DOCKERHUB_CRED_USR} dockerhub_password=${DOCKERHUB_CRED_PSW} api_username=${API_CRED_USR} api_password=${API_CRED_PSW}"
                    '''
                }
            }
        }
        stage('Test clients') {
            agent { docker { image 'dirane/docker-ansible:latest' } }
            steps {
                script {
                    sh '''
                        cd ansible
                        ansible-playbook -i clients.yml test.yml
                    '''
                }
            }
        }
        stage('Clean clients') {
            agent { docker { image 'dirane/docker-ansible:latest' } }
            steps {
                script {
                    sh '''
                        cd ansible
                        ansible-playbook -i clients.yml clean.yml
                    '''
                }
            }
        }
    }
}