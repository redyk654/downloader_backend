FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Installer les dépendances système pour psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd -u 1000 -m appuser

# Définir le répertoire de travail
WORKDIR /app

# Copier requirements.txt et installer globalement (root)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Changer de propriétaire
RUN chown -R appuser:appuser /app

# Switch vers l’utilisateur non-root
USER appuser

# Exposer le port
EXPOSE 8000

# Commande par défaut pour Docker Compose
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
