FROM python:3.11-alpine
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
