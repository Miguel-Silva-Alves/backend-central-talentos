FROM python:3.11-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    clang \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

# ✅ COPY do modelo spaCy .tar.gz
COPY ./pt_core_news_sm-3.6.0.tar.gz /usr/src/app/

# ✅ Instalar o modelo manualmente
RUN pip install pt_core_news_sm-3.6.0.tar.gz

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . .


# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
