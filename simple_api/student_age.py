#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for
from flask_httpauth import HTTPBasicAuth
from flask import g, session, redirect, url_for
from flask_simpleldap import LDAP
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
import json
import os
import time
import random


auth = HTTPBasicAuth()
app = Flask(__name__)
app.debug = True

metrics = PrometheusMetrics(app)
    
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

endpoints = ('one', 'two', 'three', 'four', 'five', 'error')


@app.route('/one')
def first_route():
    time.sleep(random.random() * 0.2)
    return 'ok'


@app.route('/two')
def the_second():
    time.sleep(random.random() * 0.4)
    return 'ok'


@app.route('/three')
def test_3rd():
    time.sleep(random.random() * 0.6)
    return 'ok'


@app.route('/four')
def fourth_one():
    time.sleep(random.random() * 0.8)
    return 'ok'


@app.route('/error')
def oops():
    return ':(', 500


Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@auth.get_password
def get_password(username):
    if username == 'toto':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


try:
    student_age_file_path
    student_age_file_path  = os.environ['student_age_file_path'] 
except NameError:
    student_age_file_path  = '/data/student_age.json'

student_age_file = open(student_age_file_path, "r")
student_age = json.load(student_age_file)

@app.route('/pozos/api/v1.0/get_student_ages', methods=['GET'])
@auth.login_required
def get_student_ages():
    return jsonify({'student_ages': student_age })

@app.route('/pozos/api/v1.0/get_student_ages/<student_name>', methods=['GET'])
@auth.login_required
def get_student_age(student_name):
    if student_name not in student_age :
        abort(404)
    if student_name in student_age :
      age = student_age[student_name]
      del student_age[student_name]
      with open(student_age_file_path, 'w') as student_age_file:
        json.dump(student_age, student_age_file, indent=4, ensure_ascii=False)
    return age 
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, threaded=True)
