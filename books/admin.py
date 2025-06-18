# stats_api/admin.py

from django.contrib import admin
from .models import DownloadStat

@admin.register(DownloadStat)
class DownloadStatAdmin(admin.ModelAdmin):
    list_display = (
        'url_telechargement',
        'adresse_ip',
        'horodatage',
        'statut_telechargement',
        'qualite_video',
        'pays_ip',
    )
    list_filter = (
        'statut_telechargement',
        'horodatage',
        'qualite_video',
        'pays_ip',
    )
    search_fields = (
        'url_telechargement',
        'adresse_ip',
        'agent_utilisateur',
        'message_erreur',
    )
    readonly_fields = ('horodatage',) # Ne permet pas de modifier l'horodatage depuis l'admin