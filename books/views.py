from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings

from .models import DownloadStat
from .serializers import DownloadStatSerializer
from .utils import get_video_info, download_video, get_client_ip

from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta

# Import pour la géolocalisation d'IP (optionnel, voir explication ci-dessous)
# import requests # N'oubliez pas d'installer : pip install requests

# --- Fonction utilitaire pour récupérer l'IP du client (plus robuste) ---
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# --- API pour la collecte de données (Endpoint public) ---
class DownloadStatCreateAPIView(generics.CreateAPIView):
    """
    API publique qui reçoit une URL et tente de télécharger une vidéo.
    Elle enregistre toutes les stats associées.
    Cet endpoint est accessible publiquement (sans authentification).
    """
    queryset = DownloadStat.objects.all()
    serializer_class = DownloadStatSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        url = request.data.get('url')
        origine = request.data.get('origine_video', 'Inconnue')

        if not url:
            return Response({"error": "L'URL est requise."}, status=status.HTTP_400_BAD_REQUEST)

        # Collecte de l'environnement client
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')

        # Préparation des champs
        stat_data = {
            "url_telechargement": url,
            "adresse_ip": ip_address,
            "agent_utilisateur": user_agent,
            "referer": referer,
            "horodatage": timezone.now(),
            "origine_video": origine
        }

        try:
            # Analyse du lien (ex: via yt_dlp)
            info = get_video_info(url)

            # Simulation ou téléchargement réel
            output_path, file_size = download_video(info)

            stat_data.update({
                "statut_telechargement": True,
                "qualite_video": info.get('quality'),
                "duree_video": int(info.get('duration')),
                "taille_fichier": file_size,
            })

            # Enregistrement en BDD
            serializer = self.get_serializer(data=stat_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Réponse au client
            return Response({
                "message": "Téléchargement réussi.",
                "download_url": output_path
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # En cas d’erreur, on logue quand même la tentative
            stat_data.update({
                "statut_telechargement": False,
                "message_erreur": str(e)
            })

            serializer = self.get_serializer(data=stat_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({
                "error": "Échec du téléchargement.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- API pour l'authentification (pour le dashboard) ---
class CustomAuthToken(ObtainAuthToken):
    """
    API personnalisée pour obtenir un token d'authentification.
    Retourne le token et les informations de l'utilisateur, y compris s'il est admin.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_admin': user.is_staff # Ajout important : indique si l'utilisateur est un admin
        })


# --- API pour les statistiques (Endpoints protégés par authentification ADMIN) ---
class DownloadStatsOverviewAPIView(APIView):
    """
    API pour obtenir un aperçu des statistiques globales de téléchargement.
    Nécessite une authentification et que l'utilisateur soit un admin.
    """
    permission_classes = [permissions.IsAdminUser] # Changé de IsAuthenticated à IsAdminUser

    def get(self, request, *args, **kwargs):
        total_downloads = DownloadStat.objects.count()
        successful_downloads = DownloadStat.objects.filter(statut_telechargement=True).count()
        failed_downloads = total_downloads - successful_downloads
        
        today = timezone.localdate()
        downloads_today = DownloadStat.objects.filter(horodatage__date=today).count()
        successful_downloads_today = DownloadStat.objects.filter(horodatage__date=today, statut_telechargement=True).count()

        return Response({
            'total_downloads': total_downloads,
            'successful_downloads': successful_downloads,
            'failed_downloads': failed_downloads,
            'downloads_today': downloads_today,
            'successful_downloads_today': successful_downloads_today,
        })


class DownloadStatsTimeSeriesAPIView(APIView):
    """
    API pour obtenir des données de séries temporelles pour les graphiques en ligne.
    Nécessite une authentification et que l'utilisateur soit un admin.
    """
    permission_classes = [permissions.IsAdminUser] # Changé de IsAuthenticated à IsAdminUser

    def get(self, request, *args, **kwargs):
        period = request.query_params.get('period', 'day') # 'day', 'week', 'month'
        end_date_str = request.query_params.get('end_date')
        start_date_str = request.query_params.get('start_date')

        queryset = DownloadStat.objects.all()

        if end_date_str:
            try:
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(horodatage__date__lte=end_date)
            except ValueError:
                return Response({"detail": "Format de date de fin invalide. Utilisez %Y-%MM-%DD."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            end_date = timezone.localdate()

        if start_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(horodatage__date__gte=start_date)
            except ValueError:
                return Response({"detail": "Format de date de début invalide. Utilisez %Y-%MM-%DD."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if period == 'day':
                start_date = end_date - timedelta(days=30)
            elif period == 'week':
                start_date = end_date - timedelta(weeks=12)
            elif period == 'month':
                start_date = end_date - timedelta(days=365)
            queryset = queryset.filter(horodatage__date__gte=start_date)


        if period == 'day':
            truncated_date = TruncDay('horodatage')
        elif period == 'week':
            truncated_date = TruncWeek('horodatage')
        elif period == 'month':
            truncated_date = TruncMonth('horodatage')
        else:
            return Response({"detail": "Période invalide. Utilisez 'day', 'week' ou 'month'."},
                            status=status.HTTP_400_BAD_REQUEST)

        time_series_data = queryset.annotate(
            date=truncated_date
        ).values('date').annotate(
            total_downloads=Count('id'),
            successful_downloads=Count('id', filter=Q(statut_telechargement=True)),
            failed_downloads=Count('id', filter=Q(statut_telechargement=False))
        ).order_by('date')

        formatted_data = []
        for entry in time_series_data:
            formatted_date = entry['date'].strftime('%Y-%m-%d')
            formatted_data.append({
                'date': formatted_date,
                'total_downloads': entry['total_downloads'],
                'successful_downloads': entry['successful_downloads'],
                'failed_downloads': entry['failed_downloads'],
            })
        
        return Response(formatted_data)


class DownloadStatsByQualityAPIView(APIView):
    """
    API pour obtenir les statistiques de téléchargement par qualité de vidéo.
    Nécessite une authentification et que l'utilisateur soit un admin.
    """
    permission_classes = [permissions.IsAdminUser] # Changé de IsAuthenticated à IsAdminUser

    def get(self, request, *args, **kwargs):
        stats_by_quality = DownloadStat.objects.exclude(qualite_video__isnull=True).exclude(qualite_video__exact='').values('qualite_video').annotate(
            count=Count('id')
        ).order_by('-count')

        return Response(stats_by_quality)


class DownloadStatsByCountryAPIView(APIView):
    """
    API pour obtenir les statistiques de téléchargement par pays.
    Nécessite une authentification et que l'utilisateur soit un admin.
    """
    permission_classes = [permissions.IsAdminUser] # Changé de IsAuthenticated à IsAdminUser

    def get(self, request, *args, **kwargs):
        stats_by_country = DownloadStat.objects.exclude(pays_ip__isnull=True).exclude(pays_ip__exact='').values('pays_ip').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response(stats_by_country)

# @api_view(['POST'])
# def facebook_video_download(request):
#     video_url = request.data.get('video_url')
#     client_ip = request.META.get('REMOTE_ADDR')

#     if not video_url:
#         return Response({'error': 'Video URL is required'}, status=status.HTTP_400_BAD_REQUEST)

#     DownloadOperation.objects.create(video_url=video_url, ip_address=client_ip)

#     try:
#         with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
#             info = ydl.extract_info(video_url, download=False)
#             downloadable_url = info['url']
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     return Response({'downloadable_url': downloadable_url}, status=status.HTTP_200_OK)

# class DownloadOperationViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = DownloadOperation.objects.all().order_by('-timestamp')
#     serializer_class = DownloadOperationSerializer