from flask import Flask
from flasgger import Swagger
from vm_api import vm_bp
from function_api import function_bp

app = Flask(__name__)

# Load Swagger from file
swagger = Swagger(app, template_file="swagger.yaml")

# Register blueprints
app.register_blueprint(vm_bp, url_prefix="/api/v1")
app.register_blueprint(function_bp, url_prefix="/api/v1")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
