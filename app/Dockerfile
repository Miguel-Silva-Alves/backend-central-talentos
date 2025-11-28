FROM python:3.11-slim

WORKDIR /usr/src/app

# Dependências do sistema (mais enxutas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Melhorar pip
RUN pip install --upgrade pip

# Copiar requirements antes — MELHORA O CACHE
COPY requirements.txt .

# Instalar deps Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar modelo spaCy sem perder cache
COPY pt_core_news_sm-3.6.0.tar.gz .
RUN pip install --no-cache-dir pt_core_news_sm-3.6.0.tar.gz

# Entrypoint
COPY entrypoint.sh .
RUN sed -i 's/\r$//g' entrypoint.sh && chmod +x entrypoint.sh

# Copiar o restante do projeto
COPY . .

ENTRYPOINT ["./entrypoint.sh"]
