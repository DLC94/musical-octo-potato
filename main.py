from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import json
import shutil
import subprocess

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

FUNCTIONS_DIR = '/tmp/functions'
os.makedirs(FUNCTIONS_DIR, exist_ok=True)

functions = {}

@app.route('/')
def root():
    # return list of functions
    return jsonify(list(functions.values()))

@app.route('/function', methods=['POST'])
def create_function():
    func_id = save_function(request)

    return jsonify({"message": "Function created", "id": func_id})

@app.route('/function/<fid>', methods=['POST','GET'])
def get_function(fid):
    if request.method == 'POST':
        fid = save_function(request)
    elif fid not in functions:
        return jsonify({"error": "Function not found"}), 404
    return jsonify(functions[fid])

@app.route('/test/<id>', methods=['POST'])
def test_function(id):
    if id not in functions:
        return jsonify({"error": "Function not found"}), 404

    func_info = functions[id]
    func_path = func_info['path']

    return jsonify({
        'stdout': 'output',
        'stderr': 'error',
        'exit_code': 'code',
        'logs': ['log1', 'log2', 'log3']
    })

    # try:
    #     result = subprocess.run(
    #         ['sudo','./run_microvm.sh', func_path],
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         timeout=10
    #     )

    #     logs = []

    #     with open('{}/vm-log.txt'.format(func_path),'r') as f:
    #         logs.append(f.readline())
    #         logs.append(f.readline())
    #         logs.append(f.readline())

    #         capture = False
    #         for l in f:
    #             l = l.strip()
    #             if l == '[+] Booted into microVM':
    #                 capture = True
    #             if capture == True:
    #                 logs.append(l)
    #             if l == '[+] Shutting down...':
    #                 capture = False
    #                 break

    #     return jsonify({
    #         'stdout': result.stdout.decode(),
    #         'stderr': result.stderr.decode(),
    #         'exit_code': result.returncode,
    #         'logs': logs
    #     })
    # except subprocess.TimeoutExpired:
    #     return jsonify({'error':'Function execution timeout'}), 504

def save_function(request):
    data = json.loads(request.data.decode('utf-8'))
    mem = data.get('memory', '128')
    func_id = data.get('id', str(uuid.uuid4()))
    func_path = os.path.join(FUNCTIONS_DIR, func_id)
    os.makedirs(func_path, exist_ok=True)

    with open(os.path.join(func_path, 'handler.py'), 'w') as f:
        f.write(data['code'])
    with open(os.path.join(func_path, 'event.json'), 'w') as f:
        json.dump(data['event'],f)

    functions[func_id] = {
        "id": func_id,
        "memory": mem,
        "path": func_path,
        "code": data['code'],
        "event": data['event']
    }
    return func_id