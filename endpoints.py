from flask import Flask, request, jsonify
import uuid
import datetime

app = Flask(__name__)

# In-memory stores
vms = {}
functions = {}


# -----------------------------
# VM ENDPOINTS
# -----------------------------

@app.route("/api/v1/vm", methods=["POST"])
def create_vm():
    data = request.json
    vm_id = f"vm-{str(uuid.uuid4())[:8]}"
    vm = {
        "vm_id": vm_id,
        "status": "pending",
        "network": {
            "ip": "10.0.0.2",
            "ssh": {"username": "ubuntu", "port": 22}
        },
        "memory_mb": data.get("memory_mb", 2048),
        "cpu_cores": data.get("cpu_cores", 1),
        "storage": {"size_mb": data.get("disk_size", 1024)},
        "uptime_in_min": 0,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    vms[vm_id] = vm
    return jsonify(vm)


@app.route("/api/v1/vm", methods=["GET"])
def list_vms():
    return jsonify(list(vms.values()))


@app.route("/api/v1/vm/<vm_id>", methods=["GET"])
def get_vm(vm_id):
    vm = vms.get(vm_id)
    if not vm:
        return jsonify({"error": "VM not found"}), 404
    return jsonify(vm)


@app.route("/api/v1/vm/<vm_id>", methods=["POST"])
def edit_vm(vm_id):
    vm = vms.get(vm_id)
    if not vm:
        return jsonify({"error": "VM not found"}), 404

    data = request.json
    if "memory" in data:
        vm["memory_mb"] = data["memory"]
    if "cpu" in data:
        vm["cpu_cores"] = data["cpu"]

    vm["status"] = "pending"
    return jsonify(vm)


@app.route("/api/v1/vm/<vm_id>/start", methods=["POST"])
def start_vm(vm_id):
    vm = vms.get(vm_id)
    if not vm:
        return jsonify({"error": "VM not found"}), 404
    vm["status"] = "starting"
    return jsonify(vm)


@app.route("/api/v1/vm/<vm_id>/stop", methods=["POST"])
def stop_vm(vm_id):
    vm = vms.get(vm_id)
    if not vm:
        return jsonify({"error": "VM not found"}), 404
    vm["status"] = "stopped"
    return jsonify(vm)


@app.route("/api/v1/vm/<vm_id>", methods=["DELETE"])
def delete_vm(vm_id):
    vm = vms.pop(vm_id, None)
    if not vm:
        return jsonify({"error": "VM not found"}), 404
    return jsonify({"vm_id": vm_id, "status": "terminated"})


# -----------------------------
# FUNCTION ENDPOINTS
# -----------------------------

@app.route("/api/v1/function", methods=["POST"])
def create_function():
    data = request.json
    function_id = f"{data['name']}_{str(uuid.uuid4())[:8]}"
    fn = {
        "name": data["name"],
        "function_id": function_id,
        "runtime": data["runtime"],
        "memory_mb": data["memory_mb"],
        "cpu_cores": data["cpu_cores"],
        "code": data["code"],
        "timeout_sec": data["timeout_sec"]
    }
    functions[function_id] = fn
    return jsonify(fn)


@app.route("/api/v1/function", methods=["GET"])
def list_functions():
    summaries = [
        {"name": fn["name"], "function_id": fn["function_id"], "runtime": fn["runtime"], "memory_mb": fn["memory_mb"]}
        for fn in functions.values()
    ]
    return jsonify(summaries)


@app.route("/api/v1/function/<function_id>", methods=["GET"])
def get_function(function_id):
    fn = functions.get(function_id)
    if not fn:
        return jsonify({"error": "Function not found"}), 404
    return jsonify(fn)


@app.route("/api/v1/function/<function_id>", methods=["POST"])
def edit_function(function_id):
    fn = functions.get(function_id)
    if not fn:
        return jsonify({"error": "Function not found"}), 404

    data = request.json
    fn.update({k: v for k, v in data.items() if k in ["memory_mb", "cpu_cores", "code", "timeout_sec"]})
    return jsonify(fn)


@app.route("/api/v1/function/<function_id>", methods=["DELETE"])
def delete_function(function_id):
    fn = functions.pop(function_id, None)
    if not fn:
        return jsonify({"error": "Function not found"}), 404
    return jsonify({"name": fn["name"], "function_id": function_id, "status": "deleted"})


@app.route("/api/v1/function/<function_id>/invoke", methods=["POST"])
def invoke_function(function_id):
    fn = functions.get(function_id)
    if not fn:
        return jsonify({"error": "Function not found"}), 404

    event = request.json.get("event", {})
    # Simulation only: fake logs + dummy result
    logs = [
        "[+] Booted into microMV",
        "Hello world!!",
        "[+] Shutting down..."
    ]
    result = event.get("value", None)
    if isinstance(result, int):
        result = result * 2  # Fake "compute" logic

    return jsonify({
        "function_id": function_id,
        "status": "success",
        "logs": logs,
        "result": result
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
