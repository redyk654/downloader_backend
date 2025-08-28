FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Installer les dépendances système pour psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root avec le même UID que votre user deployer
RUN useradd -u 1000 -m appuser

# Définir le répertoire de travail
WORKDIR /app

# Copier requirements.txt et installer globalement (root)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Changer le propriétaire du WORKDIR AVANT de copier les fichiers
RUN chown -R appuser:appuser /app

# Switch vers l'utilisateur non-root AVANT de copier le code
USER appuser

# Copier le code avec les bonnes permissions
COPY --chown=appuser:appuser . .

# Exposer le port
EXPOSE 8000

# Commande par défaut pour Docker Compose
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]