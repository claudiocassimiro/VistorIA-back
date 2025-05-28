# VistorIA - Backend

**EN** | **PT-BR** (versão em português logo abaixo)

## Overview

**VistorIA** is the backend of a computer vision agent built with Python and Flask, integrating OpenAI's Vision API.  
This project aims to support the analysis and processing of images to extract intelligent insights through AI.

## Features

- 🔍 Computer Vision agent using OpenAI's Vision API
- 🧠 Intelligent image analysis with Python
- 🌐 RESTful API built with Flask
- ♻️ CORS enabled for cross-origin requests
- 📄 PDF report generation with ReportLab
- 🔒 Environment variable support via `python-dotenv`
- ⚙️ Production-ready with Gunicorn

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-username/vistoria-back.git
cd vistoria-back
````

2. **Install dependencies**

Make sure you have [Poetry](https://python-poetry.org/) and Python 3.12 installed.

```bash
poetry install
```

3. **Configure environment**

Create a `.env` file based on `.env.example` (if provided), and set your OpenAI API key and any other required environment variables.

```env
OPENAI_API_KEY=your-api-key-here
```

4. **Run the application (development)**

```bash
poetry run flask run
```

5. **Run in production with Gunicorn**

```bash
poetry run gunicorn -b 0.0.0.0:8000 app:app
```

## Project Structure

```
vistoria-back/
├── app.py
├── .env
├── requirements.txt
├── README.md
└── ...
```

## License

This project is developed by **Claudio Cassimiro** and maintained under the [Jala University](https://jala.university) initiative.

---

# VistorIA - Backend

## Visão Geral

**VistorIA** é o backend de um agente de visão computacional desenvolvido com Python e Flask, utilizando a API de Visão da OpenAI.
O objetivo deste projeto é permitir a análise e o processamento inteligente de imagens com suporte da inteligência artificial.

## Funcionalidades

* 🔍 Agente de Visão Computacional com a API de Visão da OpenAI
* 🧠 Análise inteligente de imagens com Python
* 🌐 API RESTful com Flask
* ♻️ Suporte a CORS para requisições cross-origin
* 📄 Geração de relatórios PDF com ReportLab
* 🔒 Suporte a variáveis de ambiente com `python-dotenv`
* ⚙️ Pronto para produção com Gunicorn

## Instalação

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/vistoria-back.git
cd vistoria-back
```

2. **Instale as dependências**

Certifique-se de ter o [Poetry](https://python-poetry.org/) e Python 3.12 instalados.

```bash
poetry install
```

3. **Configure o ambiente**

Crie um arquivo `.env` com sua chave da API da OpenAI e outras variáveis necessárias.

```env
OPENAI_API_KEY=sua-chave-aqui
```

4. **Execute o aplicativo (modo desenvolvimento)**

```bash
poetry run flask run
```

5. **Execute em produção com Gunicorn**

```bash
poetry run gunicorn -b 0.0.0.0:8000 app:app
```

## Estrutura do Projeto

```
vistoria-back/
├── app.py
├── .env
├── requirements.txt
├── README.md
└── ...
```

## Licença

Este projeto é desenvolvido por **Claudio Cassimiro** e mantido sob a iniciativa da [Jala University](https://jala.university).

```

---

Se quiser incluir imagens, exemplos de endpoints ou de payloads/respostas JSON, posso complementar o README com isso também. Deseja?
