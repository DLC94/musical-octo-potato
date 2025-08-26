from flask import Blueprint, request, jsonify
import uuid

function_bp = Blueprint("function_api", __name__)

# In-memory store
FUNCTION_STORE = {}

@function_bp.route("/function", methods=["POST"])
def create_function():
    data = request.get_json()
    fid = f"{data['name']}_{uuid.uuid4().hex[:8]}"
    FUNCTION_STORE[fid] = {**data, "function_id": fid}
    return jsonify(FUNCTION_STORE[fid])

@function_bp.route("/function", methods=["GET"])
def list_functions():
    return jsonify(list(FUNCTION_STORE.values()))

@function_bp.route("/function/<function_id>", methods=["GET"])
def get_function(function_id):
    return jsonify(FUNCTION_STORE.get(function_id, {"error": "not found"}))

@function_bp.route("/function/<function_id>", methods=["POST"])
def edit_function(function_id):
    if function_id not in FUNCTION_STORE:
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    FUNCTION_STORE[function_id].update(data)
    return jsonify(FUNCTION_STORE[function_id])

@function_bp.route("/function/<function_id>", methods=["DELETE"])
def delete_function(function_id):
    if function_id not in FUNCTION_STORE:
        return jsonify({"error": "not found"}), 404
    deleted = FUNCTION_STORE.pop(function_id)
    return jsonify({"function_id": function_id, "status": "deleted", "name": deleted["name"]})

@function_bp.route("/function/<function_id>/invoke", methods=["POST"])
def invoke_function(function_id):
    if function_id not in FUNCTION_STORE:
        return jsonify({"error": "not found"}), 404
    
    event = request.json.get("event", {})
    logs = [
        "[+] Booted into microVM",
        f"Executing function {function_id}",
        "[+] Shutting down..."
    ]
    # Fake result
    result = {"echo_event": event}
    
    return jsonify({
        "function_id": function_id,
        "status": "success",
        "logs": logs,
        "result": result
    })
