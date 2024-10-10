from flask import Flask, request, send_file
from flask_cors import CORS
import os
import json
from image_descriptor import process_images
from reportlab.lib.pagesizes import letter
from io import BytesIO
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Aumenta o limite de tamanho do upload para 1GB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

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
    
    observacoes = json.loads(request.form.get('observacoes', '{}'))
    rooms = json.loads(request.form.get('rooms', '{}'))
    
    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_files.append(file_path)

    # Processa as imagens após o upload
    image_descriptions = process_images(app.config['UPLOAD_FOLDER'], observacoes)

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
    pdf_buffer = generate_styled_pdf(grouped_rooms, vistoria_info)
    
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

def generate_styled_pdf(rooms, vistoria_info):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()

    # Definindo estilos personalizados
    header_style = ParagraphStyle(
        'HeaderStyle',
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor('#0073e6')
    )

    subheader_style = ParagraphStyle(
        'SubHeaderStyle',
        fontSize=12,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=10,
        textColor=colors.HexColor('#005bb5')
    )

    normal_style = ParagraphStyle(
        'NormalStyle',
        fontSize=10,
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=8
    )

    elements = []

    # Adiciona cabeçalho com as informações de vistoria
    elements.append(Paragraph(f"VISTORIA DE {vistoria_info['tipo_vistoria'].upper()}: {vistoria_info['nome_edificio']}", header_style))
    elements.append(Paragraph(f"APARTAMENTO {vistoria_info['numero_apartamento']}", subheader_style))
    elements.append(Paragraph(f"Vistoriador: {vistoria_info['nome_vistoriador']}", normal_style))
    elements.append(Paragraph(f"Locador: {vistoria_info['locador']}", normal_style))
    elements.append(Paragraph(f"Locatário: {vistoria_info['locatario']}", normal_style))
    
    data_inicio_formatada = datetime.strptime(vistoria_info['data_inicio'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y')
    elements.append(Paragraph(f"Data de Início: {data_inicio_formatada}", normal_style))
    elements.append(Paragraph(f"Endereço: {vistoria_info['endereco_imovel']}", normal_style))
    elements.append(Spacer(1, 12))

    # Estilo de observação em itálico
    observation_style = ParagraphStyle(
        'ObservationStyle',
        fontSize=10,
        fontName='Helvetica-Oblique',
        alignment=TA_LEFT,
        spaceAfter=8,
        textColor=colors.red
    )

    # Adiciona conteúdo para cada cômodo
    for room, descriptions in rooms.items():
        # Adicionando um contêiner para o cômodo
        elements.append(KeepTogether([
            Paragraph(room.upper(), header_style),
            Spacer(1, 12)
        ]))

        # Layout de grade para o conteúdo de cada cômodo
        for desc in descriptions:
            room_elements = []

            # Adiciona descrição e todas as imagens lado a lado
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], desc['image'])
            if os.path.exists(image_path) and os.path.isfile(image_path):
                room_elements.append([
                    Paragraph(desc['description'], normal_style),
                    Image(image_path, width=200, height=150)
                ])
            else:
                room_elements.append([
                    Paragraph(desc['description'], normal_style),
                    Paragraph(f"Imagem não encontrada: {desc['image']}", normal_style)
                ])

            # Adiciona a observação, se existir
            if 'observacao' in desc:
                room_elements.append([
                    Paragraph(f"Observação: {desc['observacao']}", observation_style),
                    Spacer(1, 12)
                ])

            # Tabela para organizar o layout como CSS Flexbox
            table = Table(room_elements, colWidths=[250, 200])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

    # Tabela de assinaturas no final
    assinatura_data = [
        ["__________________________", "__________________________"],
        ["ASS.", "ASS."],
        [f"{vistoria_info['locador']}", f"{vistoria_info['locatario']}"]
    ]
    assinatura_table = Table(assinatura_data, colWidths=[250, 250])
    assinatura_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0073e6')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12)
    ]))
    elements.append(Spacer(1, 24))
    elements.append(assinatura_table)

    # Salva o PDF no buffer
    doc.build(elements)
    buffer.seek(0)

    return buffer


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)