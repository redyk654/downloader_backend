FROM python:3.10-slim

# Empêche Python de bufferiser la sortie
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système pour psycopg2 et autres
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd -u 1000 -m appuser

# Définir le répertoire de travail
WORKDIR /app

# Copier les requirements et installer avec optimisations
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Changer le propriétaire
RUN chown -R appuser:appuser /app

# Switch vers appuser
USER appuser

# Copier le code
COPY --chown=appuser:appuser . .

# Exposer le port
EXPOSE 8000

# Commande pour Gunicorn avec Uvicorn ASGI Worker
CMD ["gunicorn", "myproject.asgi:application", \
    "-k", "uvicorn.workers.UvicornWorker", \
    "--workers", "4", \
    "--bind", "0.0.0.0:8000", \
    "--timeout", "120", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]
