# Use uma imagem base do Python
FROM python:3.12.5

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos do Poetry
COPY pyproject.toml poetry.lock ./

# Instale o Poetry
RUN pip install poetry

# Instale as dependências do projeto
RUN poetry install --only main --no-interaction --no-ansi

# Copie o restante do código do projeto
COPY . .

# Expor a porta 5000
EXPOSE 5000

# Comando para executar a aplicação
CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000",  "--timeout", "0", "vistoria_back.main:app"]

