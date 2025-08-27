FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Ajoutez ces lignes avant WORKDIR
RUN useradd -u 1000 -m appuser && \
    mkdir /app && \
    chown appuser:appuser /app

USER appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]