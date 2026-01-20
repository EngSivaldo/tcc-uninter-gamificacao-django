# Usamos a versão do Python que você já está utilizando nos testes
FROM python:3.13-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONUNBUFFERED = 1

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para o PostgreSQL e imagens
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto
COPY . /app/

# Expõe a porta que o Django usará
EXPOSE 8000