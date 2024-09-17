# Use uma imagem base do Python
FROM python:3.12.5

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos do projeto para o container
COPY pyproject.toml poetry.lock ./

# Instalar o Poetry
RUN pip install poetry

# Instalar as dependências do projeto sem os pacotes de desenvolvimento
RUN poetry install --no-dev --no-interaction --no-ansi

# Copiar o restante do código do projeto
COPY . .

# Expor a porta 5000
EXPOSE 5000

# Comando para executar a aplicação
CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
