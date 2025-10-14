# Pull official base image
FROM python:3.9.6-slim

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    clang \
    netcat \
    && rm -rf /var/lib/apt/lists/*


# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements.txt
COPY ./requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Copy project files
COPY . .

# Run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
