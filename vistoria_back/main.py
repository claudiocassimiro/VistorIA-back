from flask import Flask
from flask_cors import CORS
from vistoria_back.routes.upload_bp import init_app as init_upload_bp

app = Flask(__name__)
CORS(app)

# Inicializa o blueprint de upload
init_upload_bp(app)

if __name__ == '__main__':
    app.run(debug=True)