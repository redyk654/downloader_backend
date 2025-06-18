FROM python:3.9

ENV PYTHONUNBUFFERED 1

# Ajoutez ces lignes avant WORKDIR
RUN useradd -u 1000 -m appuser && \
    mkdir /app && \
    chown appuser:appuser /app

USER appuser

WORKDIR /app

COPY --chown=appuser:appuser requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=appuser:appuser . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]