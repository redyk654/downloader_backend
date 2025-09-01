from rest_framework import serializers # type: ignore
from .models import Book, DownloadOperation, DownloadStat
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urllib.parse import urlparse



class DownloadOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadOperation
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class DownloadStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadStat
        fields = '__all__' # Inclut tous les champs du modèle
        extra_kwargs = {
            'adresse_ip': {'required': False},  # ✅ Rendu non requis
            'agent_utilisateur': {'required': False},
            'horodatage': {'required': False},
            # ajoute d'autres champs si tu les remplis côté serveur
        }

    # On peut ajouter des logiques de validation ou de traitement ici si nécessaire.
    # Par exemple, une validation pour l'URL ou l'IP.
    def validate_url_telechargement(self, value):
        validator = URLValidator()
        try:
            validator(value)
        except ValidationError:
            raise serializers.ValidationError("URL invalide")
        
        allowed_domains = ['chris-you.com', 'rimeo.chris-you.com']
        domain = urlparse(value).netloc
        if domain not in allowed_domains:
            raise serializers.ValidationError("Domaine non autorisé")
        
        return value

    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) # Aucune contrainte sur le mot de passe

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_password(self, value):
        # Pas de validation personnalisée
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user