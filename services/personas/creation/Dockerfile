FROM python:3.9.18-slim-bullseye

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Flask wird auf Port 8080 laufen, also sollten wir diesen Port im Docker-Container freigeben
EXPOSE 8080

ENV FLASK_APP persona_creation.py

# Starten Sie die Flask-App auf Port 8080
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
