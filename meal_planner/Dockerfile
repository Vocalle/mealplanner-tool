FROM python:3.11-slim

WORKDIR /app

# requirements.txt ins Image kopieren
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Den ganzen Code inkl. meal_planner/ ins Image
COPY . .

EXPOSE 5000

# **Korrekt!** run.py liegt in /app/meal_planner/run.py
CMD ["streamlit", "run", "/app/meal_planner/run.py", "--server.port=5000", "--server.address=0.0.0.0"]
