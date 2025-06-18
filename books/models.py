from django.db import models # type: ignore
from django.utils import timezone

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    published_year = models.IntegerField()

    def __str__(self):
        return self.title

class DownloadOperation(models.Model):
    video_url = models.URLField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ip_address} - {self.video_url[:50]}... at {self.timestamp}"
    
class DownloadStat(models.Model):
    """
    Modèle pour stocker les statistiques de téléchargement de vidéos Facebook.
    """
    url_telechargement = models.URLField(
        max_length=500,
        verbose_name="URL de Téléchargement",
        help_text="L'URL de la vidéo Facebook téléchargée."
    )
    adresse_ip = models.GenericIPAddressField(
        verbose_name="Adresse IP",
        help_text="L'adresse IP de l'utilisateur qui a initié le téléchargement."
    )
    horodatage = models.DateTimeField(
        default=timezone.now,
        verbose_name="Horodatage",
        help_text="Date et heure du téléchargement."
    )
    statut_telechargement = models.BooleanField(
        default=False,
        verbose_name="Statut du Téléchargement",
        help_text="Indique si le téléchargement a réussi (True) ou échoué (False)."
    )
    message_erreur = models.TextField(
        blank=True,
        null=True,
        verbose_name="Message d'Erreur",
        help_text="Description de l'erreur en cas d'échec du téléchargement."
    )
    agent_utilisateur = models.TextField(
        blank=True,
        verbose_name="Agent Utilisateur",
        help_text="Chaîne User-Agent du navigateur de l'utilisateur."
    )
    referer = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Référent",
        help_text="L'URL de la page référente."
    )
    duree_video = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Durée de la Vidéo (secondes)",
        help_text="La durée de la vidéo téléchargée en secondes."
    )
    qualite_video = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Qualité Vidéo",
        help_text="La qualité de la vidéo téléchargée (ex: 720p, 1080p)."
    )
    taille_fichier = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name="Taille du Fichier (octets)",
        help_text="La taille du fichier téléchargé en octets."
    )
    pays_ip = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Pays de l'IP",
        help_text="Le pays d'origine de l'adresse IP (nécessite une géolocalisation)."
    )

    class Meta:
        verbose_name = "Statistique de Téléchargement"
        verbose_name_plural = "Statistiques de Téléchargement"
        ordering = ['-horodatage'] # Trie par l'horodatage le plus récent par défaut

    def __str__(self):
        return f"Téléchargement de {self.url_telechargement[:50]} par {self.adresse_ip} le {self.horodatage.strftime('%Y-%m-%d %H:%M')}"
