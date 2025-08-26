from flask import Blueprint, request, jsonify
import uuid

vm_bp = Blueprint("vm_api", __name__)

# In-memory store
VM_STORE = {}

@vm_bp.route("/vm", methods=["POST"])
def create_vm():
    data = request.get_json()
    vm_id = f"{data['name']}_{uuid.uuid4().hex[:8]}"
    VM_STORE[vm_id] = {**data, "vm_id": vm_id}
    return jsonify(VM_STORE[vm_id])

@vm_bp.route("/vm", methods=["GET"])
def list_vms():
    return jsonify(list(VM_STORE.values()))

@vm_bp.route("/vm/<vm_id>", methods=["GET"])
def get_vm(vm_id):
    return jsonify(VM_STORE.get(vm_id, {"error": "not found"}))

@vm_bp.route("/vm/<vm_id>", methods=["POST"])
def edit_vm(vm_id):
    if vm_id not in VM_STORE:
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    VM_STORE[vm_id].update(data)
    return jsonify(VM_STORE[vm_id])

@vm_bp.route("/vm/<vm_id>", methods=["DELETE"])
def delete_vm(vm_id):
    if vm_id not in VM_STORE:
        return jsonify({"error": "not found"}), 404
    deleted = VM_STORE.pop(vm_id)
    return jsonify({"vm_id": vm_id, "status": "deleted", "name": deleted["name"]})
