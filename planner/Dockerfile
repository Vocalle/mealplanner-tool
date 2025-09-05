FROM python:3.12-slim

WORKDIR /app

# requirements.txt aus planner/ kopieren
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# restliche Dateien ins Image
COPY . .

EXPOSE 5000

CMD ["python3", "/app/run.py"]
