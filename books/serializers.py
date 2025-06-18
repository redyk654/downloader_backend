from rest_framework import serializers # type: ignore
from .models import Book, DownloadOperation, DownloadStat



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
        if not value.startswith("http") and not value.startswith("https"):
            raise serializers.ValidationError("L'URL de téléchargement doit commencer par http:// ou https://")
        return value