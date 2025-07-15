from django.urls import path
from .views import (
    DownloadStatCreateAPIView,
    DownloadStatsOverviewAPIView,
    DownloadStatsTimeSeriesAPIView,
    DownloadStatsByQualityAPIView,
    DownloadStatsByCountryAPIView,
    RegisterAPIView,
    TaskStatusView,
    get_formats_video
)

urlpatterns = [
    # Endpoint pour l'enregistrement d'un nouvel utilisateur (public)
    path('auth-register/', RegisterAPIView.as_view(), name='register'),

    # Endpoint pour enregistrer un téléchargement (public)
    path('downloads/record/', DownloadStatCreateAPIView.as_view(), name='record_download'),

    # Endpoint pour les obtenir les formats disponibles (public)
    path('downloads/formats/', get_formats_video, name='get_formats_videos'),

    # Endpoint pour vérifier le statut d'une tâche (public)
    path('downloads/task-status/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),

    # Endpoints pour les statistiques (protégés par authentification)
    path('stats/overview/', DownloadStatsOverviewAPIView.as_view(), name='stats_overview'),
    path('stats/timeseries/', DownloadStatsTimeSeriesAPIView.as_view(), name='stats_timeseries'),
    path('stats/by-quality/', DownloadStatsByQualityAPIView.as_view(), name='stats_by_quality'),
    path('stats/by-country/', DownloadStatsByCountryAPIView.as_view(), name='stats_by_country'),
]