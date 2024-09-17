import os
import requests
from dotenv import load_dotenv
from base64 import b64encode

# Carrega as variáveis de ambiente
load_dotenv()

# Obtém a chave da API da OpenAI do ambiente
api_key = os.getenv("OPENAI_API_KEY")

# URL da API de visão da OpenAI
url = "https://api.openai.com/v1/chat/completions"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return b64encode(image_file.read()).decode('utf-8')

def process_images(upload_folder):
    results = []
    
    for filename in os.listdir(upload_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(upload_folder, filename)
            base64_image = encode_image(image_path)
            
            # Prepara os headers e o payload
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analise a imagem. Ela faz parte de uma vistoria de apartamento. Sua missão é descrever o que a imagem tá mostrando, focando nos principais detalhes e comentando problemas visíveis. Seja sucinto e direto na descrição. Descrevendo o móvel ou parte da casa que está na imagem. Seja objetivo e direto na descrição. Uma única frase. Não comece com 'A imagem mostra' ou 'A imagem contém'. Apenas a frase."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            }
            
            # Envia a requisição para a API
            response = requests.post(url, headers=headers, json=payload)
            
            # Verifica se a requisição foi bem-sucedida
            if response.status_code == 200:
                response_json = response.json()
                if 'choices' in response_json and len(response_json['choices']) > 0:
                    description = response_json['choices'][0]['message']['content']
                else:
                    description = "Erro: Resposta da API não contém a estrutura esperada."
            else:
                description = f"Erro na API: {response.status_code} - {response.text}"
            
            # Extrai o nome do cômodo do nome do arquivo (assumindo que o nome do arquivo começa com o nome do cômodo)
            room = filename.split('_')[0]
            
            results.append({
                "image": filename,
                "description": description,
                "room": room
            })
    
    return results
