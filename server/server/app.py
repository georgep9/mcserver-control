from flask import Flask, json, request, jsonify
from flask_cors import CORS
import os
import jwt
from datetime import datetime, timedelta

import manage_server


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

ec2_server = manage_server.Server()

def auth(auth_header):
    if (auth_header):
        token = auth_header.split(' ')[1]
    else:
        return "missing"

    try:
        jwt.decode(token, os.environ.get('LOGIN_PIN'), algorithms=["HS256"])
        token_status = "valid"
    except jwt.InvalidTokenError:
        token_status = "invalid"
    except jwt.ExpiredSignatureError:
        token_status = "expired"
    finally:
        return token_status

def check_access(auth_header):
    token_status = auth(auth_header)
    if token_status == "valid":
        return True, None
    else:
        return False, jsonify({
            'status': "error",
            'msg': f"Unauthorized access. Token is {token_status}."
        })

@app.route('/login', methods=["POST"]) 
def login():
    submitted_pin = request.json["pin"]
    if (submitted_pin == os.environ.get('LOGIN_PIN')):
        exp_time = datetime.utcnow() + timedelta(hours=1)
        status = "success"
        token = jwt.encode({"exp": exp_time}, os.environ.get('LOGIN_PIN'), algorithm="HS256")
    else:
        status = "error"
        token = ""
    return jsonify({
        'status': status,
        'token': token
    })

@app.route('/start', methods=['GET']) 
def start_server():
    permitted, res = check_access(request.headers.get("Authorization"))
    if not permitted:
        return res

    with ec2_server.start_lock and ec2_server.stop_lock:
        if ec2_server.start_state == "running":
            msg = "Server startup in progress"
        elif ec2_server.stop_state == "running":
            msg = "refresh"
        else:
            ec2_server.run_start_thread()
            msg = "Starting server"
        return jsonify({
            'status': "success",
            'msg': msg
        })

@app.route('/start_logs', methods=['GET']) 
def get_start_logs():
    permitted, res = check_access(request.headers.get("Authorization"))
    if not permitted:
        return res

    with ec2_server.start_lock:
        logs = ec2_server.start_logs
        done = True if ec2_server.start_state == "done" else False
    logs_json = json.dumps(logs)
    return jsonify({
        'status': "success",
        'logs': logs_json,
        'done': done
    })

@app.route('/stop', methods=['GET']) 
def stop_server():
    permitted, res = check_access(request.headers.get("Authorization"))
    if not permitted:
        return res

    with ec2_server.stop_lock and ec2_server.start_lock:
        if ec2_server.stop_state == "running":
            msg = "Server shutdown in progress"
        elif ec2_server.start_state == "running":
            msg = "refresh"
        else:
            ec2_server.run_stop_thread()
            msg = "Shutting down server"
        return jsonify({
            'status': "success",
            'msg': msg
        })

@app.route('/stop_logs', methods=['GET']) 
def get_stop_logs():
    permitted, res = check_access(request.headers.get("Authorization"))
    if not permitted:
        return res

    with ec2_server.stop_lock:
        logs = ec2_server.stop_logs
        done = True if ec2_server.stop_state == "done" else False
    logs_json = json.dumps(logs)
    return jsonify({
        'status': "success",
        'logs': logs_json,
        'done': done
    })

@app.route('/status', methods=['GET'])
def get_status():
    permitted, res = check_access(request.headers.get("Authorization"))
    if not permitted:
        return res

    server_status = ec2_server.current_status()
    return jsonify({
        'status': "success",
        'server_status': json.dumps(server_status)
    })

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)