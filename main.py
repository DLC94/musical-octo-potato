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
	data = json.loads(request.data.decode('utf-8'))
	mem = data.get('memory', '128')
	func_id = str(uuid.uuid4())
	func_path = os.path.join(FUNCTIONS_DIR, func_id)
	os.makedirs(func_path, exist_ok=True)

	with open(os.path.join(func_path, 'handler.py'), 'w') as f:
		f.write(data['code'])
	with open(os.path.join(func_path, 'event.json'), 'w') as f:
		json.dump(data['event'],f)

	functions[func_id] = {
		"id": func_id,
		"memory": mem,
		"path": func_path
	}

	return jsonify({"message": "Function created", "id": func_id})

@app.route('/function/<id>')
def get_function(func_id):
	if func_id not in functions:
		return jsonify({"error": "Function not found"}), 404
	return jsonify(functions[func_id])

@app.route('/test/<id>', methods=['POST'])
def test_function(id):
	if id not in functions:
		return jsonify({"error": "Function not found"}), 404

	func_info = functions[id]
	func_path = func_info['path']

	try:
		# result = subprocess.run(
		# 	['./run_microvm.sh', func_path],
		# 	stdout=subprocess.PIPE
		# 	stderr=subprocess.PIPE,
		# 	timeout=10
		# )

		# return jsonify({
		# 	'stdout': result.stdout.decode(),
		# 	'stderr': result.stderr.decode(),
		# 	'exit_code': result.returncode
		# })
		print(func_info)
		return jsonify({'hello': 'world'})
	except subprocess.TimeoutExpired:
		return jsonify({'error':'Function execution timeout'}), 504