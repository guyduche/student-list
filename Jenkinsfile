pipeline {
    environment {
        IMAGE_API = "filrouge-simple-api"
        IMAGE_WEBSITE = "filrouge-website"
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
                        docker build -t $IMAGE_API student-list/simple_api
                        docker build -t $IMAGE_WEBSITE student-list/website
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
                        export HOST_ADDRESS=`docker run --rm --net=host alpine ifconfig ens33 | grep \"inet addr\" | tr -d [a-zA-Z:] | tr -s \" \" | cut -f 2 -d \" \"`
                        docker run --name $IMAGE_API -v /home/centos/student-list/simple_api/student_age.json:/data/student_age.json -d -p 5000:5000 --network jenkins_default $IMAGE_API
                        docker run --name $IMAGE_WEBSITE -v /home/centos/student-list/website:/var/www/html -d -e USERNAME=${API_CRED_USR} -e PASSWORD=${API_CRED_PSW} -e IPADDRESS=${HOST_ADDRESS} -p 80:80 --network jenkins_default $IMAGE_WEBSITE
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
        stage('Push on private registry') {
            agent any
            steps {
                script {
                    sh '''
                        docker run --name registry -d -p 5001:5000 registry:2 || echo "There's already a registry"
                        docker tag ${IMAGE_API} localhost:5001/${IMAGE_API}
                        docker tag ${IMAGE_WEBSITE} localhost:5001/${IMAGE_WEBSITE}
                        docker push localhost:5001/${IMAGE_API}
                        docker push localhost:5001/${IMAGE_WEBSITE}
                    '''
                }
            }
        }
        stage('Install ansible on Jenkins docker') {
            agent any
            steps {
                script {
                    sh '''
                        yum install -y python3 sshpass
                        curl --silent --show-error --retry 5 https://bootstrap.pypa.io/pip/2.7/get-pip.py | python
                        pip install ansible
                    '''
                }
            }
        }
        stage('Clone on clients') {
            agent any
            environment {
                GITHUB_CRED = credentials('github_http')
            }
            steps {
                script {
                    sh '''
                        export HOST_ADDRESS=`docker run --rm --net=host alpine ifconfig ens33 | grep \"inet addr\" | tr -d [a-zA-Z:] | tr -s \" \" | cut -f 2 -d \" \"`
                        cd ansible
                        ansible-playbook -i clients.yml install.yml -e "github_cred=${GITHUB_CRED} host_address=${HOST_ADDRESS}"
                    '''
                }
            }
        }
        stage('Deploy on clients') {
            agent any
            environment {
                API_CRED = credentials('student_list')
            }
            steps {
                script {
                    sh '''
                        export HOST_ADDRESS=`docker run --rm --net=host alpine ifconfig ens33 | grep \"inet addr\" | tr -d [a-zA-Z:] | tr -s \" \" | cut -f 2 -d \" \"`
                        cd ansible
                        ansible-playbook -i clients.yml student_list.yml -e "host_address=${HOST_ADDRESS} api_username=${API_CRED_USR} api_password=${API_CRED_PSW}"
                    '''
                }
            }
        }
        stage('Test clients') {
            agent any
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
            agent any
            steps {
                script {
                    sh '''
                        export HOST_ADDRESS=`docker run --rm --net=host alpine ifconfig ens33 | grep \"inet addr\" | tr -d [a-zA-Z:] | tr -s \" \" | cut -f 2 -d \" \"`
                        cd ansible
                        ansible-playbook -i clients.yml clean.yml -e "host_address=${HOST_ADDRESS}"
                    '''
                }
            }
        }
        stage('Push images on Dockerhub') {
            agent any
            environment {
                DOCKERHUB_CRED = credentials('dockerhub')
            }
            steps {
                script {
                    sh '''
                        docker tag ${IMAGE_API} guyduche/filrouge:simple-api
                        docker tag ${IMAGE_WEBSITE} guyduche/filrouge:website
                        docker login -u ${DOCKERHUB_CRED_USR} -p ${DOCKERHUB_CRED_PSW}
                        docker push guyduche/filrouge:simple-api
                        docker push guyduche/filrouge:website
                        docker rmi ${IMAGE_API} ${IMAGE_WEBSITE}
                    '''
                }
            }
        }
        stage('Clone on workers') {
            agent any
            environment {
                GITHUB_CRED = credentials('github_http')
            }
            steps {
                script {
                    sh '''
                        export HOST_ADDRESS=`docker run --rm --net=host alpine ifconfig ens33 | grep \"inet addr\" | tr -d [a-zA-Z:] | tr -s \" \" | cut -f 2 -d \" \"`
                        cd k8s/ansible
                        ansible-playbook -i hosts.yml clone.yml -e "github_cred=${GITHUB_CRED}"
                    '''
                }
            }
        }
        stage('Deploy on Kubernetes cluster') {
            agent any
            steps {
                script {
                    sh '''
                        export HOST_ADDRESS=`docker run --rm --net=host alpine ifconfig ens33 | grep \"inet addr\" | tr -d [a-zA-Z:] | tr -s \" \" | cut -f 2 -d \" \"`
                        ssh -tt centos@${HOST_ADDRESS} /bin/bash <<'EOT'
                        cd student-list/k8s
                        kubectl replace -f simple-api-deployment.yml --force
                        kubectl replace -f website-deployment.yml --force
                        exit
                        EOT
                    '''
                }
            }
        }
    }
}