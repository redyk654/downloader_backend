from celery import shared_task
from .utils import get_available_resolutions, extract_video_metadata, build_yt_dlp_format
from .models import DownloadStat
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def async_get_available_resolutions(video_url):
    """Tâche pour récupérer les résolutions de manière asynchrone"""
    try:
        return get_available_resolutions(video_url)
    except Exception as e:
        logger.error(f"Erreur dans async_get_available_resolutions: {str(e)}")
        raise

@shared_task
def async_extract_metadata_and_save(request_data, client_ip, user_agent, referer):
    """Tâche pour extraire les métadonnées et sauvegarder les stats"""
    
    video_url = request_data.get('video_url')
    origine = request_data.get('origine_video')
    format_preference = request_data.get('format_preference', 'worst')
    yt_dlp_format = build_yt_dlp_format(format_preference)
    
    try:
        metadata = extract_video_metadata(video_url, yt_dlp_format)
        
        DownloadStat.objects.create(
            url_telechargement=video_url,
            adresse_ip=client_ip,
            horodatage=timezone.now(),
            statut_telechargement=True,
            agent_utilisateur=user_agent,
            referer=referer,
            duree_video=metadata.get('duration'),
            qualite_video=metadata.get('format'),
            taille_fichier=metadata.get('filesize'),
            origine_video=origine,
            direct_url=metadata.get('direct_url')
        )
        
        return {
            "download_url": metadata.get('direct_url'),
            "format": metadata.get('format')
        }
    except Exception as e:
        DownloadStat.objects.create(
            url_telechargement=video_url,
            adresse_ip=client_ip,
            horodatage=timezone.now(),
            statut_telechargement=False,
            agent_utilisateur=user_agent,
            referer=referer,
            message_erreur=str(e),
            origine_video=origine,
        )
        logger.error(f"Erreur dans async_extract_metadata_and_save: {str(e)}")
        raise