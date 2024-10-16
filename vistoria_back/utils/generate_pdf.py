from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
import os
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether

def generate_styled_pdf(rooms, vistoria_info, app):
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

    # Estilo de observação em itálico
    observation_style = ParagraphStyle(
        'ObservationStyle',
        fontSize=10,
        fontName='Helvetica-Oblique',
        alignment=TA_LEFT,
        spaceAfter=8,
        textColor=colors.red
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

    # Adiciona observações gerais, se existirem
    if vistoria_info.get('observacoes_gerais') and vistoria_info['observacoes_gerais'] != '':
        elements.append(Paragraph("Observações Gerais:", subheader_style))
        elements.append(Paragraph(vistoria_info['observacoes_gerais'], normal_style))
        elements.append(Spacer(1, 12))
    
    # Imprime as observações gerais para depuração
    print("Observações Gerais:", vistoria_info.get('observacoes_gerais'))

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