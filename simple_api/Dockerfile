FROM python:2.7-stretch

LABEL authors="franckkoukougnon@gmail.com,lambert.tedaldi@gmail.com,guyduche@gmail.com"

RUN apt-get update -y && apt-get install python-dev python3-dev libsasl2-dev python-dev libldap2-dev libssl-dev -y

RUN pip install Flask==1.1.4 Flask-HTTPAuth==4.3.0 Flask-SimpleLDAP==1.4.0 python-dotenv==0.17.1 prometheus-flask-exporter prometheus_client uwsgi

RUN mkdir /data

COPY student_age.py /

EXPOSE 5000 

CMD [ "python", "./student_age.py" ]
