FROM python:3.9.18-slim-bullseye

WORKDIR /app

# Installiere Build-Abhängigkeiten
RUN pip install chromadb

COPY chromadb.py .

RUN apt-get update \
    && apt-get install -y build-essential default-libmysqlclient-dev pkg-config

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "chromadb.py"]
