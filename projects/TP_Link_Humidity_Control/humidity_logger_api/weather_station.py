"""
Demo Flask application to log temprature and humidity from RaspveryPi and show log using socket.io
"""

# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, jsonify, render_template, url_for, copy_current_request_context, request, redirect
from flask_cors import CORS
from random import random
from time import sleep
from threading import Thread, Event
import datetime
import os

__author__ = 'Suryakand Shinde'

app = Flask(__name__)
CORS(app, support_credentials=True)

# MySQL Setup
from flaskext.mysql import MySQL
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = os.environ['MYSQL_DATABASE_HOST'] 
app.config['MYSQL_DATABASE_PORT'] = int(os.environ['MYSQL_DATABASE_PORT'])
app.config['MYSQL_DATABASE_USER'] = os.environ['MYSQL_DATABASE_USER'] 
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['MYSQL_DATABASE_PASSWORD']
app.config['MYSQL_DATABASE_DB'] = os.environ['MYSQL_DATABASE_DB']
mysql.init_app(app)

app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app)

# app.run(debug=False)

@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@app.route('/temprature', methods=['GET'])
def showTemprature():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ws_temprature")
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {'id': result[0], 'date': result[1], 'temprature': result[2]}
        payload.append(content)
        content = {}
    cursor.close()

    return jsonify(payload)

@app.route('/temprature', methods=['POST'])
def logTemprature():
    content = request.get_json()
    temprature = content['temprature']
    time = datetime.datetime.now()

    #Emit Update for clients
    socketio.emit('temprature', {'temprature': temprature, "time": time.strftime("%m/%d/%Y, %H:%M:%S")}, namespace='/io-temprature')
    
    # Save to DB
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ws_temprature(dt_created, temprature) VALUES(%s,%s)",(datetime.datetime.now(), temprature))
    #commit to DB
    conn.commit()
    cursor.close()
    return jsonify({"status": 200, "content": content})

@app.route('/humidity', methods=['GET'])
def showHumidity():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ws_humidity")
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {'id': result[0], 'date': result[1], 'humidity': result[2]}
        payload.append(content)
        content = {}
    cursor.close()

    return jsonify(payload)

@app.route('/humidity', methods=['POST'])
def logHumidity():
    content = request.get_json()
    humidity = content['humidity']
    time = datetime.datetime.now()

    #Emit Update for clients
    socketio.emit('humidity', {'humidity': humidity, 'time': time.strftime("%m/%d/%Y, %H:%M:%S")}, namespace='/io-humidity')

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ws_humidity(dt_created, humidity) VALUES(%s,%s)",(time, humidity))
    #commit to DB
    conn.commit()
    cursor.close()

    return jsonify({"status": 200, "content": content})

@socketio.on('connect', namespace='/io-temprature')
def temprature_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected to /io-temprature')

@socketio.on('disconnect', namespace='/io-temprature')
def temprature_disconnect():
    print('Client disconnected from /io-temprature')


@socketio.on('connect', namespace='/io-humidity')
def humidity_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected to /io-humidity')

@socketio.on('disconnect', namespace='/io-humidity')
def humidity_disconnect():
    print('Client disconnected from /io-humidity')

if __name__ == '__main__':
    # app.run()
    socketio.run(app)