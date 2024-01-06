FROM python:3.9.18-slim-bullseye

# Installiere Build-Abhängigkeiten
# RUN pip install chromadb

# COPY chroma_db.py .

RUN apt-get update \
    && apt-get install -y build-essential default-libmysqlclient-dev pkg-config

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "persona-persistence.py"]
