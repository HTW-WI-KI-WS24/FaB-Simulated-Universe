FROM python:3.9.18-slim-bullseye

WORKDIR /app

COPY .. /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP persona-creation.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
