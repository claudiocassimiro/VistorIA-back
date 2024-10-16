from flask import Blueprint, request, send_file, current_app
from flask_cors import CORS
import os
import json
from vistoria_back.image_descriptor import process_images
from datetime import datetime
from werkzeug.utils import secure_filename
from vistoria_back.utils.generate_pdf import generate_styled_pdf

upload_bp = Blueprint('upload', __name__)
CORS(upload_bp)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400
    
    files = request.files.getlist('file')
    vistoria_info = {
        'tipo_vistoria': request.form.get('tipo_vistoria', 'Não especificado'),
        'nome_edificio': request.form.get('nome_edificio', 'Não especificado'),
        'locador': request.form.get('locador', 'Não especificado'),
        'locatario': request.form.get('locatario', 'Não especificado'),
        'data_inicio': request.form.get('data_inicio', 'Não especificada'),
        'endereco_imovel': request.form.get('endereco_imovel', 'Não especificado'),
        'numero_apartamento': request.form.get('numero_apartamento', 'Não especificado'),
        'nome_vistoriador': request.form.get('nome_vistoriador', 'Vistoriador não identificado'),
        'observacoes_gerais': request.form.get('observacoes_gerais', '')
    }
    
    observacoes = json.loads(request.form.get('observacoes', '{}'))
    rooms = json.loads(request.form.get('rooms', '{}'))
    
    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_files.append(file_path)

    # Processa as imagens após o upload
    image_descriptions = process_images(current_app.config['UPLOAD_FOLDER'], observacoes)

    # Associa as descrições das imagens com as rooms corretas
    for desc in image_descriptions:
        file_name = desc['image']
        comodo, index = file_name.split('_')[:2]
        chave = f"{comodo}_{index}"
        desc['room'] = next((room for room, value in rooms.items() if chave.lower().replace(' ', '').replace('-', '').replace('_', '').translate(str.maketrans('', '', 'áéíóúâêîôûãõàèìòùäëïöüç')).startswith(value.lower().replace(' ', '').replace('-', '').replace('_', '').translate(str.maketrans('', '', 'áéíóúâêîôûãõàèìòùäëïöüç')))), 'Cômodo não especificado')
        desc['observacao'] = observacoes.get(chave, '')

    # Agrupa descrições por cômodo
    grouped_rooms = {}
    for desc in image_descriptions:
        room = desc['room']
        if room not in grouped_rooms:
            grouped_rooms[room] = []
        grouped_rooms[room].append(desc)

    # Gera o PDF
    pdf_buffer = generate_styled_pdf(grouped_rooms, vistoria_info, current_app)
    
    # Exclui as imagens da pasta 'uploads' após retornar o PDF
    for file_path in uploaded_files:
        os.remove(file_path)
    
    # Retorna o PDF como um arquivo para download
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"vistoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mimetype='application/pdf'
    )

def init_app(app):
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # Aumenta o limite de tamanho do upload para 1GB
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.register_blueprint(upload_bp)
