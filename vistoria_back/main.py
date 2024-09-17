from flask import Flask, request, send_file
from flask_cors import CORS  # Importe o CORS
import os
from image_descriptor import process_images
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Adicione esta linha para habilitar CORS para toda a aplicação

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
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
        'nome_vistoriador': request.form.get('nome_vistoriador', 'Vistoriador não identificado')
    }
    
    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_files.append(file_path)
    
    # Processa as imagens após o upload
    image_descriptions = process_images(app.config['UPLOAD_FOLDER'])
    
    # Gera o PDF
    pdf_buffer = generate_pdf(image_descriptions, vistoria_info)
    
    # Exclui as imagens da pasta 'uploads'
    for file_path in uploaded_files:
        os.remove(file_path)
    
    # Retorna o PDF como um arquivo para download
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"vistoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mimetype='application/pdf'
    )

def generate_pdf(image_descriptions, vistoria_info):
    buffer = BytesIO()
    
    # Cria o documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Adiciona cabeçalho com as informações
    elements.append(Paragraph(f"Vistoria de {vistoria_info['tipo_vistoria'].upper()}: {vistoria_info['nome_edificio']}", styles['Heading1']))
    elements.append(Paragraph(f"APARTAMENTO {vistoria_info['numero_apartamento']}", styles['Heading2']))
    elements.append(Paragraph(f"Vistoriador: {vistoria_info['nome_vistoriador']}", styles['Heading3']))
    elements.append(Paragraph(f"Locador: {vistoria_info['locador']}", styles['Normal']))
    elements.append(Paragraph(f"Locatário: {vistoria_info['locatario']}", styles['Normal']))
    data_inicio_formatada = datetime.strptime(vistoria_info['data_inicio'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%y')
    elements.append(Paragraph(f"Data de Início: {data_inicio_formatada}", styles['Normal']))
    elements.append(Paragraph(f"Endereço: {vistoria_info['endereco_imovel']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Agrupa descrições por cômodo
    rooms = {}
    for desc in image_descriptions:
        room = desc['room']
        if room not in rooms:
            rooms[room] = []
        rooms[room].append(desc)

    # Adiciona conteúdo para cada cômodo
    for room, descriptions in rooms.items():
        elements.append(Paragraph(room.upper(), styles['Heading2']))
        for i, desc in enumerate(descriptions, start=1):
            elements.append(Paragraph(f"{i}. {desc['description']}", styles['Normal']))
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], desc['image'])
            img = Image(img_path, width=200, height=150)
            elements.append(img)
            elements.append(Spacer(1, 12))

    # Salva o PDF no buffer
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)