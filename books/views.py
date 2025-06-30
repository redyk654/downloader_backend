from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from .models import DownloadStat
from .serializers import DownloadStatSerializer, RegisterSerializer
from .utils import get_client_ip
from books.tasks import async_get_available_resolutions, async_extract_metadata_and_save

from django.db.models import Count, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from celery.result import AsyncResult

# Import pour la géolocalisation d'IP (optionnel, voir explication ci-dessous)

@permission_classes([permissions.AllowAny])
@api_view(['POST'])
def get_formats_video(request):
    """
    API publique pour récupérer les résolutions (asynchrone)
    Retourne un task_id immédiatement
    """
    video_url = request.data.get('video_url')

    if not video_url:
        return Response(
            {"error": "Le paramètre 'video_url' est requis."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Lancement de la tâche asynchrone
    task = async_get_available_resolutions.delay(video_url)
    
    return Response(
        {"task_id": task.id},
        status=status.HTTP_202_ACCEPTED
    )


class DownloadStatCreateAPIView(generics.CreateAPIView):
    """
    Endpoint asynchrone pour le téléchargement
    """
    serializer_class = DownloadStatSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        video_url = request.data.get('video_url')
        origine = request.data.get('origine_video')
        format_preference = request.data.get('format_preference', 'best')

        if not video_url or not origine:
            return Response(
                {"error": "Les champs 'video_url' et 'origine_video' sont requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Lancement de la tâche asynchrone
        task = async_extract_metadata_and_save.delay(
            request_data=request.data,
            client_ip=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referer=request.META.get('HTTP_REFERER', '')
        )
        
        return Response(
            {"task_id": task.id},
            status=status.HTTP_202_ACCEPTED
        )


class TaskStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        
        response_data = {
            "task_id": task_id,
            "status": task_result.status,
        }
        
        if task_result.status == "SUCCESS":
            response_data["result"] = task_result.result
        elif task_result.status == "FAILURE":
            response_data["error"] = str(task_result.result)
        
        return Response(response_data, status=status.HTTP_200_OK)


# --- API pour l'authentification ---
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

# --- API pour l'enregistrement d'un nouvel utilisateur ---
class RegisterAPIView(APIView):
    """
    API publique pour créer un nouvel utilisateur.
    Retourne un token immédiatement après enregistrement.
    """
    permission_classes = []  # Public

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_staff
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

